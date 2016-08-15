# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
#response.generic_patterns = ['*'] if request.is_local else []
response.generic_patterns = ['*']
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Service, PluginManager, prettydate
from gluon.debug import dbg

auth = Auth(db)
service = Service()
plugins = PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer

mail.settings.server = 'logging' if request.is_local else 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
# from gluon.contrib.login_methods.janrain_account import use_janrain
# use_janrain(auth, filename='private/janrain.key')


# create a scheduler instance
from gluon.scheduler import Scheduler
scheduler = Scheduler(db)
#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

db.define_table('department',
        Field('name'),
        format='%(name)s')

db.define_table('team',
        Field('name'),
        Field('department',"reference department"),
        format='%(name)s')

db.define_table('department_manager',
        Field('department',"reference department"),
        Field('manager',db.auth_user),
        format='%(department)s')

db.define_table('team_leader',
        Field('team',"reference team"),
        Field('leader',db.auth_user),
        format='%(team)s')

db.define_table('project',
                Field('name'),
                Field('projtype'),
                Field('sw'),
                Field('appli'),
                Field('perso'),
                Field('perso_m'),
                format='%(name)s-%(sw)s-%(perso)s')

db.define_table('tool',
                Field('name'),
                Field('ver'),
                format='%(name)s')

db.define_table('client',
                Field('name',requires=(IS_NOT_EMPTY(),IS_NOT_IN_DB(db, 'client.name'))),
                Field('url',requires=IS_NOT_EMPTY()),
                Field('workstation',type = 'boolean',default= False),
                format='%(name)s')

DEVICE_STATUS = ("idle","running","error")
db.define_table('device',
                Field('name',requires=(IS_NOT_EMPTY(),IS_NOT_IN_DB(db, 'device.name'))),
                Field('display_id'),
                Field('build_date'),
                Field('product'),
                Field('region'),
                Field('hardware'),
                Field('build_type'),
                Field('build_version'),
                Field('client',"reference client"),
                Field('status',requires=IS_IN_SET(DEVICE_STATUS),default=DEVICE_STATUS[0] ),
                format='%(name)s')

db.device.status.represent = lambda status,row:SPAN(status,_class=status)

# db.define_table('device_status',
#                 Field('name'),
#                 Field('plan_name'),
#                 Field('status'),
#                 Field('tester'),
#                 format='%(name)s')
# db.device_status.name.requires = IS_NOT_IN_DB(db, 'device_status.name')
#
# db.define_table('test_client',
#                 Field('client_name'),
#                 # Field('plan_list',"list:reference test_plan"),
#                 Field('plan_list',"list:string"),
#                 Field('testor_name'),
#                 Field('status'),
#                 format='%(client_name)s')
#
#
# db.define_table('test_client_status',
#                 Field('client_name'),
#                 Field('plan_name'),
#                 Field('status'),
#                 format='%(client_name)s-%(plan_name)s')
# db.test_client.client_name.requires = IS_IN_DB(db, 'client')
db.define_table("std",
                Field("phase"),
                Field("levels"),
                Field("dut"),
                Field("mtbf"),
                format='%(phase)s-%(levels)s')

db.define_table("std_level",
                Field("levels"),
                Field('std',"list:reference std"),
                Field("description"),
                Field("dut"),
                format='%(levels)s')

db.define_table("plan_schedual",
                Field("name",requires=IS_NOT_EMPTY),
                format='%(name)s')

PLAN_STATUS = ("pendding","idle","running","finished","adminfinished")
db.define_table('test_plan',
                Field('plan_name',requires=(IS_NOT_EMPTY(),IS_NOT_IN_DB(db, 'test_plan.plan_name'))),
                # Field('TestScript_Branch'),
                Field("project","reference project"),
                Field('test_case'),
                # Field('Tool',"reference tool"),
                Field('tool',"reference tool"),
                # Field('test_clients',"list:reference client"),
                Field('runcircle',default=20),
                Field('test_devices',"list:reference device"),
                Field('devices',"list:string",writable=False),
                Field('sdevices',"list:string",writable=False),
                Field('begin_time',"datetime",default=request.now),
                Field('status',writable=False,default=PLAN_STATUS[0]),
                # Field('test_operation',writable=False,default="INIT"),
                # Field('tester',"reference auth_user"),
                Field('sw',requires=IS_NOT_EMPTY()),
                Field("std_level","reference std_level"),
                #Field("task_queue"),
                auth.signature,
                format='%(plan_name)s')
