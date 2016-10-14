from twisted.python import log
from twisted.web import http, proxy

class ProxyClient(proxy.ProxyClient):
    """Mangle returned header, content here.

    Use `self.father` methods to modify request directly.
    """
    def handleHeader(self, key, value):
        # change response header here
        log.msg("Header: %s: %s" % (key, value))
        proxy.ProxyClient.handleHeader(self, key, value)

    def handleResponsePart(self, buffer):
        # change response part here
        log.msg("Content: %s" % (buffer[:50],))
        # make all content upper case
        proxy.ProxyClient.handleResponsePart(self, buffer.upper())

class ProxyClientFactory(proxy.ProxyClientFactory):
    protocol = ProxyClient

class ProxyRequest(proxy.ProxyRequest):
    protocols = dict(http=ProxyClientFactory)

class Proxy(proxy.Proxy):
    requestFactory = ProxyRequest

class ProxyFactory(http.HTTPFactory):
    protocol = Proxy

portstr = "tcp:8180:interface=localhost"

if __name__ == '__main__': # $ python proxy_modify_request.py
    import sys
    from twisted.internet import endpoints, reactor

    def shutdown(reason, reactor, stopping=[]):
        """Stop the reactor."""
        if stopping: return
        stopping.append(True)
        if reason:
            log.msg(reason.value)
        reactor.callWhenRunning(reactor.stop)

    log.startLogging(sys.stdout)
    endpoint = endpoints.serverFromString(reactor, portstr)
    d = endpoint.listen(ProxyFactory())
    d.addErrback(shutdown, reactor)
    reactor.run()
else: # $ twistd -ny proxy_modify_request.py
    from twisted.application import service, strports

    application = service.Application("proxy_modify_request")
    strports.service(portstr, ProxyFactory()).setServiceParent(application)
