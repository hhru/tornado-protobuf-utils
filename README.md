Tornado protocol buffers utilities
======================

Usage Example: copy and paste in any RequestHandler

Asynchronous
-------------

```
from protoctor.client import construct_async_protobuf_service
from protoctor.controller import RpcController

rpc_controller = RpcController()

def _search_service_cb(resume_search_result):
   if resume_search_result is not None:
       logging.debug('Search without error')
       logging.debug('\n' + str(resume_search_result))
   else:
       logging.debug('Search error: ' + controller.ErrorText())

fetcher = AsyncHTTPClient().fetch

search_service = construct_async_protobuf_service(ResumeSearch_Stub,
    self.config.protoSearchHost,
    fetcher,
    logger = logging, method = 'POST', data = {'requestId' : self.requestId}
)
search_service.ResumeSearch(rpc_controller, resume_pb2.ResumeCriteria(), _search_service_cb)
```

```fetcher``` can be:
 * ```tornado.httpclient.AsyncHTTPClient().fetch``` async http client built in Tornado
 * ```frontik.handler.PageHandler().fetch_request``` async http client wrapper in Frontik-based applications
 * any other http client that accepts ```tornado.httpclient.HTTPRequest``` in their fetch function.

```construct_async_protobuf_service``` almost accepts any number of kw arguments that will be proxied to HTTPRequest constructor, except:
 * ```data``` argument, that should be dict of any additional params that should be passed into request url (for example, passing ```data = {'requestId' : 1}```
would provide request url as the following: ```http://proto.host:port/SearchService/ResumeSearch?requestId=1```)
 * ```logger``` to log messages about client-server interaction inside rpc channel

If your request method differs from POST, PATCH, PUT (which require http request body), GET for e.g., your protobuf request would be base64-encoded and will be applied to ```request``` argument.
For example:

```
http://proto.host:port/SearchService/ResumeSearch?request=IAAoADAyQhYKEtC90LDRh9Cw0LvRjNC90LjQuhgASgYIARCF7QfaAcABCLr%2FIQin7YYHCJ%2Fx5gYI5L5kCMHkjgEI%2B%2B6bAwjI77gGCIf7jwcI9Ir%2BAwiCoZoFCJPG8QYI%2BrK%2BAwi07P4FCMWPLQjBhtgGCMCt9QYI5MC7BgiU8osHCPCbvgQIm8vEBgjsi6wGCNiZjwcI%2Bbi7Bgi6kqsCCP%2FWpgQIqe%2FlAwjX5%2B8GCJqn6wYIttqLBwjcyLIECKryrgYI5cSLBwj6pIcHCMC5mgYIspz5BAiJsIwHCMG63QQI6vOWBgjP34cH&requestId=11
```

Synchronous
-------------

Everything is similar to async way, but:

```fetcher``` should be:
* ```tornado.httpclient.HTTPClient.fetch``` blocking http client built in Tornado


Function for creating protobuf service is ```construct_sync_protobuf_service```