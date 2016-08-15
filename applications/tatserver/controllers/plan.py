# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - api is an example of Hypermedia API support and access control
#########################################################################

me = auth.user_id

def index():
    return redirect(URL("show"))

@auth.requires_membership('managers')
def manager():
    grid = SQLFORM.grid(db.test_plan)
    return locals()


def devices_filter(plan = None):
    devices = {}
    query = ((db.test_plan.status != 'finished')|(db.test_plan.status != 'adminfinished'))
    plans = db(query&(db.test_plan.id != plan.id)).select() if plan!=None else db(query).select()
    for device in  db(db.device).select():
        devices.update({device.id:device.name})
        if plans!=None:
            for row in plans:
                if row.devices!= None and device.name in row.devices:
                    devices.pop(device.id)
    return devices

def make_appli_bk():
    b = proj.get_projects()
    aa = ["","1","21"]
    if request.vars.proj:
        html = SPAN('appli:', SELECT(aa, _name='appli',id="appli", _onchange="ajax('make_perso',['appli'], 'perso');"),_style="position:absolute;border:1pt solid #c1c1c1;width:188px;  height:19px;clip:rect(-1px 190px 190px 170px);")
        html += SPAN(_style="position:absolute;border-top:1pt solid #c1c1c1;border-left:1ptsolid #c1c1c1;border-bottom:1pt solid #c1c1c1;width:170px;height:19px;")

        html += SPAN(INPUT(type="text",name="makeupCo",id="makeupCo",value="请选择或输入",_style="width:170px;height:15px;border:0pt;"),_style="position:absolute;border-top:1pt solid #c1c1c1;border-left:1pt   solid #c1c1c1;border-bottom:1pt solid #c1c1c1;width:170px;height:19px;")

        return SPAN('appli',html)

def make_perso_bk():
    makes = ['Alto22', 'Alto33']
    if request.vars.appli:
        return TR('perso:', SELECT(makes, _name='perso'))


def project_selector():
    if not request.vars.project: return ''
    projects = ['January', 'February', 'March', 'April', 'May',
              'June', 'July', 'August', 'September' ,'October',
              'November', 'December']
    project_start = request.vars.project.capitalize()
    selected = [m for m in projects if m.startswith(project_start)]
    return DIV(*[DIV(k,
                     _onclick="jQuery('#project').val('%s')" % k,
                     _onmouseover="this.style.backgroundColor='yellow'",
                     _onmouseout="this.style.backgroundColor='white'"
                     ) for k in selected])

def appli_maker():
    if not request.vars.project: return ''
    session.project = request.vars.project
    return TR("Appli",INPUT(_type="text",_id="appli",_name="appli",_style="width: 250px",_onkeyup="ajax('appli_selector', ['appli'], 'appli_suggestions');"),
        DIV(_id="appli_suggestions",_class="suggestions",_style="position: absolute;"))

def appli_selector():
    if not request.vars.project: return ''
    appli_list = proj.get_appli(request.vars.project,request.vars.type)
    #appli_start = request.vars.appli.capitalize()
    appli_start = request.vars.appli
    selected = [m for m in appli_list if m.startswith(appli_start)]
    return DIV(*[DIV(k,
                     _onclick="jQuery('#appli').val('%s')" % k,
                     _onmouseover="this.style.backgroundColor='yellow'",
                     _onmouseout="this.style.backgroundColor='white'"
                     ) for k in selected])

def appli_clean():
    selected = []
    return DIV(*[DIV(k,
                     _onclick="jQuery('#appli').val('%s')" % k,
                     _onmouseover="this.style.backgroundColor='yellow'",
                     _onmouseout="this.style.backgroundColor='white'"
                     ) for k in selected])

def perso_maker():
    if not request.vars.project: return ''
    session.perso=["4","5","6"]
    return TR("Appli",INPUT(_type="text",_id="appli",_name="appli",_style="width: 250px",_onkeyup="ajax('appli_selector', ['appli'], 'appli_suggestions');"),
        DIV(_id="appli_suggestions",_class="suggestions",_style="position: absolute;"))

