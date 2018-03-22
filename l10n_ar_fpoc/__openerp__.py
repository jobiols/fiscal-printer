# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Moldeo interactive
#                  2017 jeo Software  (http://www.jeosoft.com.ar)
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
    'demo_xml': [],
    'depends': ['account',
                'fpoc',
                'l10n_ar_invoice',
                'l10n_ar_afipws_fe',
                'ticket_citi_fix',
                'partner_fiscal_constraints',
                'account_multi_store',
                ],
    'name': 'Localization for FPoc',
    'init_xml': [],
    'license': 'AGPL-3',
    'test': [],
    'data': [
        'view/ra_fpoc_view.xml',
        'view/journal_view.xml',
        'view/invoice_workflow.xml',
        'view/invoice_view.xml',
        'view/afip_point_of_sale_view.xml'
    ],
    'post_load': '',
    'js': [],
    'css': [],
    'qweb': [],
    'version': '8.0.2.0.0',
    'website': '',
    'installable': True,
    'active': False,
}
