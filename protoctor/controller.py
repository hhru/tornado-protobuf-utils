# coding=utf-8


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
