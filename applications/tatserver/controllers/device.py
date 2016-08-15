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
    return redirect(URL("show_all"))

def create():
    db.device.status.writable = False
    db.device.status.readable = False
    form = SQLFORM(db.device)
    if form.accepts(request.post_vars,session):
        session.flash = 'device created ok'
        redirect(URL('show_all'))
    Message ="New Device"
    return dict(form=form,message=Message)

def show_all():
    # devices = db(db.device).select()
    db.device.id.readable = False
    grid = SQLFORM.grid(db.device,create=False,csv=False,editable = auth.has_membership('managers'),
                             deletable = auth.has_membership('managers'))
    return locals()

def show():
    device = db.device[request.args(0,cast=int)] or redirect(URL('index'))
    form = SQLFORM(db.device,device,readonly=True)
    return locals()

def show_by_name():
    response.view = "device/show.html"
    device = db(db.device.name==request.args(0)).select().first() or redirect(URL('index'))
    form = SQLFORM(db.device,device,readonly=True)
    return locals()

def flush():
    client = db.client(request.args(0,cast=int)) or redirect(URL('index'))
    if None == client:
        raise HTTP(400, "<h1>Client not finded,may deleted by others.<a href=\"%s\"><br/>Go back homepage</h1>"%(URL("index")))
    try:
        #delete the old device on this host?
        db(db.device.client == client.id).delete()
        for device,detail in db_rpc.show_device(client.url).items():
            device_id = device+"_"+detail["product"]
            #add the new device on this host
            raw = db(db.device.name==device_id).select().first()
            if None != raw:
                raw.update_record(display_id = detail["display_id"],
                                       build_date = detail["build_date"],product = detail["product"],
                                       region = detail["region"],hardware = detail["hardware"],
                                       build_type = detail["build_type"],host_name = client.id,build_version =detail["version"] )
            else:
                db.device.update_or_insert(name = device_id,display_id = detail["display_id"],
                                       build_date = detail["build_date"],product = detail["product"],
                                       region = detail["region"],hardware = detail["hardware"],
                                       build_type = detail["build_type"],client = client.id,build_version =detail["version"] )
            session.flash = T("Flush Devices Success!")
    except Exception, e:
        print e
        session.flash = T("Flush Devices FAILED!")
    redirect(URL('client','show_all',args=request.args(0,cast=int)))
    Message ="Flush all devices Success!"
    return dict(message=Message)

#---------------------------------------------legency-------------------------------------
def show_device():
    list_device = db(db.device.host_name==request.args[0]).select()
    if None == list_device:
        raise HTTP(400, "<h1>Record not finded,may deleted by others.<a href=\"%s\"><br/>Go back homepage</h1>"%(URL("index")))
    return dict(list_device = list_device)

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