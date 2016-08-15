#!/usr/bin/env python
# encoding: utf-8
'''
orange -- tat rpc server 

orange is a TAT Client RPC-Server! Connect TAT tool to TAT web server,and register XML-RPC Instance/Function

@author:     zhuo.li

@copyright:  2014 TCL VAL-Performance Team. All rights reserved.

@license:    license

@contact:    Zhuo.Li@tcl.com
'''

import sys
import os
from optparse import OptionParser
import xmlrpclib
import SimpleXMLRPCServer
import SocketServer
import socket
import threading
import re
from SvnScript import SvnScript
from lxml import etree
import codecs
import xml.etree.ElementTree as ET
__all__ = []
__version__ = 0.1
__date__ = '2014-10-25'
__updated__ = '2014-10-26'

SimpleXMLRPCServer.allow_reuse_address = 1
server_port = 8080
server_url = 'http://172.16.11.195:8000/tatserver/rpc/call/xmlrpc'
    # server_url = 'http://127.0.0.1:8000/TATServer/rpc/call/xmlrpc'
SCRIPTPATH = "../Script"

class TestData:
    """Used to get the latest TestData.xml on TAT"""
    def __init__(self,dir = r"..\Plan",data_file = "TestData.xml"):
        self.dir = dir
        self.data_file = data_file

    def get_latest(self,product_name):
        def _compare(x, y):
            """Order by Datetime"""
            stat_x = os.stat(self.dir + "/" + x)
            stat_y = os.stat(self.dir + "/" + y)
            if stat_x.st_ctime > stat_y.st_ctime:
                return -1
            elif stat_x.st_ctime < stat_y.st_ctime:
                return 1
            else:
                return 0
        pat = re.compile(r"%s\s*-\s*\d*"%(product_name))
        iterms = os.listdir(self.dir)
        iterms.sort(_compare)
        for iterm in iterms:
            out = pat.search(iterm)
            if out!=None:
                test_data = os.path.join(os.path.join(self.dir,  out.group()),self.data_file)
                # return codecs.open(os.path.join(test_data), 'r', 'utf-8').read()
                # return open(test_data).read()
                return xmlrpclib.Binary(open(test_data,'rb').read())
        return ""

    def get_newer(self,product_name,pertime):
        def _compare(x, y):
            """Order by Datetime"""
            stat_x = os.stat(self.dir + "/" + x)
            stat_y = os.stat(self.dir + "/" + y)
            if stat_x.st_ctime > stat_y.st_ctime:
                return -1
            elif stat_x.st_ctime < stat_y.st_ctime:
                return 1
            else:
                return 0
        pat = re.compile(r"%s\s*-\s*\d*"%(product_name))
        iterms = os.listdir(self.dir)
        iterms.sort(_compare)
        for iterm in iterms:
            out = pat.search(iterm)
            if out!=None:
                test_data = os.path.join(os.path.join(self.dir,  out.group()),self.data_file)
                return open(test_data).read()

