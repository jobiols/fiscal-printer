# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017  jeo Software  (http://www.jeosoft.com.ar)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'author': 'Moldeo Interactive, jeo Software',
    'category': 'base.module_category_hidden',
    'depends': [
        'account',
        'l10n_ar_invoice',
    ],
    'description': 'Fiscal Printer on the Cloud',
    'license': 'AGPL-3',
    'name': 'Fiscal Printer on the Cloud',
    'test': [
        'test/check_spools.yml',
    ],
    'data': [
        'view/fiscal_printer_view.xml',
        'security/fiscal_printer_group.xml',
        'security/ir.model.access.csv',
        'view/fpoc_menuitem.xml',
    ],
    'version': '8.0.1.0',
    'website': 'https://github.com/csrocha/odoo_fpoc',
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
