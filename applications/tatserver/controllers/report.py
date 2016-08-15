# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

from ReportParser import Report,time_2_second,second_2_time

def index():
    response.flash = T("Welcome to TAT Server!")
    return dict(message=T('Hello World'))

def _dict2db(name,time,report):
    db.report.update_or_insert(plan_name=name,begin_time=time)
    raw = db((db.report.plan_name==name)&(db.report.begin_time==time)).select().first()
    if None == raw:
        raise HTTP(400, "<h1>Record not finded,may deleted by others.<a href=\"%s\"><br/>Go back homepage</h1>"%(URL("show_plan")))
    for d,status in report.items():
        raw.update_record(device = d,sw = status["sw"],mtbf = status['runtime'])
        for name in sorted(status['status'].keys()):
            db.report_status.update_or_insert(report_id = raw.id,case = name.split("_")[-1],passrate = status['status'][name]["passrate"] ,looptime = status['status'][name]["avgtime"])

def _get_from_db(name,time,sw):
    report = {}
    # 1. find report in db
    db_report = db((db.report.name == name) & (db.report.datetime == time) & (db.report.sw == sw)).select().first()
    if None != db_report:
        report.update(eval(db_report.report))
    return report

def report_hander(report_data):
    report = {}
    data = report_data["data"]
    if data != ''and data != None:
        cases = Report(data).parser()
        report["status"] = cases.case
        report["runtime"] = cases.mtbf
    return report

def log_hander(log,plan):
    db_dict = {}
    db_dict["except"] = log
    if (log!=""):
        db_dict["except"] = log
        db_log = db((db.reportlog.name == plan.plan_name) & (db.reportlog.sw == plan.sw)& (db.reportlog.begin_time == plan.begin_time)).select().first()
        if None != db_log:
            db_log.update_record(log_breif=log[1])
        else:
            db.reportlog.insert(name = plan.plan_name,sw = plan.sw,begin_time = plan.begin_time,log_breif=log[1])
    return db_dict

def get_report(plan):
    report = {}
    db_report = report_from_db(plan)
    # 1. find report in db
    if plan.status != "running" and plan.status != "idle" and  plan.status != "pendding":
        return db_report
    #2. get report from client
    if None!=plan.devices:
        for device_id in plan.devices:
            devices = db(db.device.name == device_id).select().first()
            if devices!=None:
                if devices.client.workstation == True:
                    try:
                        for device, report_data in db_rpc.show_report_by_device(devices.client.url, devices.name).items():
                        # for device, test_data in db_rpc.show_all_report(url).items():
                            data = report_data["data"]
                            log = report_data["log"]
                            if data != ''and data != None:
                                cases = Report(data)
                                report[device] = cases.parse2dict()
                                #device report
                                device_report = device_report_from_db(db_report.id,device)
                                # device_report.update_record(test_type=cases.type,mtbf = cases.mtbf,status = cases.status)
                                device_report.update_record(test_type=cases.type,mtbf = cases.mtbf) #status = cases.status
                                #case report
                                for name in cases.case:
                                    case_report = case_report_from_db(db_report.id,device_report.name,name)
                                    case_report.update_record(run_time = cases.case[name]["runtime"],passrate = cases.case[name]["passrate"]
                                                              ,avgtime = cases.case[name]["avgtime"],)
                                    #devices defects
                                    cases_defects_from_db(plan,name)
                                if (log!=""):
                                    db_log = db(db.report_log.device_report == device_report.id).select().first()
                                    if None != db_log:
                                        db_log.update_record(title = log[0],brief=log[1])
                                    else:
                                        db.report_log.insert(device_report = device_report.id,title = log[0],brief=log[1])
                                    #devices defects
                                    mod = re.findall(r"(.*)_.*", str(log[0]),re.I);
                                    mod = mod[0] if mod else str(log[0])
                                    mod_report = db((db.case_report.report == db_report.id)&(db.case_report.case_name.like(mod+"%"))).select().first()
                                    if mod_report:
                                        if mod_report.status==None or mod_report.status.lower() not in ["anr","crash","android reboot","error","androidreboot"]:
                                            status = str(log[0]).split("_")[-1]
                                            mod_report.update_record(status = "Android reboot" if status == "AndroidReboot" else status)
                                            case_defect = cases_defects_from_db(plan,mod)
                                            if case_defect:
                                                counts = case_defect.counts+1
                                                case_defect.update_record(counts = counts)
                    except:
                        continue
    db_report.update_record(report = report)
    return db_report

def current():
    plan = db.test_plan[request.args(0,cast=int)] or redirect(URL('index'))
    report = get_report(plan)
    if report == None:
        session.flash=T("No Report Found!")
        redirect(URL("plan","show"))
    devices,mtbf,status_span,logs,resaults = report_analysis(plan,report)
    #message = "<html><li>The target is <strong> level%s. %s ( 5 devices )</strong> </li>"%(plan.std_level.levels,plan.std_level.description) if plan.std_level else "NA"
    #message+= "<ul><li> Pass Rate for every module SHOULD > 95%</li><li>Valid MTBF for single DUT(Device Under Test) MUST>=40H</li></ul>"
    #message+= "<li><strong>The actual MTBF</strong> is %s</li>"%mtbf
    #message+= "One devices just:%s"%report.status if report.status!=None else ""
    #message+="%s </html>"%A('Details see',_href=URL(args=plan.id,scheme=True, host=True))
    #send_email(to=plan.created_by.email,sender=auth.user.email,
    #send_email(to="valeera@foxmail.com",sender=auth.user.email,
    #  subject="Automation report plan: %s" % plan.plan_name,
    #  message=message)

    #send_report_by_email(plan,report)
    return locals()

