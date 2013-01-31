import logging
from collections import namedtuple
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPResponse, HTTPError
from tornado.httputil import url_concat
import inspect
import base64

Error = namedtuple('Error', 'code,reason,url')

log = logging.getLogger('protobuf_logger')

def construct_protobuf_service(service_stub, host, fetcher = AsyncHTTPClient().fetch, logger=log, **kwargs):
    class ProtoService(service_stub):
        def __init__(self, host, fetcher, **kwargs):
            rpc_channel = RpcChannel(host, fetcher, logger, **kwargs)
            service_stub.__init__(self, rpc_channel)

    return ProtoService(host, fetcher, **kwargs)

class RpcController(object):
    def __init__(self):
        self.Reset()

    def Reset(self):
        self.fail_reason = None
        self.canceled = False
        self.failed = False

    def StartCancel(self):
        self.canceled = True

    def IsCanceled(self):
        return self.canceled

    def SetFailed(self, reason):
        self.failed = True
        self.fail_reason = reason

    def ErrorText(self):
        return self.fail_reason

    def Failed(self):
        return self.failed

class RpcChannel(object):
    ct_header = 'Content-Type'
    protobuf_ct = 'application/x-protobuf'
    get_arg = 'request'

    def __init__(self, host, fetcher, logger, **kwargs):
        self.host = host
        self.fetcher = fetcher
        self.is_async = 'callback' in inspect.getargspec(fetcher).args
        self.logger = logger
        self.kwargs = kwargs
        self.request_args = inspect.getargspec(HTTPRequest.__init__).args[1:]

    def construct_http_request(self, url, body):
        request_params = dict(
            method = 'POST',
            headers = {}
        )

        for k, v in self.kwargs.iteritems():
            if k in self.request_args:
                request_params[k] = v

        request_params['headers'].update({self.ct_header: self.protobuf_ct})

        data = self.kwargs.get('data', {})
        if request_params['method'] not in ("POST", "PATCH", "PUT"):
            data[self.get_arg] = base64.b64encode(body)
        else:
            request_params['body'] = body

        return HTTPRequest(url_concat(url, data), **request_params)

    def CallMethod(self, method_descriptor, rpc_controller, request, response_class, done):
        url = self.host.rstrip('/') + '/{0}/{1}'.format(method_descriptor.containing_service.name,
            method_descriptor.name)

        def _cb(response):
            rc = response_class()
            try:
                rc.ParseFromString(response.body)
            except Exception as e:
                _error_no_proto_msg(response.body, response.headers, response.error or str(e), response.code if response.error else None)
                return

            if response.error is not None \
                or rpc_controller.IsCanceled() \
                or response.headers.get(self.ct_header) != self.protobuf_ct:
                    _error(rc, response.headers, response.error, response.code)
                    return

            self.logger.debug('Decoded protobuf response from %s', response.request.url, extra={'_protobuf': str(rc)})
            done(rc)

        def _error(response, headers, error = None, code = None):
            fail_reason = 'RPC fail: ' + _compose_reason(headers, error) + "\n response is:\n" + str(response)
            rpc_controller.SetFailed(_compose_error(error, code, fail_reason))
            done(None)

        def _error_no_proto_msg(msg, headers, error, code):
            reason_header = 'RPC fail: ' + _compose_reason(headers, error)
            try:
                fail_reason = reason_header + ("\nmessage is:\n" + str(msg) if msg is not None else "")
                error_data = _compose_error(error, code, fail_reason)
            except ValueError:
                fail_reason = reason_header + ("\nCan't show message")
                error_data = _compose_error(error, code, fail_reason)
            rpc_controller.SetFailed(error_data)
            done(None)

        def _compose_reason(headers, error):
            fail_reason = ''

            if error is not None:
                fail_reason += str(error)
            if headers.get(self.ct_header, None) != self.protobuf_ct:
                fail_reason += 'Wrong content-type in response: ' + str(headers.get(self.ct_header, None))
            if rpc_controller.IsCanceled():
                fail_reason += 'Call was canceled by client'

            if fail_reason == '':
                fail_reason = 'Unknown fail!'

            return fail_reason

        def _compose_error(error, code, reason):
            return Error(code, reason, url)

        rpc_controller.Reset()

        http_request = self.construct_http_request(url, request.SerializeToString())
        self.logger.debug('Encoding protobuf request to %s %s', http_request.method, http_request.url, extra={'_protobuf': str(request)})

        if self.is_async:
            self.fetcher(http_request, callback = _cb)
        else:
            try:
                response = self.fetcher(http_request)
                _cb(response)
            except HTTPError, e:
                _cb(e.response or HTTPResponse(http_request, e.code, error = e))
