# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################

import openerp.addons.web.http as oeweb
import json
import threading
from openerp.osv import osv
from openerp.tools.translate import _
from urlparse import parse_qs

from Queue import Queue, Empty
import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

# jinegconpkicmfefahjgkpinkgoabnme
# access_control_allow_origin = 'chrome-extension://gileacnnoefamnjnhjnijommagpamona'
access_control_allow_origin = 'chrome-extension://jinegconpkicmfefahjgkpinkgoabnme'
event_id = 0
event_event = {}
event_result = {}
event_hub = {}
result_hub = {}
thread_hub = {}
response_hub = {}
to_remove = {}
timeout = 5

# Monkey path for HttpRequest
http_old_dispatch = oeweb.HttpRequest.dispatch


def http_dispatch(self):
    r = http_old_dispatch(self)
    if hasattr(r, 'headers'):
        r.headers._list.append(
            ('Access-Control-Allow-Origin', access_control_allow_origin))
        r.headers._list.append(('Access-Control-Allow-Credentials', 'true'))
    return r


oeweb.HttpRequest.dispatch = http_dispatch

# Monkey path for JsonRequest
json_old_dispatch = oeweb.JsonRequest.dispatch


def json_dispatch(self):
    r = json_old_dispatch(self)
    if hasattr(r, 'headers'):
        r.headers._list.append(
            ('Access-Control-Allow-Origin', access_control_allow_origin))
        r.headers._list.append(('Access-Control-Allow-Credentials', 'true'))
    return r


oeweb.JsonRequest.dispatch = json_dispatch

# Monkey path to capture connection_dropped
from werkzeug.serving import WSGIRequestHandler

wsgi_old_connection_dropped = WSGIRequestHandler.connection_dropped


def connection_dropped(self, error, environ=None):
    """ Called if the connection was closed by the client.  By default
        nothing happens.
    """
    print '//// connection dropped / error=', error
    path = environ.get('PATH_INFO', None)
    if path and path == '/fp/spool':
        q = parse_qs('&'.join([environ.get('QUERY_STRING', ''),
                               environ.get('HTTP_COOKIE', '')]))
        sid = q.get('session_id', [''])[0]
        pid = q.get('printer_id', [''])[0]
        qid = "%s:%s" % (sid, pid)
        if qid in event_hub:
            del event_hub[qid]
            _logger.debug(
                u"Removing spools %s by %s" % (qid, str(error).decode('utf8')))
        else:
            _logger.warning(
                u"Removing spools %s by %s, but it not was stored." % (
                    qid, str(error).decode('utf8')))


WSGIRequestHandler.connection_dropped = connection_dropped


