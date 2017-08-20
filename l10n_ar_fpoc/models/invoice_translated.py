# -*- coding: utf-8 -*-


from openerp import fields, models, api, _


import logging


_logger = logging.getLogger(__name__)


class AccountInvoice():
    _inherit = "account.invoice"

    @api.one
    def get_validation_type(self):

        # for compatibility with account_invoice_operation, if module installed
        # and there are operations we return no_validation so no validate
        # button is displayed
        if self._fields.get('operation_ids') and self.operation_ids:
            self.validation_type = 'no_validation'
        # if invoice has cae then me dont validate it against afip
        elif self.journal_id.point_of_sale_id.afip_ws and not self.afip_auth_code:
            self.validation_type = self.env[
                'res.company']._get_environment_type()
