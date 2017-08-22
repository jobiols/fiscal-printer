# -*- coding: utf-8 -*-
{
    'active': False,
    'author': 'Moldeo Interactive, jeo Software',
    'category': 'base.module_category_hidden',
    'demo_xml': [],
    'depends': ['account',
                'fpoc',
                'l10n_ar_invoice',
                'l10n_ar_afipws_fe',
                'ticket_citi_fix',
                'base_vat_dni'
                ],
    'name': 'Fiscal Printer on the Cloud support for Argentina Localization',
    'description': '___',
    'init_xml': [],
    'installable': True,
    'license': 'AGPL-3',
    'test': [ ],
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
    'version': '0.1',
    'website': ''
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
