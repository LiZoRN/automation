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
    db.survey.description.readable=False
    db.survey.choices.readable=False
    db.survey.name.represent = lambda a,row:A(a,_href=URL("take",args=row.uuid))
    grid = SQLFORM.grid(db.survey.created_by==auth.user_id,editable = False,create=False,deletable=False,
                        links=[lambda row:A("take",_href=URL("take",args=row.uuid),_class="btn"),
                               lambda row:A("results",_href=URL("results",args=row.uuid),_class="btn"),])
    return locals()

@auth.requires_login()
def create():
    def f(form):
        form.vars.results = [0]*len(request.vars.choices)
    from gluon.utils import web2py_uuid
    db.survey.uuid.default = uuid = web2py_uuid()
    form = SQLFORM(db.survey).process(onvalidation=f)
    if form.accepted:
        redirect(URL('take',args=uuid))
    return locals()

def take():
    uuid = request.args(0)
    survey =  db.survey(uuid=uuid)
    if survey.requires_login:
        if not auth.user:
            redirect(URL('user/login',vars=dict(_next=URL(args=request.args))))
        vote = db.vote(survey=survey.id,created_by=auth.user.id)
        if vote:
            session.flash="You voted aready!"
            redirect(URL('thank_you'))
    if request.vars:
        k = int(request.vars.choice)
        survey.results[k]+=1
        survey.update_record(results=survey.results)
        db.vote.insert(survey=survey.id)
        redirect(URL('thank_you'))
    return locals()

@auth.requires_login()
def results():
    uuid = request.args(0)
    survey =  db.survey(uuid=uuid)
    if survey.created_by and survey.created_by!=auth.user.id:
        session.flash="user not authorized"
        redirect(URL('index'))
    return locals()

def thank_you():
    return locals()

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