class RpcClient(object):
    """Connect to tat server, XML-RPC is used to call the function on web tat server"""
    def __init__(self,server = server_url):
        self.url = ""
        self.hostname = socket.gethostname()
        self.server = xmlrpclib.ServerProxy(server)
        print "Connect to Server %s"%server

    def test_report(self,name,test_data):
        """test report to server
        @param test_data: client host name
        @type    test_data: string
        @rtype: True/False
        @return: If success,return False.Else,return True.
        B{Example:}
          - C{test_report(deviceid-pruductname,test_data"")}
        """
        return self.server.test_report(name,test_data)

    def sync_client_status(self,devices_status):
        """sync client status to server
        @param devices_status: client host name
        @type    devices_status: string -- "IsRunning" or "Idle"
        @rtype: True/False
        @return: If success,return False.Else,return True.
        B{Example:}
          - C{sync_client_status("8bf5f7f-M812"."IsRunning".,"")}
        """
        self.server.sync_client_status(self,self.hostname,devices_status)

    def host_hello(self,url):
        """Client Online report
        @param url: ip:port
        @type    url: string
        @rtype: True/False
        @return: If success,return False.Else,return True.
        B{Example:}
          - C{host_hello(socket.gethostname(),"http://127.0.0.1:8000")}
        """
        return self.server.host_hello(self.hostname,url)

    def host_leave(self):
        """Client Leave
        @rtype: True/False
        @return: If success,return False.Else,return True.
        B{Example:}
          - C{host_leave(socket.gethostname())}
        """
        return self.server.host_leave(self.hostname)

    def device_hello(self,device_id):
        """Device  detect and report to server
        @param device_id: device_id used by adb
        @type device_id: string
        @param product_name: product name
        @type product_name: string
        @rtype: True/False
        @return: If success,return False.Else,return True.
        B{Example:}
          - C{device_hello("8bf5f7f-M812")}
        """
        return self.server.device_hello(self.hostname,device_id)

    def device_leave(self,device_id):
        """Device offline and report to server
        @param device_id: device_id used by adb
        @type device_id: string
        @rtype: True/False
        @return: If success,return False.Else,return True.
        B{Example:}
          - C{device_leave("8bf5f7f-M812")}
        """
        return self.server.device_leave(device_id)

    def open_file(self,file):
        """Open server file
        @param file: file addr
        @type file: string
        @return: file binary stream.
        B{Example:}
          - C{open_file("testplan.xml")}
        """
        return xmlrpclib.Binary(open(file,'rb').read())

class XMLRPCServerThreading(SocketServer.ThreadingMixIn,SimpleXMLRPCServer.SimpleXMLRPCServer): 
    pass