def perso_selector():
    if( not request.vars.project) or (not request.vars.appli): return ''
    perso_list = proj.get_perso(request.vars.project,request.vars.appli)
    perso_start = request.vars.perso
    selected = [m for m in perso_list if m.startswith(perso_start)]
    return DIV(*[DIV(k,
                     _onclick="jQuery('#perso').val('%s')" % k,
                     _onmouseover="this.style.backgroundColor='yellow'",
                     _onmouseout="this.style.backgroundColor='white'"
                     ) for k in selected])
def perso_clean():
    return DIV(*[DIV(k,
                     _onclick="jQuery('#perso').val('%s')" % k,
                     _onmouseover="this.style.backgroundColor='yellow'",
                     _onmouseout="this.style.backgroundColor='white'"
                     ) for k in []])

def form_make():
    INPUT(type="text",id="month",name="month",_style="width: 250px")
    DIV(id="suggestions",_class="suggestions",_style="position: absolute;")

@auth.requires_membership('tester','managers')
def create():
    """ a simple entry form with various types of objects """
    mdevices = devices_filter().values()
    sdevices = devices_filter().values()
    tools = []
    for row in db(db.tool).select():
        tools.append(row.id)
    std = []
    for row in db(db.std_level).select():
        std.append("level-%s"%(row.levels))
    scripts = script.get_svn_tag() #todo
    form = FORM(TABLE(
        TR('Plan Name:', INPUT(_type='text', _name='plan_name',requires=IS_NOT_EMPTY())),
        #SPAN(TR(TD('proj:',  SELECT(proj.get_projects(),_name='proj',_onchange="ajax('make_appli',['proj'], 'appli');"),
        #           TD('appli:',_id='appli'),
        #           TD('perso:',_id='perso')))),
        #TR("Project",SELECT(proj.get_projects(),_name='project',_onchange="ajax('appli_maker',['project'], 'appli');"),
        #TR("Appli",INPUT(_type="text"),_id='appli')),
        TR("Project",SELECT(proj.get_projects(),_name='project'),TR("Type",SELECT(proj.get_type(),_name='type',_value=proj.get_type()[0])),
        TR("Appli",INPUT(_type="text",_id="appli",_name="appli",_style="width: 250px",_onkeyup="ajax('appli_selector', ['project','appli','type'], 'appli_suggestions');",_onfocus="ajax('perso_clean', [''], 'perso_suggestions');"),
              DIV(_id="appli_suggestions",_class="appli_suggestions",_style="position: absolute;")),

        TR("Perso",INPUT(_type="text",_id="perso",_name="perso",_style="width: 250px",_onkeyup="ajax('perso_selector', ['project','appli','perso'], 'perso_suggestions');",_onfocus="ajax('appli_clean', [''], 'appli_suggestions');"),
              DIV(_id="perso_suggestions",_class="perso_suggestions",_style="position: absolute;"))),

        #TR("Appli",INPUT(_type="text",_id="appli",_name="appli",_style="width: 250px",_onkeyup="ajax('project_selector', ['appli'], 'suggestions');"),
        #DIV(_id="appli_suggestions",_class="suggestions",_style="position: absolute;")),
        TR('Test Case:',  SELECT(scripts.keys(), _name='test_case')),
        TR('Tool:',  SELECT(tools, _name='tool')),
        TR('mDevices:',  SELECT(mdevices, _name='devices',_multiple="multiple")),
        # TR('sDevices:',  SELECT(sdevices, _name='sdevices',_multiple="multiple")),
        TR('Begin Time:',  INPUT(_type='text',_class = 'datetime',_name='begin_time',_value = request.now.strftime("%Y-%m-%d %H:%M:%S"))),
        TR('SW Version:', INPUT(_type='text', _name='sw')),
        TR('runcircle:', INPUT(_type='text', _name='runcircle',_value = 20)),
        TR('std:',  SELECT(std, _name='std')),
        TR('', INPUT(_type='submit', _value='SUBMIT')),
    ))
    if form.process().accepted:
        std = db((db.std_level.levels == form.vars.std.split("-")[1])).select().first()
        row = db((db.test_plan.plan_name == form.vars.plan_name)).select().first()
        if row == None:
            project = db.project.insert(name = form.vars.project,projtype=form.vars.type,sw = form.vars.appli, perso = form.vars.perso)
            db.test_plan.insert(plan_name = form.vars.plan_name,test_case = form.vars.test_case,
                                          begin_time = form.vars.begin_time,sw = form.vars.sw ,devices =form.vars.devices,tool = form.vars.tool,std_level = std.id,project = db.project[project])

        # for device,plan in dbfile.gen_plan(form.vars).items():
        #     db_rpc.test_start(db(db.device.name == device).select().first().host_name.url,plan)
        response.flash = 'record inserted'
        redirect(URL('show'))
    elif form.errors:
        response.flash = 'form is invalid'
    else:
        response.flash = 'please fill the form'
    return dict(form=form,scripts = scripts)

