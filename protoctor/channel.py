# coding=utf-8

import base64
from collections import namedtuple
import inspect
import time

from tornado.httpclient import HTTPRequest, HTTPResponse, HTTPError
from tornado.httputil import url_concat

Error = namedtuple('Error', 'error,code,reason')


class RpcChannel(object):
    CONTENT_TYPE_HEADER = 'Content-Type'
    PROTOBUF_CONTENT_TYPE = 'application/x-protobuf'
    GET_ARGUMENT_NAME = 'request'

    def __init__(self, host, fetcher, **kwargs):
        self.host = host
        self.fetcher = fetcher
        self.logger = kwargs.get('logger')
        self.kwargs = kwargs
        self.request_args = inspect.getargspec(HTTPRequest.__init__).args[1:]

    def construct_http_request(self, url, body):
        request_params = dict(
            method='POST',
            headers={
                RpcChannel.CONTENT_TYPE_HEADER: RpcChannel.PROTOBUF_CONTENT_TYPE
            }
        )

        for k in self.kwargs:
            if k in self.request_args:
                request_params[k] = self.kwargs[k]

        data = self.kwargs.get('data', {})
        if request_params['method'] not in ('POST', 'PATCH', 'PUT'):
            data[RpcChannel.GET_ARGUMENT_NAME] = base64.b64encode(body)
        else:
            request_params['body'] = body

        return HTTPRequest(url_concat(url, data), **request_params)

    def fetch(self, http_request, callback):
        try:
            response = self.fetcher(http_request)
            callback(response)
        except HTTPError as e:
            callback(e.response or HTTPResponse(http_request, e.code, error=e))

    def CallMethod(self, method_descriptor, rpc_controller, request, response_class, done):
        url = '{host}/{service}/{method}'.format(
            host=self.host.rstrip('/'), service=method_descriptor.containing_service.name, method=method_descriptor.name
        )

        def _cb(response):
            decode_start_time = time.time()

            rc = response_class()
            try:
                rc.ParseFromString(response.body)
            except Exception as e:
                _error_no_proto_msg(response.body, response.headers, str(e), response.code)
                return

            if response.error is not None or rpc_controller.IsCanceled():
                _error(rc, response.headers, response.error, response.code)
                return

            if self.logger:
                response_content_type = response.headers.get(RpcChannel.CONTENT_TYPE_HEADER)
                if response_content_type != response.request.headers.get(RpcChannel.CONTENT_TYPE_HEADER):
                    self.logger.warn('Wrong Content-Type in response: %s', response_content_type)

                self.logger.info(
                    'Decoded protobuf response from %s in %.2fms',
                    response.request.url, (time.time() - decode_start_time) * 1000,
                    extra={'_protobuf': rc}
                )

            done(rc)

        def _error(response, headers, error=None, code=None):
            fail_reason = 'RPC fail: ' + _compose_reason(headers, error) + '\n response is:\n' + str(response)
            rpc_controller.SetFailed(_compose_error(error, code, fail_reason))
            done(None)

        def _error_no_proto_msg(msg, headers, error, code):
            reason_header = 'RPC fail: ' + _compose_reason(headers, error)

            try:
                fail_reason = reason_header + ('\nmessage is:\n' + str(msg) if msg is not None else '')
                error_data = _compose_error(error, code, fail_reason)
            except ValueError:
                fail_reason = reason_header + "\nCan't show message"
                error_data = _compose_error(error, code, fail_reason)

            rpc_controller.SetFailed(error_data)
            done(None)

        def _compose_reason(headers, error):
            fail_reason = ''

            if error is not None:
                fail_reason += str(error)

            if rpc_controller.IsCanceled():
                fail_reason += 'Call was canceled by client'

            if fail_reason == '':
                fail_reason = 'Unknown fail!'

            return fail_reason

        def _compose_error(error, code, reason):
            return Error(error, code, reason)

        rpc_controller.Reset()

        encode_start_time = time.time()
        http_request = self.construct_http_request(url, request.SerializeToString())

        if self.logger:
            self.logger.info(
                'Encoded protobuf request to %s %s in %.2fms',
                http_request.method, http_request.url, (time.time() - encode_start_time) * 1000,
                extra={'_text': str(request)}
            )

        self.fetch(http_request, _cb)


class AsyncRpcChannel(RpcChannel):
    def fetch(self, http_request, callback):
        self.fetcher(http_request, callback=callback)