db.test_plan.status.represent = lambda status,row:SPAN(status,_class=status)

REPORT_STATUS = ("testing","pass","failed")

db.define_table('report',
                Field('name',writable=False,requires=IS_NOT_EMPTY()),
                Field('sw',writable=False,requires=IS_NOT_EMPTY()),
                Field('datetime',"datetime",writable=False,requires=IS_NOT_EMPTY()),
                Field('report',writable=False),
                Field("results",writable=False,requires=IS_IN_SET(REPORT_STATUS),default=REPORT_STATUS[0]),
                Field("std_level","reference std_level"),
                # Field('reports',"list:reference device_report"),
                Field("mtbf"),
                Field('mailed','boolean',default=False,writable=False,readable=False),
                format='%(name)s')
db.report.results.represent = lambda results,row:SPAN(results,_class=results)

DEVICE_REPORT_STATUS = ("Running","pass","failed","Manual Stop","Crash","Anr","Android reboot","Error")
db.define_table('device_report',
                Field('report',"reference report"),
                Field('name',requires=IS_NOT_EMPTY()),
                Field('test_type',writable=False),
                Field('status',writable=False,requires=IS_IN_SET(DEVICE_REPORT_STATUS),default=DEVICE_REPORT_STATUS[0]),
                Field('mtbf',writable=False),
                Field('mailed','boolean',default=False,writable=False,readable=False),
                # Field('cases',writable=False),
                format='%(name)s')
db.device_report.status.represent = lambda status,row:SPAN(status,_class=status)

db.define_table('case_report',
                Field('report',"reference report"),
                # Field('device_report',"reference device_report"),
                Field('device_name',requires=IS_NOT_EMPTY()),
                Field('case_name',requires=IS_NOT_EMPTY()),
                Field('passrate',writable=False),
                Field('avgtime',writable=False),
                Field('run_time',writable=False),
                Field('status',writable=False),
                format='%(name)s')

db.define_table('case_defects',
                Field('test_plan',"reference test_plan"),
                Field('name',requires=IS_NOT_EMPTY()),
                Field('counts','integer',requires=IS_NOT_EMPTY(),default=0),
                format='%(name)s')

db.define_table('report_log',
                Field('device_report',"reference device_report"),
                Field('title'),
                Field('brief'),
                Field('log_file',"upload"),
                format='%(title)s')

db.define_table('meminfo',
                Field('device_report',"reference device_report"),
                Field('memory_data'),
                format='%(device_report)s')

# db.define_table('reportlog',
#                 Field('name',"string"),
#                 Field('sw'),
#                 Field('begin_time',"datetime"),
#                 Field('log_title'),
#                 Field('log_breif'),
#                 Field('log_file',"upload"),
#                 format='%(name)s')

# db.test_plan.client_name.requires = IS_IN_DB(db,db.client.id,'%(name)s')

db.define_table('email',
                Field('sendto','list:string'),
                Field('subject'),
                Field('body','text'),
                Field('sender'),
                Field('status',requires=IS_IN_SET(('pending','sent','failed'))),
                Field('author'))

def fullname(user):
    if user == None:
        return "Unknown"
    return "%(first_name)s %(last_name)s"%user

def show_status(status,row=None):
    return SPAN(status,_class=status)

def report_from_db(plan):
    query = (db.report.name == plan.plan_name) & (db.report.sw == plan.sw)& (db.report.datetime == plan.begin_time)
    report = db(query).select().first()
    if report == None:
        db.report.insert(name=plan.plan_name,sw = plan.sw,datetime=plan.begin_time)
        return db(query).select().first()
    return report

def report_from_rpc(plan):
    query = (db.report.name == plan.plan_name) & (db.report.sw == plan.sw)& (db.report.datetime == plan.begin_time)
    #db(query).delete()
    if not db(query).select().first():
        db.report.insert(name=plan.plan_name,sw = plan.sw,datetime=plan.begin_time)
    return db(query).select().first()

