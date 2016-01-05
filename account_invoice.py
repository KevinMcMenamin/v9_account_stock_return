from openerp import api, fields, models
from openerp.tools.float_utils import float_compare


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    picking_id = fields.Many2one(comodel_name='stock.picking', string='Create a Stock Credit',
                                 help='When selected, the associated return picking move lines are added to the partner invoice.')

    @api.onchange('partner_id')
    def _onchange_allowed_return_ids(self):
        '''
        The purpose of the method is to define a domain for the available
        return pickings.
        '''
        result = {}
        if self.partner_id:
            relevant_ids = self.search([('partner_id', '=', self.partner_id.id), ('picking_id', '!=', False)])
            picking_ids = [x.picking_id.id for x in relevant_ids]
        else:
            picking_ids = []

        if self.type in ('in_invoice', 'in_refund'):
            result['domain'] = {'picking_id': [
                ('location_dest_id.usage', '=', 'supplier'),
                ('partner_id', 'child_of', self.partner_id.id),
                ('id', 'not in', picking_ids), ]}
        else:
            result['domain'] = {'picking_id': [
                ('location_id.usage', '=', 'customer'),
                ('partner_id', 'child_of', self.partner_id.id),
                ('id', 'not in', picking_ids), ]}
        return result

    @api.onchange('picking_id')
    def picking_id_change(self):
        result = []
        if not self.picking_id:
            return {}
        if not self.partner_id and self.picking_id.partner_id:
            self.partner_id = self.picking_id.partner_id
        if not self.partner_id:
            return {}

        for line in self.picking_id.move_lines:
            if line in self.invoice_line_ids.mapped('stock_move_id'):
                continue
            qty = 0 - line.product_uom_qty
            if self.type in ('in_invoice', 'in_refund'):
                taxes = line.product_id.supplier_taxes_id
                invoice_line_tax_ids = self.partner_id.property_account_position_id.map_tax(taxes)
                data = {
                    'purchase_line_id': False,
                    'name': line.name,
                    'origin': self.origin,
                    'uom_id': line.product_uom.id,
                    'product_id': line.product_id.id,
                    'account_id': self.env['account.invoice.line'].with_context({'journal_id': self.journal_id.id, 'type': 'in_invoice'})._default_account(),
                    'price_unit': line.price_unit,
                    'quantity': qty,
                    'discount': 0.0,
                    'invoice_line_tax_ids': invoice_line_tax_ids.ids,
                    'type': 'normal',
                    'stock_move_id': line.id,
                }
                account = self.env['account.invoice.line'].get_invoice_line_account('in_invoice', line.product_id, self.partner_id.property_account_position_id, self.env.user.company_id)
                if account:
                    data['account_id'] = account.id
                    result.append(data)

            else:
                taxes = line.product_id.taxes_id
                invoice_line_tax_ids = self.partner_id.property_account_position_id.map_tax(taxes)
                data = {
                    'sale_line_id': False,
                    'name': line.name,
                    'origin': self.origin,
                    'uom_id': line.product_uom.id,
                    'product_id': line.product_id.id,
                    'account_id': self.env['account.invoice.line'].with_context({'journal_id': self.journal_id.id, 'type': 'out_refund'})._default_account(),
                    'price_unit': line.procurement_id.sale_line_id.price_subtotal / line.procurement_id.sale_line_id.product_uom_qty,  # will be nett of discount
                    'cost_price': line.price_unit,
                    'quantity': qty,
                    'discount': 0.0,
                    'invoice_line_tax_ids': invoice_line_tax_ids.ids,
                    'type': 'normal',
                    'stock_move_id': line.id,
                }
                account = self.env['account.invoice.line'].get_invoice_line_account('out_refund', line.product_id, self.partner_id.property_account_position_id, self.env.user.company_id)
                if account:
                    data['account_id'] = account.id
                    result.append(data)

        self.invoice_line_ids = result
        return {}

    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        self.write({'picking_id': self.picking_id.id})
        for line in self.invoice_line_ids:
            self.env['account.invoice.line'].write({'cost_price': line.cost_price,
                                                    'stock_move_id': line.stock_move_id})
