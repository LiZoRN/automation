
import codecs
import re
import os
from xml.dom import  minidom
from datetime import datetime
from xmlrpclib import ServerProxy,Fault
from urlparse import urlparse

plan_path = r"/home/valeera/src/test/data/tat/"
UNHANDLED = 100
ACCESS_DENIED = 200
'''
def gen_plan(path,planname,sw,begin_time,script,runcircle,mDevices,sDevices=""):

    impl = minidom.getDOMImplementation()
    dom = impl.createDocument(None, 'Config', None)
    root = dom.documentElement

    planE=dom.createElement('PLAN')
    planT=dom.createTextNode(planname)
    planE.appendChild(planT)
    root.appendChild(planE)

    scriptE=dom.createElement('Script')
    scriptT=dom.createTextNode(str(script))
    scriptE.appendChild(scriptT)
    root.appendChild(scriptE)

    runCircleE =dom.createElement('RunCircle')
    runCircleT=dom.createTextNode(str(runcircle))
    runCircleE.appendChild(runCircleT)
    root.appendChild(runCircleE)

    mDeviceE =dom.createElement('M-Device')
    mDeviceT=dom.createTextNode(mDevices)
    mDeviceE.appendChild(mDeviceT)
    root.appendChild(mDeviceE)
    # mDeviceE =dom.createElement('M-Device')
    # for device in mDevices:
    #     deviceIdE = dom.createElement("id")
    #     deviceIdT=dom.createTextNode(device)
    #     deviceIdE.appendChild(deviceIdT)
    #     mDeviceE.appendChild(deviceIdE)
    # root.appendChild(mDeviceE)
    sDeviceE =dom.createElement('S-Device')
    sDeviceT=dom.createTextNode(sDevices)
    sDeviceE.appendChild(sDeviceT)
    root.appendChild(sDeviceE)
    #for i in script:
        #scriptE=dom.createElement('script')
        #scriptT=dom.createTextNode(i)
        #scriptE.appendChild(scriptT)
        #root.appendChild(scriptE)
#         os.system('mkdir /data/TAT/ClientName/' + clientname + ' >/dev/null 2>&1')
#         os.system('touch /data/TAT/ClientName/' + clientname +'/currentpath.xml >/dev/null 2>&1')
#         f= open('/data/TAT/ClientName/' + clientname+ '/currentpath.xml', 'w')
#     dir = os.path.join(path,planname,sw,datetime.strftime(begin_time,'%Y%m%d%H%M%S'))
    # dir = os.path.join(path,planname,begin_time)
    dir = os.path.join(path,planname,sw,begin_time.replace("-", "").replace(":", "").replace(" ", ""))
    if not os.path.exists(dir):
        os.makedirs(dir)
    f= open(os.path.join(dir,"%s_testplan.xml"%(mDevices)), 'w')
    dom.writexml(f,'\n',encoding='utf-8')
    f.close()
    # return {mDevices:open(os.path.join(dir,"%s_testplan.xml"%(mDevices)), 'r').read()}
    return {mDevices:dom.toxml('UTF-8')}
'''

def gen_plan(planname,script,runcircle,mDevices,sDevices=""):
    impl = minidom.getDOMImplementation()
    dom = impl.createDocument(None, 'Config', None)
    root = dom.documentElement

    planE=dom.createElement('PLAN')
    planT=dom.createTextNode(planname)
    planE.appendChild(planT)
    root.appendChild(planE)

    scriptE=dom.createElement('Script')
    scriptT=dom.createTextNode(str(script))
    scriptE.appendChild(scriptT)
    root.appendChild(scriptE)

    runCircleE =dom.createElement('RunCircle')
    runCircleT=dom.createTextNode(str(runcircle))
    runCircleE.appendChild(runCircleT)
    root.appendChild(runCircleE)

    mDeviceE =dom.createElement('M-Device')
    mDeviceT=dom.createTextNode(mDevices)
    mDeviceE.appendChild(mDeviceT)
    root.appendChild(mDeviceE)

    sDeviceE =dom.createElement('S-Device')
    sDeviceT=dom.createTextNode(sDevices)
    sDeviceE.appendChild(sDeviceT)
    root.appendChild(sDeviceE)
    return {mDevices:dom.toxml('UTF-8')}

