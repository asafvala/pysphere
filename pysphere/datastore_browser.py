import urllib, urllib2, httplib
from unverified_https_handler import UnVerifiedHTTPSHandler
import sys
from pysphere import VIServer

class DatastoreBrowser(object):

    def __init__(self, server_instance, datastore_name, dc_name=None):
        self._s = server_instance
        self._datastore = datastore_name
        self._datacenter = dc_name
        self._ssl_handler = UnVerifiedHTTPSHandler()
        self.relogin()

    def relogin(self):
        self._handler = self._build_auth_handler()

    def upload(self, local_file_path, remote_file_path):
        fd = open(local_file_path, "r")
        data = fd.read()
        fd.close()
        resource = "/folder/%s" % remote_file_path.lstrip("/")
        url = self._get_url(resource)
        resp = self._do_request(url, data)
        return resp.code == 200

    def download(self, remote_file_path, local_file_path):
        resource = "/folder/%s" % remote_file_path.lstrip("/")
        url = self._get_url(resource)

        if sys.version_info >= (2, 6):
            resp = self._do_request(url)
            CHUNK = 16 * 1024
            fd = open(local_file_path, "wb")
            while True:
                chunk = resp.read(CHUNK)
                if not chunk: break
                fd.write(chunk)
            fd.close()
        else:
            urllib.urlretrieve(url, local_file_path)

    def _do_request(self, url, data=None):
        opener = urllib2.build_opener(self._ssl_handler, self._handler)
        request = urllib2.Request(url, data=data)
        if data:
            request.get_method = lambda: 'PUT'

        return opener.open(request)

    def _get_url(self, resource):
        if not resource.startswith("/"):
            resource = "/" + resource

        params = {"dsName":self._datastore}
        if self._datacenter:
            params["dcPath"] = self._datacenter

        params = urllib.urlencode(params)

        return "%s%s?%s" % (self._get_service_url(), resource, params)

    def _get_service_url(self):
        service_url = self._s._proxy.binding.url
        return service_url[:service_url.rindex("/sdk")]

    def _build_auth_handler(self):
        service_url = self._get_service_url()
        user = self._s._VIServer__user
        password = self._s._VIServer__password
        auth_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        auth_manager.add_password(None, service_url, user, password)
        return urllib2.HTTPBasicAuthHandler(auth_manager)