def show():
    def list_device(devices):
        d = []
        for device in devices:
           d.append(A("%s | "%device,_href=URL('device','show_by_name',args=device)))
        return d
    db.test_plan.created_by.readable = True
    db.test_plan.id.readable = False
    db.test_plan.project.readable = False
    db.test_plan.devices.represent = lambda devices,row:list_device(devices)
    grid = SQLFORM.grid(db.test_plan,details=False,csv=False,editable=False,create=False,#editable=lambda row:(row.created_by==me)
                        deletable=lambda row:(row.created_by==me),
                        links=[lambda row:A('start',_href=URL('start',args=row.id),_class='btn btn-primary') if row.created_by==me else "",
                                 lambda row:A('stop',_href=URL('stop',args=row.id),_class='btn btn-primary') if row.created_by==me else "",
                                 lambda row:A('finish',_href=URL('finish',args=row.id),_class='btn btn-primary') if row.created_by==me else "",
                                 lambda row:A('report',_href=URL('report','current',args=row.id),_class='btn btn-primary'),
                                 lambda row:A('history',_href=URL('report','history',args=row.id),_class='btn btn-primary'),
                                 lambda row:A('pareto',_href=URL('report','pareto',args=row.id),_class='btn btn-primary'),
                                 lambda row:A('edit',_href=URL('plan','edit',args=row.id),_class='btn btn-primary') if row.created_by==me else "",
                            ],
                        fields=[
                            db.test_plan.status,
                            db.test_plan.plan_name,
                            db.test_plan.sw,
                            #db.test_plan.tool,
                            db.test_plan.devices,
                            db.test_plan.begin_time,
                            db.test_plan.created_by
                        ])
    return locals()