class UnhandledQuery(Fault):
    '''
    that's show can't handle the query exception
    '''
    def __init__(self,message="Couldn't handle the query"):
        Fault.__init__(self, UNHANDLED, message)

class AccessDenied(Fault):
    '''
    when user try to access the forbiden resources raise exception
    '''
    def __init__(self, message="Access denied"):
        Fault.__init__(self, ACCESS_DENIED, message)

def inside(dir,name):
    '''
    check the dir that user defined is contain the filename the user given
    '''
    dir = os.path.abspath(dir)
    name = os.path.abspath(name)
    return name.startswith(os.path.join(dir,''))

def getPort(url):
    '''
    get the port num from the url
    '''
    name = urlparse(url)[1]
    parts = name.split(':')
    return int(parts[-1])


class LogNode:
    def __init__(self, url, planname,sw,datetime,deviceid):
        self.dirname = os.path.join(plan_path,"plan",planname,sw,datetime,"logs")
        self.url = url
        self.deviceid = deviceid
        if not os.path.exists(self.dirname):
            os.makedirs(self.dirname)

    def query(self, query):
        try:
            return self._handle(query)
        except AccessDenied:
            return self._rpcfile(query)

    def fetch(self, query):
        return self.query(query)

    def _handle(self, query):
        name = os.path.join(self.dirname, query)
        if not os.path.isfile(name) or not inside(self.dirname, name):
            raise AccessDenied
        return name

    def _rpcfile(self,query):
        s = ServerProxy(self.url)
        f = open(os.path.join(self.dirname, query),'wb')
        f.write(s.fetch_log(self.deviceid).data)
        f.close()
        return os.path.join(self.dirname, query)

class DbFile:
    def __init__(self,dir = "/data/tat/"):
        
        self.data_path = dir
        self.plan_path  = os.path.join(self.data_path,"plan")
        
    def _save2file(self,name,data):
        f = codecs.open(os.path.join(self.data_path,name), 'wb')
        f.write(data)
        f.close()

    def gen_plan(self,row):
        plan_dict = {}
        for device in row.devices:
            #plan_dict.update(gen_plan(self.plan_path,raw.plan_name,raw.sw,raw.begin_time,raw.test_case,raw.runcircle,device))
            plan_dict.update(gen_plan(row.plan_name,row.test_case,row.runcircle,device))
        return plan_dict

    def get_plan(self,name,time):
        try:
            return open(os.path.join(self.plan_path,name,datetime.strftime(time,'%Y%m%d%H%M%S'),"testplan.xml")).read()
        except:
            return None

    def store_report(self,name,time,device,data):
        plan_path = os.path.join(self.plan_path,name,datetime.strftime(time,'%Y%m%d%H%M%S'),"report")
        if not os.path.exists(os.path.join(plan_path)):
            os.makedirs(plan_path)
        self._save2file(os.path.join(plan_path,"%s_testdata.xml"%device),data)

    def get_report(self,name,time):
        report = {}
        root = os.path.join(self.plan_path,name,datetime.strftime(time,'%Y%m%d%H%M%S'),"report")
        try:
            for i in os.listdir(root):
                try:
                    if os.path.isfile(os.path.join(root,i)):
                        report[re.findall("(.*)_testdata\.xml",i)[0]] = open(os.path.join(root,i)).read()
                except:
                    continue
        except:
            pass
        return report

    def history_report(self,name,start,end):
        pass

    def get_log(self,url,planname,sw,time,deviceid,filename):
        lognode = LogNode(url, planname,sw,datetime.strftime(time,'%Y%m%d%H%M%S'),deviceid)
        return lognode.fetch("%s_%s.zip"%(deviceid,filename))

dbfile = DbFile(plan_path)