class RpcServer(object):
    """TAT Server that ruuning on client, and register XML-RPC Instance/Function"""
    
    instance=None
    mutex=threading.Lock()
    
    def __init__(self,port = server_port,web_server = server_url,data_path = "..\\TAT\\Plan",auto=False):
        RpcServer.instance=self
        print RpcServer.instance
        self.port = int(port)
        self.hostname = socket.gethostname()
        self.url = socket.gethostbyname(self.hostname)
        self.devices = {}
        self.testplan_status = {}
        self.rpc_client = RpcClient(web_server)
        self.server = SimpleXMLRPCServer.SimpleXMLRPCServer((self.url, self.port))
        self.register_obj = []
        self.auto = auto
        self.property = {}
        self.test_data = TestData(data_path)
        self.script = SvnScript(SCRIPTPATH)
        try:
            self._host_hello("http://%s:%s"%(self.url,self.port))
        except:
             print "Web server is not on line"

        
    def __del__(self):
        """client leave, TDB!!"""
        #auto leave may not used!!!
        if self.auto:
            try:
                self._host_leave()
            except:
                print "leave failed!"
        print('RpcServer has been destroyed')

    def __adb_devices(self):
        """show devices"""
        self.devices= re.findall(r"(\w+\-?\w+)\s*device\b", os.popen('adb devices').read())

    def __get_prop(self):
        """get devices property"""
        for device in self.devices:
            #init
            tempProp = {"hardware":0,"product":0,"display_id":0,"region":0,"build_type":0,"build_date":0,"version":0}
            prop_buff = os.popen('adb -s '+device+' shell getprop').read()
            try:
                tempProp["hardware"] = re.findall(r"\[ro.hardware\]:\s*\[(\w*)\]", prop_buff)[0]
                tempProp["product"] = re.findall(r"\[ro.product.name\]:\s*\[(\w*)\]", prop_buff)[0]
                tempProp["display_id"] = re.findall(r"\[ro.build.display.id\]:\s*\[(\w*)\]", prop_buff)[0]
                tempProp["region"] = re.findall(r"\[ro.product.locale.region\]:\s*\[(\w*)\]", prop_buff)[0]
                tempProp["build_type"] = re.findall(r"\[ro.build.type\]:\s*\[(\w*)\]", prop_buff)[0]
                tempProp["build_date"] = re.findall(r"\[ro.build.date\]:\s*\[(.*)\]", prop_buff)[0]
                tempProp["version"] = re.findall(r"\[ro.build.version.incremental\]:\s*\[(.*)\]", prop_buff)[0]
            except:
                print "Log to do!"
            self.property[device]=tempProp

    def _show_device(self):
        """get devices and it's property"""
        self.__adb_devices()
        self.__get_prop()
        return self.property

    def _register_object(self,object):
        """register XML-RPC function"""
        self.register_obj.append(object)

    def _test_status_display(self,plan_id):
        """get test status"""
        try:
            return self.testplan_status[plan_id]
        except:
            return {}

    def _device_status_display(self):
        """get device status"""
        pass

    def _get_test_report(self,plan_id):
        """get or generate test data by plan id"""
        pass

    def _host_hello(self,url):
        """host hello 2 server"""
        return self.rpc_client.host_hello(url)

    def _host_leave(self):
        """host leave from server"""
        return self.rpc_client.host_leave()

    def _device_hello(self,device_id,product):
        """device hello 2 server"""
        return self.rpc_client.device_hello(device_id,product)

    def _device_leave(self,device_id):
        """device leave from server"""
        return self.rpc_client.device_leave(device_id)

    def _send_report(self,name,test_data):
        """send report to server"""
        # threading.Thread(target= self.rpc_client.test_report,args = (name,test_data)).start()
        # return True
        return self.rpc_client.test_report(name,test_data)

    def _sync_client_status(self,device_status):
        """sync client status 2 server"""
        return self.rpc_client.sync_client_status(self.self.devices)

    def _start(self):
        """start the TAT Client XML-RPC Server"""
        self.server.register_instance(self)
        for obj in self.register_obj:
            method_list = [method for method in dir(obj) if callable(getattr(obj,method))]
            for method in  method_list:
                self.server.register_function(getattr(obj,method))
        print "Listening On:%s:%s"%(self.url,self.port)
        self.server.serve_forever()

    @staticmethod
    def GetInstance():
        """Singleton"""
        if(RpcServer.instance==None):
            RpcServer.mutex.acquire()
            if(RpcServer.instance==None):
                print('Init Instance')
                RpcServer.instance=RpcServer()
            else:
                print('Instance Exist!')
            RpcServer.mutex.release()
        else:
            # print('Instance Exist!')
            pass
        return RpcServer.instance

    def suit_setup(self,suit_cfg):
        """host/tool/device/environment setup before test start
        @param suit_cfg:
        @type    suit_cfg: string
        @rtype: True/False
        @return: If success,return False.Else,return True.
        B{Example:}
          - C{suit_setup("cfg.ini")}
        """
        # TO DO!!
        pass
    def suit_teardown(self):
        """host/tool/device/environment teardown after all test finish/stop.
        @rtype: True/False
        @return: If success,return False.Else,return True.
        B{Example:}
          - C{suit_teardown()}
        """
        # TO DO!!
        pass

    def test_setup(self,test_cfg):
        """ test prepare before test start
        @param test_cfg: test condition/parameter ----- (etc.picture/contacts number)
        @type    test_cfg: string
        @rtype: True/False
        @return: If success,return False.Else,return True.
        B{Example:}
          - C{test_setup("cfg.ini")}
        """
        # TO DO!!
        pass

    def test_teardown(self):
        """ test teardown after test finish/stop.
        @rtype: True/False
        @return: If success,return False.Else,return True.
        B{Example:}
          - C{test_teardown()}
        """
        # TO DO!!
        pass

    def test_start(self,test_plan):
        """ test start attach to test_plan
        @param test_plan: xml file string describe the test plan,such as plantype/scrip
        @type test_plan: string
        @rtype: True/False
        @return: If success,return False.Else,return True.
        B{Example:}
          - C{test_start(plan)}
        """
        # STUB TO DO!!
        #print test_plan
        try:
            script_tag = ET.fromstring(test_plan).find("Script").text
            # get script from svn,to workspace
            self.script.get_script_by_tag(script_tag)
            # self.test_plan = test_plan
            # self.testplan_status["testplan_id"] = "IsRunning"
            # call tat client interface and return,TO DO!!
            # return self.testplan_status["testplan_id"]
        except:
            print "plan:%s start failed"
        return True

    def test_stop(self,test_plan):
        """ stop the producing test by test plan
        @param test_plan: test plan name
        @type test_plan: string
        @rtype: True/False
        @return: If success,return False.Else,return True.
        B{Example:}
          - C{test_stop("stability-m812")}
        """
        # TO DO!!
        testplan_id = 1
        self.test_plan = test_plan
        self.testplan_statu["testplan_id"] = "IsStopped"
        return self.testplan_status["testplan_id"]

    def show_test_status(self,plan_id):
        """ show test status by test plan name
        @param plan_id: test plan id
        @type plan_id: string
        @rtype: True/False
        @return: If success,return False.Else,return True.
        B{Example:}
          - C{show_test_status("stability-m812")}
        """
        return self._test_status_display(plan_id)

    def show_device_status(self):
        """ show devices status
        @rtype: A Dict that contains the devices id and each device's status("Running"/""Idle") on this host
        @return: If success,return A Dict.Else,return [].
        B{Example:}
          - C{show_test_status("stability-m812")}
        """
        return self._device_status_display()

    def show_device(self):
        """ show devices and it's property
        @rtype: A Dict that contains the devices id and each device's property on this host
        @return: If success,return A Dict.Else,return [].
        B{Example:}
          - C{show_device()}
        """
        print "show_device"
        return self._show_device()

    def show_report(self,plan_id):
        """ show report by test plan id
        @rtype: A Dict that contains the test report on the host
        @return: If success,return A Dict.Else,return [].
        B{Example:}
          - C{show_report("Stability")}
        """
        return self._get_test_report(plan_id)
    
    def all_report_display(self):
        """Get TAT testData.xml by each devices
        @rtype: A Dict that contains the test report on the host
        @return: If success,return A Dict.Else,return [].
        B{Example:}
          - C{all_report_display("Stability")}
        """
        testdata = {}
        for device in self.devices:
            try:
                testdata.update({"%s_%s"%(device,self.property[device]["product"]):self.test_data.get_latest(device)})
            except:
                continue
        return testdata

    def device_report_display(self,device_id):
        """Get TAT testData.xml by device id
        @param device_id: device id
        @type device_id: string
        @rtype: A Dict that contains the test report on the host
        @return: If success,return A Dict.Else,return [].
        B{Example:}
          - C{device_report_display("8bf5fss_M812C")}
        """
        print "device_report_display, device:%s"%device_id
        print {device_id:self.test_data.get_latest(device_id.split("_")[0])}
        return {device_id:self.test_data.get_latest(device_id.split("_")[0])}

    def open_file(self,file):
        """Open file
        @param file: file name
        @type file: string
        @return: file binary stream.
        B{Example:}
          - C{open_file("testplan.xml")}
        """
        return xmlrpclib.Binary(open(file,'rb').read())

