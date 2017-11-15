# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################

from openerp import tools, models, fields, api, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    nro_ticket_impreso = fields.Char(
            'Nro ticket impreso'
    )