class DenialService(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


# Event manager
def do_event(event, data=None, session_id=None, printer_id=None,
             control=False):
    #import wdb;wdb.set_trace()

    print '//// do_event / data=', data, 'session_id=', session_id, 'printer_id=', printer_id

    """
        Execute an event on client side.

        If client does not response in 60 seg, raise DenialService.
        Else return client result.
    """
    if not data:
        data = dict()

    global event_id

    event_id += 1
    result = {}
    item = {
        'id': event_id,
        'event': event,
        'data': json.dumps(data),
    }

    # Select target of queue. Control go to Chrome Application, else take
    # printers. All control queue end with ':'.
    if control:
        qids = [session_id] if session_id else [qid for qid in event_hub.keys()
                                                if qid[-1] == ':']
    else:
        qid = ':'.join([session_id or '', printer_id or ''])
        qids = [qid] if qid != ':' else event_hub.keys()
        qids = [qid for qid in qids if
                qid in event_hub.keys() and qid[-1] != ':']

    _logger.debug("=======VARIOS QIDS======================")
    _logger.debug("Send Message '%s' to spools: %s" % (event, qids))

    for qid in qids:
        _logger.debug("===========UNO POR CADA QID=============")
        event_event[event_id] = threading.Event()
        event_result[event_id] = None
        event_hub[qid].put(item)
        w = event_event[event_id].wait(300)
        if not w:
            raise osv.except_osv(_('Error!'), _('Timeout happen!!'))

        _logger.debug("Send Message Ret '%s': %s" % (qids, w))

        result[qid] = event_result[event_id]
        event_hub[qid].task_done()

    _logger.debug("Send Message Result '%s' was: %s" % (qids, result))

    return [result[qid] for qid in qids if qid in result]


def do_return(req, result):
    print '//// do_return / req=', req,'result=',result
    """ Take response from the client side, and push result in the queue.
        If response is not related to any previous request drop the message.
    """
    sid = req.session_id
    pid = req.params.get('printer_id', '')
    qid = ':'.join([sid, pid])

    if qid not in event_hub:
        _logger.debug("<<< Drop message: %s" % result)
        return False

    this_event_id = int(result['event_id'])
    event_result[this_event_id] = result
    event_event[this_event_id].set()
    del event_event[this_event_id]


# Controller
class FiscalPrinterController(oeweb.Controller):
    _cp_path = '/fp'

    @oeweb.jsonrequest
    def login(self, req, database, login, password, **kw):
        print '//// login / req=', req, 'database=', database, 'login=', login, 'password=', password

        wsgienv = req.httprequest.environ
        env = dict(
            base_location=req.httprequest.url_root.rstrip('/'),
            HTTP_HOST=wsgienv['HTTP_HOST'],
            REMOTE_ADDR=wsgienv['REMOTE_ADDR'],
        )
        req.session.authenticate(database, login, password, env)
        return {'session_id': req.session_id}

    @oeweb.jsonrequest
    def push(self, req, **kw):
        print '//// push / req=', req
        return do_return(req, kw)

    def on_close_spool(self, **kw):
        print '//// on_close_spool'
        _logger.debug("Closing spool %s" % self.qid)
        return

    @oeweb.httprequest
    def spool(self, req, **kw):
        #import wdb;wdb.set_trace()
        print '//// spool / req=', req
        global event_id
        global event_hub
        print 'event_id', event_id, 'event_hub', event_hub
        sid = req.session_id
        pid = req.params.get('printer_id', '')
        print '+++++++++++++++++++++ SE CONECTA', pid
        print 'sesion',sid
        print 'printer',pid

        qid = ':'.join([sid, pid])
        self.qid = qid

        if qid in event_hub:
            _logger.debug("Close connection spool %s by duplication." % qid)
            return req.make_response('\n\nevent: close\n\n\n\n',
                                     [('cache-control', 'no-cache'),
                                      ('Content-Type', 'text/event-stream')])

        _logger.debug("Open new connection spool: %s" % qid)

        event_hub[qid] = Queue()

        if req.httprequest.headers.get('accept') != 'text/event-stream':
            return req.make_response('Not implemented',
                                     headers={'Status': '501 Not Implemented'})

        # Last event id.
        last_event_id = req.httprequest.headers.get('last-event-id', 0,
                                                    type=int)
        if last_event_id > event_id:
            event_id = last_event_id

        self.spool_response = req.make_response(
            self.event_source_iter(last_event_id),
            [('cache-control', 'no-cache'),
             ('Content-Type', 'text/event-stream')])
        return self.spool_response

    @oeweb.jsonrequest
    def fp_info(self, req, printers, **kw):
        print '//// fp_info / req=', req, 'printers=', printers
        return do_return(req, printers);

    def event_source_iter(self, event_id):
        print '//// event_source_iter / event_id=', event_id
        qid = self.qid

        yield '\n\n'  # Force connection recognition on client
        while True:
            try:
                message = event_hub[qid].get(timeout=timeout)
                _logger.debug("Send message NUMERO DOS %s to %s" % (
                    message['event'], qid))
                yield 'event: %(event)s\ndata: %(data)s\nid: %(id)s\n\n' % message
            except Empty:
                # Force check status.
                # If connection, spool still alive.
                yield 'event: ping\n\n'