class Interface():
    """register the XML-PRC function,called by client"""
    @staticmethod
    def hello_2_server(device_id,product_name):
        """hello 2 server,trigger by other tools,such as TAT Client/MONKEY
        @param device_id: ADB DEVICES ID
        @type device_id: string
        @param product_name: product name
        @type product_name: string
        @rtype: True/False
        @return: If success,return False.Else,return True.
        B{Example:}
          - C{hello_2_server("8bf5f7f",""M812)}
        """
        return RpcServer.GetInstance()._device_hello(device_id,product_name)
    @staticmethod
    def send_report_2_server(plan,report):
        """send test report to server by other tools,such as TAT Client/MONKEY
        @param report: test report
        @type report: string
        @rtype: True/False
        @return: If success,return False.Else,return True.
        B{Example:}
          - C{send_report_2_server(report)}
        """
        return RpcServer.GetInstance()._send_report(plan,report)
    @staticmethod
    def sync_status_2_server(device_status):
        """sync status to server to server by other tools,such as TAT Client/MONKEY
        @param device_status: device statis
        @type device_status: dict
        @rtype: True/False
        @return: If success,return False.Else,return True.
        B{Example:}
          - C{sync_status_2_server({"devices":"Running})}
        """
        return RpcServer.GetInstance()._sync_client_status(device_status)
    @staticmethod
    def report_finish(name,state):
        """report_finish
        @param name: test plan name
        @type name: string
        @param state: plan state
        @type state: 0/1/2     start/finish/error
        @rtype: True/False
        @return: If success,return False.Else,return True.
        B{Example:}
          - C{sync_status_2_server({"devices":"Running})}
        """

        print "report_finish ------ plan:%s state:%s"%(name,state)
        return 2
    @staticmethod
    def test_report(name,state):
        """test_report
        @param name: test plan name
        @type name: string
        @param state: plan state
        @type string: Finished/Error/Start
        @rtype: True/False
        @return: If success,return False.Else,return True.
        B{Example:}
          - C{sync_status_2_server({"devices":"Running})}
        """
        print "test_report ------ plan:%s state:%s"%(name,state)
        return RpcServer.GetInstance()._send_report(name,state)

    def main(self):
        at_server = RpcServer()
        at_server._register_object(Interface)
        at_server._start()



