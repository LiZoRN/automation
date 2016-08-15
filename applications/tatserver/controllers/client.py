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
    form = SQLFORM(db.client)
    if form.accepts(request.post_vars,session):
        session.flash = 'client created ok'
        redirect(URL('show_all'))
    message ="New Client"
    return locals()


def delete():
    """delete an existing client"""
    row = db.client[request.args(0)]
    form = SQLFORM(db.client, row, deletable=True,showid=False)
    if form.process().accepted:
        response.flash = 'record delete'
        redirect(URL('show_clients'))
    return dict(form=form)

def edit():
     """edit an existing client"""
     this_page = db.client(request.args(0,cast=int)) or redirect(URL('index'))
     form = SQLFORM(db.client, this_page, deletable=True,showid=False).process(
         next = URL('show_all',args=request.args))
     return dict(form=form)

def clients_attached(id):
    links = []
    for row in db(db.device.host_name==id).select():
        links.append(A(B(T(row.name)), _href=URL('device','show',args=row.id)))
    print links
    return links

def show_all():
    clients = db(db.client).select()
    # db.client.id.readable = False
    # grid = SQLFORM.grid(db.client,create=False,csv=False,editable = auth.has_membership('managers'),
    #                          deletable = auth.has_membership('managers'),
    #                          links= [lambda row:clients_attached(row.id)])
    return locals()

def show():
    client = db.client(request.args(0,cast=int)) or redirect(URL('index'))
    return dict(client =client)

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