def device_report_from_db(report_id,device_name):
    query = (db.device_report.report == report_id) & (db.device_report.name == device_name)
    device_report = db(query).select().first()
    if device_report == None:
        db.device_report.insert(report=report_id,name=device_name)
        return db(query).select().first()
    return device_report

def case_report_from_db(report_id,device_name,case_name):
    query = (db.case_report.report == report_id)& (db.case_report.device_name == device_name) & (db.case_report.case_name == case_name)
    case_report = db(query).select().first()
    if case_report == None:
        db.case_report.insert(report=report_id,case_name = case_name,device_name=device_name)
        return db(query).select().first()
    return case_report

def meminfo_report_from_db(device_report_id):
    query = (db.meminfo.device_report == device_report_id)
    meminfo = db(query).select().first()
    if meminfo == None:
        db.meminfo.insert(device_report=device_report_id)
        return db(query).select().first()
    return meminfo

def cases_defects_from_db(plan,name):
    query = (db.case_defects.test_plan == plan.id) & (db.case_defects.name == name)
    case_defect = db(query).select().first()
    if case_defect == None:
        db.case_defects.insert(test_plan=plan.id,name=name)
        return db(query).select().first()
    return case_defect

def db_fetch_log(device_report,plan,report):
    devices = db(db.device.name.like(str(device_report.name)+"%")).select().first()
    #if devices!=None and devices.client.workstation == True:
    if devices!=None and devices.client.workstation:
        try:
            for device, report_data in db_rpc.show_report_by_device(devices.client.url, devices.name).items():
                log = report_data["log"]
                if (log!=""):
                    db_log = db(db.report_log.device_report == device_report.id).select().first()
                    if None != db_log:
                        db_log.update_record(title = log[0],brief=log[1])
                    else:
                        db.report_log.insert(device_report = device_report.id,title = log[0],brief=log[1])
                    #devices defects
                    mod = re.findall(r"(.*)_.*", str(log[0]),re.I);
                    mod = mod[0] if mod else str(log[0])
                    mod_report = db((db.case_report.report == report.id)&(db.case_report.case_name.like(mod+"%"))).select().first()
                    if mod_report:
                        if mod_report.status==None or mod_report.status.lower() not in ["anr","crash","android reboot","error","androidreboot"]:
                            status = str(log[0]).split("_")[-1]
                            mod_report.update_record(status = "Android reboot" if status == "AndroidReboot" else status)
                            case_defect = cases_defects_from_db(plan,mod)
                            if case_defect:
                                counts = case_defect.counts+1
                                case_defect.update_record(counts = counts)
        except:
            pass

from ReportParser import time_2_second,second_2_time
def report_analysis(plan,report):
    mtbf = 0
    isfinished = True
    device_log = {}
    mtbf_resault = ""
    devices = db(db.device_report.report == report.id).select()
    for device in devices:
        if time_2_second(device.mtbf) >= int(plan.std_level.dut)*3600:
            mtbf+=time_2_second(device.mtbf)
        #log
        db_log = db(db.report_log.device_report == device.id).select().first()
        if db_log != None:
            device_log[device.id] = db_log
        elif db_log == None and device.status in ["Anr","Crash","Android reboot","Error"]:
            db_fetch_log(device,plan,report)
            db_log = db(db.report_log.device_report == device.id).select().first()
            if db_log != None:
                device_log[device.id] = db_log
    for id in plan.std_level.std:
        std = db.std[id]
        resault = "pass" if mtbf/3600 >= int(std.mtbf) else ("failed")
        mtbf_resault+=" %s(%s) "%(resault,std.phase)
        report.update_record(results = resault)
    mtbf=second_2_time(mtbf)
    report.update_record(mtbf = mtbf,std_level = plan.std_level)
    status_span = []
    for name in db(db.case_report.report == report.id).select(groupby=db.case_report.case_name,orderby=db.case_report.case_name):
        status_span.append(name.case_name)
    try:
        status_span.sort(key=lambda x:int(x.split("_")[0]))
    except:
        pass
    return devices,mtbf,status_span,device_log,mtbf_resault


