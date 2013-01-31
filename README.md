Tornado protocol buffers utilities
======================

Usage Example: copy and paste in any RequestHandler

```
rpc_controller = tornado.protobuf.utils.client.RpcController()

def _search_service_cb(resume_search_result):
   if resume_search_result is not None:
       logging.debug('Search without error')
       logging.debug('\n' + str(resume_search_result))
   else:
       logging.debug('Search error: ' + controller.ErrorText())

fetcher = AsyncHTTPClient().fetch
logger = logging

search_service = tornado.protobuf.client.construct_service(ResumeSearch_Stub, self.config.protoSearchHost, fetcher, logger, method = 'POST', data = {'requestId' : self.requestId})
search_service.ResumeSearch(rpc_controller, resume_pb2.ResumeCriteria(), _search_service_cb)
```

```fetcher``` can be:
 * ```tornado.httpclient.AsyncHTTPClient().fetch``` async http client built in Tornado
 * ```tornado.httpclient.HTTPClient.fetch``` blocking http client built in Tornado
 * ```frontik.handler.PageHandler().fetch_request``` async http client wrapper in Frontik-based applications
 * any other http client that applies ```tornado.httpclient.HTTPRequest``` in their fetch functions

```construct_service``` almost applies any number of kw arguments that will be proxied to HTTPRequest constructor.
Except ```data``` argument, that should be dict of any additional params that should be passed into request url (for example, passing ```data = {'requestId' : 1}```
would provide request url as the following: ```http://proto.host:port/SearchService/ResumeSearch?requestId=1```).

Almost if your request method differs from POST, PATCH, PUT (which requires http request body), GET for e.g., your protobuf request would be base64-encoded and will be applied to ```request``` argument.
For exmaple:

```http://proto.host:port/SearchService/ResumeSearch?request=IAAoADAyQhYKEtC90LDRh9Cw0LvRjNC90LjQuhgASgYIARCF7QfaAcABCLr%2FIQin7YYHCJ%2Fx5gYI5L5kCMHkjgEI%2B%2B6bAwjI77gGCIf7jwcI9Ir%2BAwiCoZoFCJPG8QYI%2BrK%2BAwi07P4FCMWPLQjBhtgGCMCt9QYI5MC7BgiU8osHCPCbvgQIm8vEBgjsi6wGCNiZjwcI%2Bbi7Bgi6kqsCCP%2FWpgQIqe%2FlAwjX5%2B8GCJqn6wYIttqLBwjcyLIECKryrgYI5cSLBwj6pIcHCMC5mgYIspz5BAiJsIwHCMG63QQI6vOWBgjP34cH&requestId=11```