def main(argv=None):
    '''Command line options.'''

    def check_ip(ipaddr):
            #print addr
            for item in (ipaddr.strip().split('.') ):
                if ((str(item).isdigit() != True) or (int(item)>255 or int(item)<0)):
                    #print "check ip address failed!,Input Valid ip address(such as 127.0.0.1) or whole url rpc address"
                    return False
            return True

    program_name = os.path.basename(sys.argv[0])
    program_version = "v1"
    program_build_date = "%s" % __updated__

    program_version_string = '%%prog %s (%s)' % (program_version, program_build_date)

    program_usage = '''orange [-d \"tatpath.\"] [-i \"serverip.\"] [-p \"port.\"] [-a \"auto.\"] '''

    program_longdesc = '''This is a TAT Client RPC-Server!Connect to TAT web server,and register XML-RPC Instance/Function'''
    program_license = "Copyright 2014 TCL(Ningbo) VAL-Performance Team"

    if argv is None:
        argv = sys.argv[1:]
    try:
        # setup option parser
        parser = OptionParser(version=program_version_string, epilog=program_longdesc, description=program_license,usage = program_usage)
        parser.add_option("-d", "--dir", dest="tatpath",help="tool path. default is '../plan/'")
        parser.add_option("-i", "--ip", dest="serverip",help="web server RPC-SERVER url,Input Valid ip address(such as 127.0.0.1) or whole url rpc address, type 'localhost' if you want to connect to local web server")
        parser.add_option("-p", "--port", dest="port",help="The RPC-Server LISTENING port. default is:8000")
        parser.add_option("-a", "--auto", dest="auto",action="store_true",default = False,help="client will auto-leave if this option is choosed. default is: False")
        # set defaults
        parser.set_defaults(tatpath="..", serverip="https://172.16.11.195:8000/tatserver/rpc/call/xmlrpc",port = 8000)

        # process options
        (opts, args) = parser.parse_args(argv)

        if opts.serverip is not None:
            if opts.serverip == "localhost":
                opts.serverip = "http://127.0.0.1:8000/tatserver/rpc/call/xmlrpc"
            elif check_ip(opts.serverip):
                opts.serverip = "http://%s:%s/tatserver/rpc/call/xmlrpc"%(opts.serverip,opts.port)
        if opts.tatpath is None:
            tat_path = os.environ["TAT_PATH"]
            if tat_path != None:
                opts.tatpath = tat_path
    except Exception, e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return False

    at_server = RpcServer(opts.port,opts.serverip,opts.tatpath,opts.auto)
    at_server._register_object(Interface)
    at_server._start()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        RpcServer.GetInstance().__del__()

