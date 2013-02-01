from channel import RpcChannel, AsyncRpcChannel

def construct_async_protobuf_service(service_stub, host, fetcher, **kwargs):
    class ProtoService(service_stub):
        def __init__(self, host, fetcher, **kwargs):
            rpc_channel = AsyncRpcChannel(host, fetcher, **kwargs)
            service_stub.__init__(self, rpc_channel)

    return ProtoService(host, fetcher, **kwargs)

def construct_sync_protobuf_service(service_stub, host, fetcher, **kwargs):
    class ProtoService(service_stub):
        def __init__(self, host, fetcher, **kwargs):
            rpc_channel = RpcChannel(host, fetcher, **kwargs)
            service_stub.__init__(self, rpc_channel)

    return ProtoService(host, fetcher, **kwargs)