def send_email_realtime(to,subject,message,sender):
    if not isinstance(to,list):to = [to]
    mail.settings.sender = sender
    return mail.send(to=to,subject=subject,message=message or '(no message)')

def send_email_deferred(to,subject,message,sender):
    if not isinstance(to,list):to = [to]
    db.email.insert(sendto=to,subject=subject,body=message,sender=sender,
                    status='pending')
    scheduler.queue_task(send_pending_emails)

def send_pending_emails():
    rows = db(db.email.status=='pending').select()
    for row in rows:
        if mail.send(to=row.sendto,subject=row.subject,message=row.body,sender=row.sender):
            row.update_record(status = 'sent')
        else:
            row.update_record(status = 'failed')
        db.commit()

EMAIL_POLICY = 'deferred'
def send_email(to,subject,message,sender):
    if EMAIL_POLICY == 'realtime':
        return send_email_realtime(to,subject,message,sender)
    else:
        return send_email_deferred(to,subject,message,sender)

def send_report_by_email(plan,report,device_report=None):
    if (report.mailed and device_report==None) or (device_report!=None and device_report.mailed and report.mailed):
        return
    else:
        devices,mtbf,status_span,logs,resaults = report_analysis(plan,report)
        message = "<html><li>The target is <strong> level%s. %s ( 5 devices )</strong> </li>"%(plan.std_level.levels,plan.std_level.description) if plan.std_level else "NA"
        message+= "<ul><li> Pass Rate for every module SHOULD > 95%</li><li>Valid MTBF for single DUT(Device Under Test) MUST>=40H</li></ul>"
        message+= "<li><strong>The actual MTBF</strong> is %s</li>"%report.mtbf
        if device_report!=None and not device_report.mailed and device_report.status=="error": #todo
            message+= "One devices just:%s"%report.status
            device_report.update_record(mailed = True)
        if plan.status == "finished":
            report.update_record(mailed = True)

        message+="%s </html>"%A('Details see',_href=URL(args=plan.id,scheme=True, host=True))
        #send_email(to=plan.created_by.email,sender=auth.user.email,
        send_email(to="valeera@foxmail.com",sender=auth.user.email,
          subject="Automation report plan: %s" % plan.plan_name,
          message=message)

def pending_stability(row):
    row.update_record(status = "pendding")

def stop_stability(row):
    row.update_record(status = "idle")

def start_test(row):
    row.update_record(status = "pendding")
    if row.status=="pending" and request.now>=row.begin_time:
        try:
            for d,p in dbfile.gen_plan(row).items():
                db_rpc.test_start(db(db.device.name == d).select().first().client.url,p)
            row.update_record(status = "running")
        except:
            traceback.print_exc()
            row.update_record(status="idle")
import re
def analysis_pareto():
    for log in db(db.report_log).select():
        print 1
        name = re.findall(r"(.*)_.*", log.title,re.I)
        plan = db(db.test_plan.plan_name == log.device_report.report.name).select().first()
        if plan and name:
            case_defect = cases_defects_from_db(plan,name[0])
            print case_defect
            case_defect.update_record(counts = case_defect.counts+1)

#analysis_pareto()
'''
def plan_task():
    while True:
        for row in db(db.test_plan).select():
            if row.status=="pending" and request.now>=row.begin_time:


                print db(db.device.name == d).select().first().client.url
                try:
                    for d,p in dbfile.gen_plan(row).items():
                        db_rpc.test_start(db(db.device.name == d).select().first().client.url,p)
                        row.update_record(status = "running")
                except:
                    traceback.print_exc()
                    row.update_record(status="idle")
        time.sleep(60)

def send_plan(id):
    row = db(db.text_plan.id == id).select().firxt()
    if plan.status=="pending" and request.now>=row.begin_time:
        try:
            for d,p in dbfile.gen_plan(row).items():
                db_rpc.test_start(db(db.device.name == d).select().first().client.url,p)
            row.update_record(status = "running")
            return True
        except:
            traceback.print_exc()
            row.update_record(status="idle")
    return False

#scheduler.queue_task(plan_task,repeats = 1, period = 180)#
#scheduler.queue_task(plan_task)
## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
'''