import time
@auth.requires_membership('tester','managers')
def start():
    """start a plan"""
    devices = []
    row = db.test_plan[request.args(0,cast=int)]
    if None == row:
        raise HTTP(400, "<h1>Record not finded,may deleted by others.<a href=\"%s\"><br/>Go back homepage</h1>"%(URL("show_plan")))
    for id in row.devices:
        if None!=db(db.device.name==id).select().first():
            devices.append(id)
    row.update_record(status = "running",devices = devices,begin_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    #for device,plan in dbfile.gen_plan(row).items():
    #     db_rpc.test_start(db(db.device.name == device).select().first().client.url,plan)
    pending_stability(row)
    message = "Test Plan Start"
    redirect(URL('show'))
    return dict(message=message)

@auth.requires_membership('tester','managers')
def stop():
    """stop a plan"""
    row = db.test_plan[request.args(0,cast=int)]
    if None == row:
        raise HTTP(400, "<h1>Record not finded,may deleted by others.<a href=\"%s\"><br/>Go back homepage</h1>"%(URL("show_plan")))
    if row.status != "running":
        message = "Test Plan IsStoped"
        redirect(URL('show_plan'))
    stop_stability(row)
    row.update_record(status = "stop")
    message = "Test Plan Stop"
    redirect(URL('show'))
    return dict(message=message)

@auth.requires_membership('tester','managers')
def finish():
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
    redirect(URL('show'))
    return dict(message=message)

@auth.requires_membership('tester','managers')
def edit():
    """delete an existing client"""
    row = db.test_plan[request.args(0,cast=int)]
    tool = ["1.2.0","1.1.0"]
    devices = devices_filter().values()
    devices+=row.devices
    scripts = script.get_svn_tag()
    std = []
    for stdrow in db(db.std_level).select():
        std.append("level-%s"%(stdrow.levels))
    form = FORM(TABLE(
        TR('Plan Name:', INPUT(_type='text', _name='plan_name',_value=row.plan_name,requires=IS_NOT_EMPTY())),
        TR('Test Case:',  SELECT(scripts.keys(), _name='test_case',value = row.test_case)),
        TR('Tool:',  SELECT(tool, _name='tool',_value = row.tool)),
        TR('mDevices:',  SELECT(devices, _name='devices',_multiple="multiple",value = row.devices)),
        TR('Begin Time:',  INPUT(_type='text',_class = 'datetime',_name='begin_time',_value = request.now.strftime("%Y-%m-%d %H:%M:%S"))),
        TR('SW Version:', INPUT(_type='text', _name='sw',_value = row.sw)),
        TR('runcircle:', INPUT(_type='text', _name='runcircle',_value = row.runcircle)),
        TR('std:',  SELECT(std, _name='std',_value = row.std_level)),
        TR('', INPUT(_type='submit', _value='SUBMIT')),
    ))

    if form.process().accepted:
        std = db((db.std_level.levels == int(form.vars.std.split("-")[1]))).select().first()
        row = db((db.test_plan.plan_name == form.vars.plan_name)).select().first()

        print form.vars
        row.update_record(test_case = form.vars.test_case, begin_time = form.vars.begin_time,sw = form.vars.sw ,devices =form.vars.devices,std = std.id) if row != None else redirect(URL('index'))
        # for device,plan in dbfile.gen_plan(form.vars).items():
        #     db_rpc.test_start(db(db.device.name == device).select().first().host_name.url,plan)
        response.flash = 'record inserted'
        redirect(URL('show'))
    elif form.errors:
        response.flash = 'form is invalid'
    else:
        response.flash = 'please fill the form'
    return dict(form=form,scripts = scripts)


# --------------------------------------------------------------legency-------------------------------------------
@auth.requires_membership('tester','managers')
def new_legency():
    """ a simple entry form with various types of objects """
    tool_ver = ["1.2.0","1.1.0"]
    mdevices = devices_filter().values()
    sdevices = devices_filter().values()
    scripts = script.get_svn_tag()
    form = FORM(TABLE(
        TR('Plan Name:', INPUT(_type='text', _name='plan_name',requires=IS_NOT_EMPTY())),
        TR('Test script:',  SELECT(scripts.keys(), _name='test_case')),
        TR('Tool Version:',  SELECT(tool_ver, _name='tool')),
        TR('mDevices:',  SELECT(mdevices, _name='devices',_multiple="multiple")),
        TR('sDevices:',  SELECT(sdevices, _name='sdevices',_multiple="multiple")),
        TR('Begin Time:',  INPUT(_type='text',_class = 'datetime',_name='begin_time',_value = request.now.strftime("%Y-%m-%d %H:%M:%S"))),
        # TR('Tester:', INPUT(_type='text', _name='tester')),
        TR('SW Version:', INPUT(_type='text', _name='sw')),
        TR('runcircle:', INPUT(_type='text', _name='runcircle')),
        TR('', INPUT(_type='submit', _value='SUBMIT')),
    ))
    if form.process().accepted:
        # devices_id = []
        # for device in form.vars.devices:
        #     temp = db(db.device.name == device).select().first()
        #     if None != temp:
        #         devices_id.append(temp.id)
        row = db((db.test_plan.plan_name == form.vars.plan_name)).select().first()
        if row == None:
            db.test_plan.update_or_insert(plan_name = form.vars.plan_name,test_case = form.vars.test_case,
                                          begin_time = form.vars.begin_time,sw = form.vars.sw ,devices =form.vars.devices,tool_ver = form.vars.tool)
        #to do test plan
        # for device,plan in dbfile.gen_plan(form.vars).items():
        #     db_rpc.test_start(db(db.device.name == device).select().first().host_name.url,plan)
        response.flash = 'record inserted'
        redirect(URL('show'))
    elif form.errors:
        response.flash = 'form is invalid'
    else:
        response.flash = 'please fill the form'
    return dict(form=form, vars=form.vars,scripts = scripts)

@auth.requires_membership('tester','managers')
def show_legency():
    return dict(list_plan= db(db.test_plan).select())

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