def show():
    response.view = "report/current.html"
    plan = db.test_plan[request.args(0,cast=int)] or redirect(URL('index'))
    report = db.report[request.args(1,cast=int)] or redirect(URL('index'))
    devices,mtbf,status_span,logs,resaults = report_analysis(plan,report)
    return locals()

import json
def case_analysis(reports):
    case_report = {}
    swdict = {}
    for report in reports:
        cases = db(db.case_report.report == report.id).select()
        case_report[report.sw] = {}
        for case in cases:
            case_report[report.sw][case.case_name] =case_report[report.sw][case.case_name]+ time_2_second(case.run_time) if case_report[report.sw].has_key(case.case_name) else time_2_second(case.run_time)
            #if case.status.lower() in ["anr","crash","Android reboot","error"]:
    for cases in case_report.values():
        for k,v in cases.items():
            cases[k] = second_2_time(v)
    return json.dumps(case_report)

def case_pareto(plan):
    pareto = []
    for item in db(db.case_defects.test_plan == plan.id).select():
        pareto.append({"label":item.name,"value":str(item.counts)})
    return pareto

def history():
    plan = db.test_plan[request.args(0,cast=int)] or redirect(URL('index'))
    reports = db(db.report.name == plan.plan_name).select(groupby=db.report.sw) #get last report each sw
    status_span = []
    history_sw = ""
    history_data = ""
    history_color = ""
    for report in reports:
        for name in db(db.case_report.report == report.id).select(groupby=db.case_report.case_name,orderby=db.case_report.case_name):
            status_span.append(name.case_name) if name.case_name not in status_span else "Nothing"
        # history_sw+= str(A(report.sw,_href=URL('report','show',args=[report.id,report.sw,report.datetime])))+","
        history_sw+= report.sw+","
        history_data+=str(time_2_second(report.mtbf)/3600)+","
        if report.results:
            history_color+="#00FF00," if report.results == "pass" else "#FF0000,"
        else:
            history_color+="#FFFF00,"
        cases = db(db.case_report.report == report.id).select()
    case_report = case_analysis(reports)
    pareto = case_pareto(plan)
    return locals()

def pareto():
    plan = db.test_plan[request.args(0,cast=int)] or redirect(URL('index'))
    pareto = case_pareto(plan)
    return locals()

def fetch_log():
    plan_name = request.args[1]
    sw = request.args[2]
    begin_time = datetime.strptime(request.args[3],'%Y-%m-%d_%H_%M_%S')
    filename = request.args[4]
    device_report = db.device_report[request.args(0,cast=int)] or redirect(URL('index'))
    #device = db(db.device.name == device_report.name).select().first()
    device = db(db.device.name.like(str(device_report.name)+"%")).select().first()
    db_log = db(db.report_log.device_report == request.args(0,cast=int)).select().first()
    if None == db_log or None == device:
        raise HTTP(400, "<h1>Record not finded,may deleted by others.<a href=\"%s\"><br/>Go back homepage|<a href=\"%s\">Edit Test Plan</h1>"%(URL("index"),(URL("index"))))
    else:
        if db_log.log_file==None:
            logfile = dbfile.get_log(device.client.url,plan_name,sw,begin_time,device.name,filename)
            with open(os.path.abspath(logfile),"rb") as f:
                file = db.report_log.log_file.store(f,os.path.basename(device.name+logfile))
                db_log.update_record(log_file=file)
    return dict(form = db_log)


def fetch_log_bk():
    deviceid = request.args[0]
    plan_name = request.args[1]
    sw = request.args[2]
    begin_time = datetime.strptime(request.args[3],'%Y-%m-%d_%H_%M_%S')
    filename = request.args[4]
    device = db(db.device.name == deviceid).select().first()
    if None == device:
        raise HTTP(400, "<h1>Record not finded,may deleted by others.<a href=\"%s\"><br/>Go back homepage|<a href=\"%s\">Edit Test Plan</h1>"%(URL("index"),(URL("index"))))
    else:
        url = device.host_name.url
        logfile = dbfile.get_log(url,plan_name,sw,begin_time,deviceid,filename)
    f = open(os.path.abspath(logfile),"rb")
    file = db.reportlog.log_file.store(f,filename)
    db_reportlog = db((db.reportlog.name == plan_name) & (db.reportlog.sw == sw)).select().first()
    if None != db_reportlog:
        db_reportlog.update_record(log_file=file)
    else:
        db.reportlog.insert(name = plan_name,sw = sw,begin_time = begin_time,log_file=file,log_breif="NA")

    db_reportlog = db((db.reportlog.name == plan_name) & (db.reportlog.sw == sw)).select().first()
    f.close()
    return dict(form = db_reportlog)


# def _sendEmail(tester,title,content):
#     if tester=='':
#         pass
#     else:
#         os.system('echo \"'+content+'\" |mail -s \"' + title + '\" ' + tester)
#
# def mailto():
#     report = request.args[0]
#
#     plan = request.args[1]
#     # mail.send('Zhuo.li@tcl.com',
#     #       'Message subject',
#     #       'Plain text body of the message')
#     _sendEmail("tat web server","test","text")
#     return dict(report =type(report),plan = type(plan))



@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login() 
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)

def one():
    return dict()

def echo():
    return request.vars.name
