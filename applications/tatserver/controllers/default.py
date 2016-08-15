# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - api is an example of Hypermedia API support and access control
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Welcome to TAT Server!")
    return dict(message=T('Hello World'))


def new_client():
    form = SQLFORM(db.client)
    if form.accepts(request.post_vars,session):
        session.flash = 'client created ok'
        redirect(URL('show_clients'))
    Message ="New Client"
    return dict(form=form,message=Message)

def delete_client():
    """delete an existing client"""
    row = db.client[request.args(0)]
    form = SQLFORM(db.client, row, deletable=True,showid=False)
    if form.process().accepted:
        response.flash = 'record delete'
        redirect(URL('show_clients'))
    return dict(form=form)

def edit_client():
     """edit an existing client"""
     this_page = db.client(request.args(0,cast=int)) or redirect(URL('index'))
     form = SQLFORM(db.client, this_page, deletable=True,showid=False).process(
         next = URL('show_clients',args=request.args))
     return dict(form=form)

def show_clients():
    list_client = db(db.client).select()
    return dict(list_client =list_client)

def show_client():
    client = db.client(request.args(0,cast=int)) or redirect(URL('index'))
    return dict(client =client)

def new_device():
    form = SQLFORM(db.device)
    if form.accepts(request.post_vars,session):
        session.flash = 'client created ok'
        redirect(URL('show_clients'))
    Message ="New Client"
    return dict(form=form,message=Message)

def edit_device():
    """delete an existing client"""
    row = db.device[request.args(0,cast=int)]
    form = SQLFORM(db.device, row, deletable=True,showid=False,readonly=False)
    if form.process().accepted:
        response.flash = 'record delete'
        redirect(URL('show_all_devices'))
    return dict(form=form)

def flush_all_devices():
    list_client = db(db.client).select()
    devices = {}
    for client in list_client:
        try:
            for device,detail in db_rpc.show_device(client.url).items():
                device_id = device+"_"+detail["product"]
                raw = db(db.device.name==device_id).select().first()
                if None != raw:
                    db.raw.update_record(display_id = detail["display_id"],
                                           build_date = detail["build_date"],product = detail["product"],
                                           region = detail["region"],hardware = detail["hardware"],
                                           build_type = detail["build_type"],host_name = client.id,build_version =detail["version"] )
                else:
                    db.device.update_or_insert(name = device_id,display_id = detail["display_id"],
                                           build_date = detail["build_date"],product = detail["product"],
                                           region = detail["region"],hardware = detail["hardware"],
                                           build_type = detail["build_type"],host_name = client.id,build_version =detail["version"] )
        except:
            continue
    redirect(URL('show_all_devices'))
    Message ="Flush all devices Success!"
    return dict(message=Message)

def flush_device():
    client = db.client(request.args(0,cast=int)) or redirect(URL('index'))
    if None == client:
        raise HTTP(400, "<h1>Client not finded,may deleted by others.<a href=\"%s\"><br/>Go back homepage</h1>"%(URL("index")))
    try:
        #delete the old device on this host?
        db(db.device.host_name == client.id).delete()
        for device,detail in db_rpc.show_device(client.url).items():
            device_id = device+"_"+detail["product"]
            #add the new device on this host
            raw = db(db.device.name==device_id).select().first()
            if None != raw:
                db.raw.update_record(display_id = detail["display_id"],
                                       build_date = detail["build_date"],product = detail["product"],
                                       region = detail["region"],hardware = detail["hardware"],
                                       build_type = detail["build_type"],host_name = client.id,build_version =detail["version"] )
            else:
                db.device.update_or_insert(name = device_id,display_id = detail["display_id"],
                                       build_date = detail["build_date"],product = detail["product"],
                                       region = detail["region"],hardware = detail["hardware"],
                                       build_type = detail["build_type"],host_name = client.id,build_version =detail["version"] )
            response.flash = T("Flush Devices Success!")
    except:
        response.flash = T("Flush Devices FAILED!")
    redirect(URL('show_all_devices'))
    Message ="Flush all devices Success!"
    return dict(message=Message)

def show_all_devices():
    list_devices = db(db.device).select()
    return dict(list_device =list_devices)

def show_device_status():
    list_devices = db(db.device_status).select()
    return dict(list_devices =list_devices)

def show_device():
    list_device = db(db.device.host_name==request.args[0]).select()
    if None == list_device:
        raise HTTP(400, "<h1>Record not finded,may deleted by others.<a href=\"%s\"><br/>Go back homepage</h1>"%(URL("index")))
    return dict(list_device = list_device)

def device_cfg():
    return dict(device = db.device[request.args(0,cast=int)])


