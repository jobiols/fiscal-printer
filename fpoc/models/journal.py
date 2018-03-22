# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import tools, models, fields, api, _


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    fp_serial_number = fields.Char(
            'Nro de serie'
    )
