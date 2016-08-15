# -*- coding: utf-8 -*-

#########################################################################
"""service XML-RPC registered"""
#########################################################################

service = Service()
import ReportParser

def stability_report_process(device,plan,report):
    db_report = report_from_rpc(plan)
    if device in [d.split("_")[0] for d in plan.devices]:
        device_report = device_report_from_db(db_report.id,device)
        # device_report.update_record(test_type=cases.type,mtbf = cases.mtbf,status = cases.status)
        if device_report.status not in ["Anr","Crash","Android reboot","Error"] or report.status not in ["Anr","Crash","Android reboot","Error"]:
            device_report.update_record(test_type=report.type,mtbf = report.mtbf,status = report.status)
            #case report
            for name in report.case:
                case_report = case_report_from_db(db_report.id,device_report.name,name)
                case_report.update_record(run_time = report.case[name]["runtime"],passrate = report.case[name]["passrate"]
                                          ,avgtime = report.case[name]["avgtime"])
                cases_defects_from_db(plan,name)
    return db_report,device_report

@service.xmlrpc
def test_report(sender,test_data):
    """test report
    @param sender: device
    @type    sender: string
    @param test_data: client host name
    @type    test_data: string
    @rtype: True/False
    @return: If success,return False.Else,return True.
    B{Example:}
      - C{test_report(deviceid-pruductname,test_data"")}
    """
    # TO DO!!
    report = ReportParser.Report(test_data)
    report.parser()
    plan = db(db.test_plan.plan_name == report.name).select().first()
    if plan!=None:
        db_report,device_report = plan,stability_report_process(sender,plan,report)
        #send_report_by_email(plan,db_report,device_report)
    return True

@service.xmlrpc
def report(sender,test_data):
    """report
    @param sender: device/cline.or any others
    @type    sender: string
    @param test_data: the raw of xml file
    @type    test_data: string
    @rtype: True/False
    @return: If success,return False.Else,return True.
    B{Example:}
      - C{report(deviceid-pruductname,test_data"")}
    """
    # TO DO!!
    report = ReportParser.report(test_data)
    report.parser()
    report.dump()
    plan = db(db.test_plan.plan_name == report.name).select().first()
    print plan
    #report = get_report(plan)
    #devices,mtbf,status_span,logs = report_analysis(plan,report)
    return True

@service.xmlrpc
def sync_client_status(sender,devices_status):
    """sync client status
    @param sender: devices id
    @type    sender: string
    @param devices_status: client host name
    @type    devices_status: string -- "IsRunning" or "Idle"
    @rtype: True/False
    @return: If success,return False.Else,return True.
    B{Example:}
      - C{sync_client_status("8bf5f7f-M812"."IsRunning".,"")}
    """
    # TO DO!!
    return True

@service.xmlrpc
def host_hello(sender,url):
    """Client Online report
    @param sender: client host name
    @type    sender: string
    @param url: ip:port
    @type    url: string
    @rtype: True/False
    @return: If success,return False.Else,return True.
    B{Example:}
      - C{host_hello(socket.gethostname(),"http://127.0.0.1:8000")}
    """
    print sender
    raw = db(db.client.name == sender).select().first()
    if None == raw:
        db.client.update_or_insert(name = sender,url = url)
    else:
        raw.update_record(url = url)
    return True

@service.xmlrpc
def host_leave(sender):
    """Client Leave
    @param sender: client host name
    @type    sender: string
    @rtype: True/False
    @return: If success,return False.Else,return True.
    B{Example:}
      - C{host_leave(socket.gethostname(),"")}
    """
    db(db.device.host_name == db(db.client.name==sender).select().first().id).delete()
    db(db.client.name==sender).delete()
    return True

@service.xmlrpc
def device_hello(sender,device_id,product_name):
    """Device  detect
    @param sender: client host name
    @type sender: string
    @param device_id: device_id used by adb
    @type device_id: string
    @param product_name: product name
    @type product_name: string
    @rtype: True/False
    @return: If success,return False.Else,return True.
    B{Example:}
      - C{device_hello(socket.gethostname(),"8bf5f7f","M812")}
    """
    db.device.update_or_inser(client_name = sender,device_id = device_id,product_name = product_name)
    return True

@service.xmlrpc
def open_file(file):
    """Open server file by client
    @param file: file addr
    @type file: string
    @return: file binary stream.
    B{Example:}
      - C{open_file("testplan.xml")}
    """
    with open(file,'rb') as handle:
        return xmlrpclib.Binary(handle.read())


@service.xmlrpc
def get_plan_status(plan_name):
    """Open server file by client
    @param file: file addr
    @type file: string
    @return: file binary stream.
    B{Example:}
      - C{open_file("testplan.xml")}
    """
    row = db((db.test_plan.plan_name == plan_name)).select().first()
    return dbfile.gen_plan(row) if row!=None else {}

@service.xmlrpc
def get_project_dnd_config(name,sw):
    """get plan project dnd config file for user_debug only
    @param name: project name
    @type sw: project sw
    @return: file binary stream.
    B{Example:}
      - C{open_file("testplan.xml")}
    """
    try:
        with open(proj.get_user_debug_config(name,sw),'rb') as handle:
            return xmlrpclib.Binary(handle.read())
    except:
        return False


@service.xmlrpc
def report_meminfo(plan_name,device,data):
    """Open server file by client
    @param file: file addr
    @type file: string
    @return: file binary stream.
    B{Example:}
      - C{open_file("testplan.xml")}
    """
    query = (db.test_plan.status == 'running')&(db.test_plan.plan_name == plan_name)
    plan = db(query).select().first()
    if plan==None:
        return False
    db_report = report_from_rpc(plan)
    if device in [d.split("_")[0] for d in plan.devices]:
        device_report = device_report_from_db(db_report.id,device)
        db_meminfo = meminfo_report_from_db(device_report.id)
        db_meminfo.update_record(memory_data = data)
        print db_meminfo

    return True


def call():
    """exposes all registered services, including XML-RPC"""
    return service()
