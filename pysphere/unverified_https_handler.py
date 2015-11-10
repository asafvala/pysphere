import urllib, urllib2, httplib

class UnVerifiedHTTPSHandler(urllib2.HTTPSHandler):
    def __init__(self):
        urllib2.HTTPSHandler.__init__(self)

    def https_open(self, req):
        #Rather than pass in a reference to a connection class, we pass in
        # a reference to a function which, for all intents and purposes,
        # will behave as a constructor
        return self.do_open(self.getConnection, req)

    def getConnection(self, host, timeout=300):
        import ssl
        return httplib.HTTPSConnection(host,context=ssl._create_unverified_context())