def del_device():

    return dict()


def devices_filter(plan = None):
    devices = {}
    if plan!=None:
        plan_row = db((db.test_plan.status != 'Finished')|(db.test_plan.status != 'AdminFinished')|(db.test_plan.id != plan.id)).select()
    else:
        plan_row = db((db.test_plan.status != 'Finished')|(db.test_plan.status != 'AdminFinished')).select()
    for device in  db(db.device).select():
        devices.update({device.id:device.name})
        if plan_row!=None:
            for row in plan_row:
                if row.display_devices!= None:
                    if device.name in row.display_devices:
                        devices.pop(device.id)
    return devices

from xml_parse import xml
def new_plan():
    """ a simple entry form with various types of objects """
    tool_ver = ["1.2.0","1.1.0"]
    mdevices = devices_filter().values()
    sdevices = devices_filter().values()
    scripts = script.get_svn_tag()
    form = FORM(TABLE(
        TR('Plan Name:', INPUT(_type='text', _name='plan_name',requires=IS_NOT_EMPTY())),
        TR('Test script:',  SELECT(scripts.keys(), _name='TestScript_Tag')),
        TR('Tool Version:',  SELECT(tool_ver, _name='tool')),
        TR('mDevices:',  SELECT(mdevices, _name='display_devices',_multiple="multiple")),
        TR('sDevices:',  SELECT(sdevices, _name='sdevices',_multiple="multiple")),
        TR('Begin Time:',  INPUT(_type='text',_class = 'datetime',_name='begin_time')),
        TR('Tester:', INPUT(_type='text', _name='tester')),
        TR('SW Version:', INPUT(_type='text', _name='sw')),
        TR('runcircle:', INPUT(_type='text', _name='runcircle')),
        TR('', INPUT(_type='submit', _value='SUBMIT')),
    ))
    if form.process().accepted:
        devices_id = []
        for device in form.vars.display_devices:
            temp = db(db.device.name == device).select().first()
            if None != temp:
                devices_id.append(temp.id)
        row = db((db.test_plan.plan_name == form.vars.plan_name)).select().first()
        if row == None:
            db.test_plan.update_or_insert(plan_name = form.vars.plan_name,TestScript_Tag = form.vars.TestScript_Tag,
                                          begin_time = form.vars.begin_time,tester = form.vars.tester,
                                          sw = form.vars.sw ,display_devices =form.vars.display_devices,tool_ver = form.vars.tool)
        for device,plan in dbfile.gen_plan(form.vars).items():
            db_rpc.test_start(db(db.device.name == device).select().first().host_name.url,plan)
        response.flash = 'record inserted'
        redirect(URL('show_plan'))
    elif form.errors:
        response.flash = 'form is invalid'
    else:
        response.flash = 'please fill the form'
    return dict(form=form, vars=form.vars,scripts = scripts)

