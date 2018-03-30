# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################

from openerp.osv import osv, fields
from openerp.tools.translate import _

from ..controllers.main import do_event
from datetime import datetime

from openerp.addons.fpoc.controllers.main import DenialService

import logging

_logger = logging.getLogger(__name__)


# _logger.setLevel(logging.DEBUG)


class FiscalPrinter(osv.osv):
    """
    The fiscal printer entity.
    """

    def _get_status(self, cr, uid, ids, field_name, arg, context=None):
        s = self.get_state(cr, uid, ids, context)

        r = {}
        for p_id in ids:
            if s[p_id]:
                if s[p_id].has_key('clock'):
                    dt = datetime.strptime(s[p_id]['clock'], "%Y-%m-%d %H:%M:%S")
                    clock_now = dt.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    clock_now = str(datetime.datetime.now())
                r[p_id] = {
                    # 'clock': dt.strftime("%Y-%m-%d %H:%M:%S"),
                    'clock': clock_now,
                    'printerStatus': s[p_id].get('strPrinterStatus', 'Unknown'),
                    'fiscalStatus': s[p_id].get('strFiscalStatus', 'Unknown'),
                }
            else:
                r[p_id] = {
                    'clock': False,
                    'printerStatus': 'Offline',
                    'fiscalStatus': 'Offline',
                }
        return r

    _name = 'fpoc.fiscal_printer'
    _description = 'Connected fiscal printers'

    _columns = {
        'name': fields.char(string='Name', required=True),
        'protocol': fields.char(string='Protocol'),
        'model': fields.char(string='Model'),
        'serialNumber': fields.char(string='Serial Number (S/N)'),
        'lastUpdate': fields.datetime(string='Last Update'),
        'printerStatus': fields.function(_get_status, type="char", method=True,
                                         readonly="True", multi="state",
                                         string='Printer status'),
        'fiscalStatus': fields.function(_get_status, type="char", method=True,
                                        readonly="True", multi="state",
                                        string='Fiscal status'),
        'clock': fields.function(_get_status, type="datetime", method=True,
                                 readonly="True", multi="state",
                                 string='Clock'),
        'session_id': fields.char(string='session_id'),
    }

    _sql_constraints = [
        ('model_serialNumber_unique',
         'unique("model", "serialNumber")',
         'this printer with this model and serial number already exists')
    ]

    def short_test(self, cr, uid, ids, context=None):
        for fp in self.browse(cr, uid, ids):
            do_event('short_test', {'name': fp.name},
                     session_id=fp.session_id, printer_id=fp.name)
        return True

    def large_test(self, cr, uid, ids, context=None):
        for fp in self.browse(cr, uid, ids):
            do_event('large_test', {'name': fp.name},
                     session_id=fp.session_id, printer_id=fp.name)
        return True

    def advance_paper(self, cr, uid, ids, context=None):
        for fp in self.browse(cr, uid, ids):
            do_event('advance_paper', {'name': fp.name},
                     session_id=fp.session_id, printer_id=fp.name)
        return True

    def cut_paper(self, cr, uid, ids, context=None):
        for fp in self.browse(cr, uid, ids):
            do_event('cut_paper', {'name': fp.name},
                     session_id=fp.session_id, printer_id=fp.name)
        return True

    def open_fiscal_journal(self, cr, uid, ids, context=None):
        for fp in self.browse(cr, uid, ids):
            do_event('open_fiscal_journal', {'name': fp.name},
                     session_id=fp.session_id, printer_id=fp.name)
        return True

    def cancel_fiscal_ticket(self, cr, uid, ids, context=None):
        for fp in self.browse(cr, uid, ids):
            do_event('cancel_fiscal_ticket', {'name': fp.name},
                     session_id=fp.session_id, printer_id=fp.name)
        return True

    def close_fiscal_journal(self, cr, uid, ids, context=None):
        for fp in self.browse(cr, uid, ids):
            do_event('close_fiscal_journal', {'name': fp.name},
                     session_id=fp.session_id, printer_id=fp.name)
        return True

    def shift_change(self, cr, uid, ids, context=None):
        for fp in self.browse(cr, uid, ids):
            do_event('shift_change', {'name': fp.name},
                     session_id=fp.session_id, printer_id=fp.name)
        return True

    def get_state(self, cr, uid, ids, context=None):
        r = {}
        for fp in self.browse(cr, uid, ids):
            try:
                event_result = do_event('get_status', {'name': fp.name},
                                        session_id=fp.session_id,
                                        printer_id=fp.name)
            except DenialService as m:
                raise osv.except_osv(_('Connectivity Error'), m)
            r[fp.id] = event_result.pop() if event_result else False
        return r

    def get_counters(self, cr, uid, ids, context=None):
        r = {}
        for fp in self.browse(cr, uid, ids):
            event_result = do_event('get_counters', {'name': fp.name},
                                    session_id=fp.session_id,
                                    printer_id=fp.name)
            r[fp.id] = event_result.pop() if event_result else False
        return r

    def make_fiscal_ticket(self, cr, uid, ids, options={}, ticket={},
                           context=None):
        fparms = {}
        r = {}
        for fp in self.browse(cr, uid, ids):
            fparms['name'] = fp.name
            fparms['options'] = options
            fparms['ticket'] = ticket
            # event_result = do_event('make_fiscal_ticket', fparms,
            event_result = do_event('make_ticket_factura', fparms,
                                    session_id=fp.session_id,
                                    printer_id=fp.name)
            r[fp.id] = event_result.pop() if event_result else False
        return r

    def make_fiscal_refund_ticket(self, cr, uid, ids, options={}, ticket={},
                                  context=None):
        fparms = {}
        r = {}
        for fp in self.browse(cr, uid, ids):
            fparms['name'] = fp.name
            fparms['options'] = options
            fparms['ticket'] = ticket
            # import pdb;pdb.set_trace()
            # event_result = do_event('make_fiscal_ticket', fparms,
            event_result = do_event('make_ticket_notacredito', fparms,
                                    session_id=fp.session_id,
                                    printer_id=fp.name)
            r[fp.id] = event_result.pop() if event_result else False
        return r

    def cancel_fiscal_ticket(self, cr, uid, ids, context=None):
        fparms = {}
        r = {}
        for fp in self.browse(cr, uid, ids):
            fparms['name'] = fp.name
            event_result = do_event('cancel_fiscal_ticket', fparms,
                                    session_id=fp.session_id,
                                    printer_id=fp.name)
            r[fp.id] = event_result.pop() if event_result else False
        return r

