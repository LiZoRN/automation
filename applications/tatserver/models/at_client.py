
import xmlrpclib
import httplib
import socket

class TimeoutHTTP(httplib.HTTP):
    def __init__(self, host='', port=None, strict=None,
                timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        if port == 0:
            port = None
        self._setup(self._connection_class(host, port, strict, timeout))

    def getresponse(self, *args, **kw):
        return self._conn.getresponse(*args, **kw)

class TimeoutTransport(xmlrpclib.Transport):
    def __init__(self,  timeout=socket._GLOBAL_DEFAULT_TIMEOUT, *l, **kw):
        xmlrpclib.Transport.__init__(self, *l, **kw)
        self.timeout=timeout

    def make_connection(self, host):
        host, extra_headers, x509 = self.get_host_info(host)
        conn = TimeoutHTTP(host, timeout=self.timeout)
        return conn

class TimeoutServerProxy(xmlrpclib.ServerProxy):
    def __init__(self, uri, timeout= socket._GLOBAL_DEFAULT_TIMEOUT, *l, **kw):
        kw['transport']=TimeoutTransport(timeout=timeout, use_datetime=kw.get('use_datetime',0))
        xmlrpclib.ServerProxy.__init__(self, uri, *l, **kw)


class DbRpc:
    # def add_client(self,name):
    # client = db(db.client.name==name).select().first()
    #     if None == client:
    #         raise HTTP(400, "<h1>Client not finded,may deleted by others.<a href=\"%s\"><br/>Go back homepage</h1>"%(URL("index")))
    #     DbRpc.db_client[name] = ATClient(client.url)
    #     return True
    #
    # def remove_client(self,name):
    #     client = db(db.client.name==name).select().first()
    #     if None == client:
    #         raise HTTP(400, "<h1>Client not finded,may deleted by others.<a href=\"%s\"><br/>Go back homepage</h1>"%(URL("index")))
    #     DbRpc.db_client[name].remove()
    #     return True

    def _make_connection(self, host):
        # conn = xmlrpclib.Transport.make_connection(self, host)
        # conn.timeout = self.timeout
        return TimeoutServerProxy(host)
        return xmlrpclib.ServerProxy(host,allow_none=True)
    def suit_setup(self, url, suit_cfg):
        return self._make_connection(url).suit_setup(suit_cfg)

    def suit_teardown(self, url):
        return self._make_connection(url).suit_teardown()

    def test_setup(self, url, test_cfg):
        return self._make_connection(url).test_setup(test_cfg)

    def test_teardown(self, url):
        return self._make_connection(url).test_teardown()

    def test_start(self, url, test_plan):
        return self._make_connection(url).test_start(test_plan)

    def test_download(self,url,test_plan):
        configfile= proj.gen_user_debug_config(test_plan.project.name,test_plan.project.sw)
        if os.path.exists(configfile):
            return self._make_connection(url).test_download(xmlrpclib.Binary(open(configfile,'rb').read()))

    def test_stop(self, url, test_plan):
        return self._make_connection(url).test_stop(test_plan)

    def show_test_status(self, url, plan_id):
        return self._make_connection(url).show_test_status(plan_id)

    def show_device_status(self, url):
        return self._make_connection(url).show_device()

    def show_device(self, url):
        return self._make_connection(url).show_device()

    def show_report(self, url, plan_id):
        return self._make_connection(url).show_report(plan_id)

    def show_all_report(self, url):
        return self._make_connection(url).all_report_display()

    def show_report_by_device(self, url, deviceid):
        return self._make_connection(url).show_report_by_device(deviceid)

    def open_file(self, url, file):
        return self._make_connection(url).open_file(file)


db_rpc = DbRpc()