import time
def start_plan():
    """delete an existing client"""
    devices = []
    row = db.test_plan[request.args(0,cast=int)]
    if None == row:
        raise HTTP(400, "<h1>Record not finded,may deleted by others.<a href=\"%s\"><br/>Go back homepage</h1>"%(URL("show_plan")))
    for id in row.display_devices:
        if None!=db(db.device.name==id).select().first():
            devices.append(id)
    row.update_record(status = "Running",display_devices = devices,begin_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    for device,plan in dbfile.gen_plan(row).items():
        db_rpc.test_start(db(db.device.name == device).select().first().host_name.url,plan)

    message = "Test Plan Start"
    redirect(URL('show_plan'))
    return dict(message=message)

def stop_plan():
    """delete an existing client"""
    row = db.test_plan[request.args(0,cast=int)]
    if None == row:
        raise HTTP(400, "<h1>Record not finded,may deleted by others.<a href=\"%s\"><br/>Go back homepage</h1>"%(URL("show_plan")))
    if row.status != "Running":
        message = "Test Plan IsStoped"
        redirect(URL('show_plan'))
    row.update_record(status = "Stop")
    message = "Test Plan Stop"
    redirect(URL('show_plan'))
    return dict(message=message)

def finish_plan():
    """delete an existing client"""
    row = db.test_plan[request.args(0,cast=int)]
    if None == row:
        raise HTTP(400, "<h1>Record not finded,may deleted by others.<a href=\"%s\"><br/>Go back homepage</h1>"%(URL("show_plan")))
    # if row.status != "Running":
    #     message = "Test Plan IsFinished"
    #     response.flash = T("Welcome to TAT Server!")
    #     redirect(URL('show_plan'))
    row.update_record(status = "AdminFinished")
    message = "Test Plan Stop"
    redirect(URL('show_plan'))
    return dict(message=message)

def edit_plan():
    """delete an existing client"""
    row = db.test_plan[request.args(0,cast=int)]
    tool_ver = ["1.2.0","1.1.0"]
    devices = devices_filter().values()
    devices+=row.display_devices
    scripts = script.get_svn_tag()
    form = FORM(TABLE(
        TR('Plan Name:', INPUT(_type='text', _name='plan_name',_value=row.plan_name,requires=IS_NOT_EMPTY())),
        TR('Test script:',  SELECT(scripts.keys(), _name='TestScript_Tag')),
        TR('Tool Version:',  SELECT(tool_ver, _name='tool',_value = row.tool_ver)),
        TR('Test Devices:',  SELECT(devices, _name='test_devices',_multiple="multiple",value = row.display_devices)),
        TR('Begin Time:',  INPUT(_type='text',_class = 'datetime',_name='begin_time',_value = row.begin_time)),
        TR('Tester:', INPUT(_type='text', _name='tester',_value = row.tester)),
        TR('SW Version:', INPUT(_type='text', _name='sw',_value = row.sw)),
        TR('delete:', INPUT(_type='checkbox', _name='delete')),
        TR('', INPUT(_type='submit', _value='SUBMIT')),
    ))

    if form.process().accepted:
        devices_id = []
        for device in form.vars.test_devices:
            temp = db(db.device.name == device).select().first()
            if None != temp:
                devices_id.append(temp.id)
        row = db((db.test_plan.plan_name == form.vars.plan_name)).select().first()
        if row == None:
            db.test_plan.update_or_insert(plan_name = form.vars.plan_name,TestScript_Tag = form.vars.TestScript_Tag,
                                          begin_time = form.vars.begin_time,tester = form.vars.tester,
                                          sw = form.vars.sw ,display_devices =form.vars.test_devices,tool_ver = form.vars.tool)
        else:
            row.update_record(plan_name = form.vars.plan_name,TestScript_Tag = form.vars.TestScript_Tag,
                                          begin_time = form.vars.begin_time,tester = form.vars.tester,
                                          sw = form.vars.sw ,display_devices =form.vars.test_devices,tool_ver = form.vars.tool)
        if form.vars.delete == 'on':
            db(db.test_plan.plan_name==form.vars.plan_name).delete()
        response.flash = 'record inserted'
        redirect(URL('show_plan'))
    elif form.errors:
        response.flash = 'form is invalid'
    else:
        response.flash = 'please fill the form'
    return dict(form=form, vars=form.vars)
    #
    # devices = []
    # row = db.test_plan[request.args(0,cast=int)]
    # form = SQLFORM(db.test_plan, row, deletable=True,showid=False,readonly=False,fields=['plan_name', 'TestScript_Tag','tester','tool_ver', 'display_devices',"begin_time","sw"])
    # print form.vars.plan_name
    #
    # if form.process().accepted:
    #     for id in row.test_devices:
    #         if None!=db.device[id]:
    #             devices.append(db.device[id].name)
    #     row.update_record(display_devices = devices)
    #     response.flash = 'record delete'
    #     redirect(URL('show_plan'))
    # return dict(form=form,devices = devices_filter(row),plan = row)

def get_log():
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
    print plan_name
    print sw
    print begin_time
    db_reportlog = db((db.reportlog.name == plan_name) & (db.reportlog.sw == sw)).select().first()
    if None != db_reportlog:
        db_reportlog.update_record(log_file=file)
    else:
        db.reportlog.insert(name = plan_name,sw = sw,begin_time = begin_time,log_file=file,log_breif="NA")

    db_reportlog = db((db.reportlog.name == plan_name) & (db.reportlog.sw == sw)).select().first()
    f.close()
    return dict(form = db_reportlog)

def get_report():
    return "success"

def display():
    form = SQLFORM(db.test_plan)
    return dict(form = form)

def show_plan():
    return dict(list_plan= db(db.test_plan).select())

def show_all_plan():
    return dict(list_plan= db(db.test_plan).select())

def show_all_report():
    from applications.TATServer.modules.testdata import xml2dict
    report = {}
    list_client = db(db.client).select()
    for client in list_client:
        report[client.name] = {}
        try:
            for device,test_data in db_rpc.show_all_report(client.url).items():
                report[client.name].update({device:xml2dict(test_data)})
        except:
            continue
    return dict(list_client =list_client ,report = report)

def show_report_bak():
    list_device = []
    report = {}
    data = []
    from testdata import TestData,time_2_second,second_2_time
    import codecs
    for id in request.args:
        plan = db.test_plan[id]
        for device_id in plan.test_devices:
            devices = db.device[device_id]
                # db(db.device.id==device_id).select().first()
            list_device.append(devices)
    def _get_report(list_device):
        url = list_device[0].host_name.url
        for device,test_data in db_rpc.show_all_report(url).items():
            report[device] = {}
            total_runtime = 0
            cases = TestData(test_data).parse_data()
            for case,value in cases.items():
                total_runtime += time_2_second(value["runtime"])
            report[device]["status"]=cases
            report[device]["runtime"]= second_2_time(total_runtime)
            report[device]["sw"] = db(db.device.name==device).select().first().build_date
        list_device = filter(lambda x:list_device[0].host_name!=x.host_name, list_device)
        if list_device!=[]:
            _get_report(list_device)
    _get_report(list_device)
    return dict(list_status =report,plan_name = plan)

def _dict2db(name,time,report):
    db.report.update_or_insert(plan_name=name,begin_time=time)
    raw = db((db.report.plan_name==name)&(db.report.begin_time==time)).select().first()
    if None == raw:
        raise HTTP(400, "<h1>Record not finded,may deleted by others.<a href=\"%s\"><br/>Go back homepage</h1>"%(URL("show_plan")))
    for d,status in report.items():
        raw.update_record(device = d,sw = status["sw"],mtbf = status['runtime'])
        for name in sorted(status['status'].keys()):
            db.report_status.update_or_insert(report_id = raw.id,case = name.split("_")[-1],passrate = status['status'][name]["passrate"] ,looptime = status['status'][name]["avgtime"])

def testdata_parse(device,testdata):
    from testdata import TestData,time_2_second,second_2_time
    report = {}
    try:
        report[device] = {}
        total_runtime = 0
        cases = TestData(testdata).parse_data()
        for case,value in cases.items():
            total_runtime += time_2_second(value["runtime"])
        report[device]["status"]=cases
        report[device]["runtime"]= second_2_time(total_runtime)
        report[device]["sw"] = "NA"
    except:
        pass
    return report


def get_report_by_plan(plan):
    # ttt = {'8bf232f_M812C': {'status': {'Telephony': {'passrate': '82.24%', 'runtime': '9:54:12', 'avgtime': '1:14:16'}, 'Browser': {'passrate': '99.77%', 'runtime': '7:21:49', 'avgtime': '0:55:13'}, 'Multi Tasking': {'passrate': '43.87%', 'runtime': '4:19:12', 'avgtime': '0:32:24'}, 'PIM': {'passrate': '100.00%', 'runtime': '0:28:20', 'avgtime': '0:3:32'}, 'Download': {'passrate': '95.50%', 'runtime': '4:34:2', 'avgtime': '0:34:15'}, 'Messaging': {'passrate': '76.12%', 'runtime': '23:52:53', 'avgtime': '2:59:6'}, 'Wifi': {'passrate': '63.93%', 'runtime': '3:2:43', 'avgtime': '0:26:6'}, 'Email': {'passrate': '98.42%', 'runtime': '17:41:7', 'avgtime': '2:12:38'}, 'Multi-Media': {'passrate': '99.66%', 'runtime': '5:29:23', 'avgtime': '0:41:10'}}, 'runtime': '76:43:41', 'sw': 'Thu Jul 31 13:56:18 CST 2014'}}
    report = {}
    from testdata import TestData, time_2_second, second_2_time

    # 1. access db file report
    if plan.status == "AdminFinished":
        db_report = db(
            (db.report.name == plan.plan_name) & (db.report.begin_time == plan.begin_time)).select().first()
        if None != db_report:
            report.update(eval(db_report.report))
            # report.update(ttt)
            return report
    data = dbfile.get_report(plan.plan_name, plan.begin_time)
    #2. RPC file report
    # for device_id in plan.test_devices:
    #     devices = db(db.device.id==device_id).select().first()
    if None!=plan.display_devices:
        for device_name in plan.display_devices:
            devices = db(db.device.name == device_name).select().first()
            if None == devices:
                #2 access db file
                print "access db file"
                if data != {}:
                    if data.has_key(device_name):
                        report.update(testdata_parse(device_name, data[device_name]))
                        continue
                    else:
                        continue
            else:
                # raise HTTP(400, "<h1>Record not finded,may deleted by others.<a href=\"%s\"><br/>Go back homepage|<a href=\"%s\">Edit Test Plan</h1>"%(URL("index"),(URL("index"))))
                # devices =  db.client(id)
                url = devices.host_name.url
                # try:
                for device, test_data in db_rpc.show_report_by_device(url, devices.name).items():
                # for device, test_data in db_rpc.show_all_report(url).items():
                    data = test_data["data"]
                    log = test_data["log"]
                    if data != ''and data != None:
                        report[device] = {}
                        total_runtime = 0
                        cases = TestData(data).parse_data()
                        for case, value in cases.items():
                            total_runtime += time_2_second(value["runtime"])
                        report[device]["status"] = cases
                        report[device]["runtime"] = second_2_time(total_runtime)
                        report[device]["sw"] = devices.build_date
                        if (log!=""):
                            report[device]["except"] = log
                            db_reportlog = db((db.reportlog.name == plan.plan_name) & (db.reportlog.sw == plan.sw)& (db.reportlog.begin_time == plan.begin_time)).select().first()
                            if None != db_reportlog:
                                db_reportlog.update_record(log_breif=log[1])
                            else:
                                db.reportlog.insert(name = plan.plan_name,sw = plan.sw,begin_time = plan.begin_time,log_breif=log[1])
                        else:
                            report[device]["except"] = log
                        dbfile.store_report(plan.plan_name, plan.begin_time, device, data.data)
                # except:
                #     continue
    # save to db report
    # db_report = db((db.report.name == plan.plan_name) & (db.report.begin_time == plan.begin_time)).select().first()
    db_report = db((db.report.name == plan.plan_name) & (db.report.sw == plan.sw)& (db.report.begin_time == plan.begin_time)).select().first()
    if None != db_report:
        db_report.update_record(report=report)
    else:
        db.report.insert(name=plan.plan_name,sw = plan.sw,begin_time=plan.begin_time, report=report)
    return report


def show_report():
    plan = db.test_plan[request.args(0,cast=int)]
    if plan == None:
        raise HTTP(400, "<h1>Record not finded,may deleted by others.<a href=\"%s\"><br/>Go back homepage</h1>"%(URL("show_plan")))
    report = get_report_by_plan(plan)
    return dict(report =report,plan = plan)

def show_all_report():
    all_report = {}
    from testdata import TestData,time_2_second,second_2_time
    import codecs
    for row in db().select(db.test_plan.ALL):
        report = {}
        for device_id in row.test_devices:
            devices = db(db.device.id==device_id).select().first()
            # devices =  db.client(id)
            url = devices.host_name.url
            for device,test_data in db_rpc.show_report_by_device(url,devices.name).items():
                report[devices.name] = {}
                total_runtime = 0
                cases = TestData(test_data).parse_data()
                for case,value in cases.items():
                    total_runtime += time_2_second(value["runtime"])
                report[device]["status"]=cases
                report[device]["runtime"]= second_2_time(total_runtime)
                report[device]["sw"] = devices.build_date
                dbfile.store_report(row.plan_name,row.begin_time,test_data)
        all_report[row.plan_name] = report
    if report == {}:
        raise HTTP(400, "<h1>No test plan exist!<a href=\"%s\"><br/>Go back homepage</h1>"%(URL("index")))
    return dict(all_report =all_report)

def show_current_report():
    all_report = {}
    for row in db().select(db.test_plan.ALL):
        all_report[row.plan_name] = get_report_by_plan(row)
    return dict(all_report =all_report)

def show_history_report():
    all_report = {}
    from testdata import TestData,time_2_second,second_2_time
    import codecs
    for row in db().select(db.test_plan.ALL):
        report = {}
        for device_id in row.test_devices:
            devices = db(db.device.id==device_id).select().first()
            # devices =  db.client(id)
            url = devices.host_name.url
            for device,test_data in db_rpc.show_report_by_device(url,devices.name).items():
                report[devices.name] = {}
                total_runtime = 0
                cases = TestData(test_data).parse_data()
                for case,value in cases.items():
                    total_runtime += time_2_second(value["runtime"])
                report[device]["status"]=cases
                report[device]["runtime"]= second_2_time(total_runtime)
                report[device]["sw"] = devices.build_date
                dbfile.store_report(row.plan_name,row.begin_time,test_data)
        all_report[row.plan_name] = report
    if report == {}:
        raise HTTP(400, "<h1>No test plan exist!<a href=\"%s\"><br/>Go back homepage</h1>"%(URL("index")))
    return dict(all_report =all_report)

def idx_tst():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    return dict(message=T('Hello World'))


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())



def display_form():
    record = db.person(request.args(0)) or redirect(URL('index'))
    url = URL('download')
    form = SQLFORM(db.person, record, deletable=True,
                   upload=url, fields=['name', 'image'])
    if request.vars.image!=None:
        form.vars.image_filename = request.vars.image.filename
    if form.process().accepted:
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    return dict(form=form)


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