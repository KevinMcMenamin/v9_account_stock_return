# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013- Solnet Solutions (<http://www.solnetsolutions.co.nz>).
#    Copyright (C) 2010 OpenERP S.A. http://www.openerp.com
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Partner Returns Invoicing",
    "version": "1.0",
    "depends": ["base", "account", "stock", "account_anglo_saxon"],
    "author": "Solnet Solutions Ltd",
    "website": "http://www.solnetsolutions.co.nz",
    "category": "Accounting",
    "description": ("Allows a partner credit note to be referenced back to the originating return picking"),
    "data": ["account_invoice.xml"
             ],
    "update_xml": [],
    "demo": [],
    "test": [],
    "installable": True,
    "active": False
}
