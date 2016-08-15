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
    if auth.user: redirect(URL('tasks'))
    return dict(message=T('Hello World'))

def error(message="not authorized"):
    session.flash = message
    redirect(URL('index'))

def tasks():
    db.task.created_on.readable = True
    db.task.created_by.readable = True
    db.task.title.represent = lambda title,row:A(title,_href=URL('view_task',args=row.id))
    query = (db.task.assigned_to==me)|(db.task.created_by==me)
    grid = SQLFORM.grid(query,orderby=~db.task.modified_on,
                        details=False,editable=False,
                        deletable=lambda row:(row.created_by==me),
                        links=[
                            lambda row:A('view',_href=URL('view_task',args=row.id),_class='btn btn-primary')
                        ],
                        fields=[
                            db.task.status,
                            db.task.title,
                            db.task.created_on,
                            db.task.deadline,
                            db.task.created_by,
                            db.task.assigned_to
                        ])
    return locals()

@auth.requires_login()
def create_task():
    db.task.status.writable = False
    db.task.status.readable = False
    form = SQLFORM(db.task).process()
    if form.accepted:
        if form.vars.assigned_to!=me:
            email = db.auth_user(form.vars.assigned_to).email
            send_email(to=[email],sender=auth.user.email,
                      subject="New Task Assigned: %s" % form.vars.title,
                      message=form.vars.description)
        redirect(URL('tasks'))
    return locals()

@auth.requires_login()
def view_task():
    task_id = request.args(0,cast=int)
    task = db.task(task_id) or error()
    if not task.created_by==me and not task.assigned_to==me:error()
    db.post.task.default = task_id
    db.post.task.writable = db.post.task.readable = False
    form = SQLFORM(db.post).process()
    if form.accepted:
        user_id = task.created_by if task.assigned_to == me else task.assigned_to
        send_email(to=db.auth_user[user_id].email,sender=auth.user.email,
                  subject="New Comment About: %s" % task.title,message=form.vars.body)
    posts = db(db.post).select(orderby=db.post.created_on)
    return locals()

@auth.requires_login()
def edit_task():
    task_id = request.args(0,cast=int)
    task = db.task(task_id) or redirect(URL('index'))
    if not task.created_by==me and not task.assigned_to==me:error()
    if task.created_by == me:
        task.assigned_to.writable = True
    else:
        task.assigned_to.writable = False
        task.status.requires=IS_IN_SET(('accepted','rejected','reassigned','completed'))
    form = SQLFORM(db.task,task,deletable=(task.created_by==me)).process()
    if form.accepted:
        if task.created_by==me:
            email_to = db.auth_user(form.vars.assigned_to).email
        else:
            email_to = db.auth_user(task.created_by).email
        if True or email_to != me: #for debug use
            mail.settings.sender = auth.user.email
            mail.send(to=[email_to],
                      subject="Task Changed: %s" % form.vars.title,
                      message=form.vars.description or '(no description)')
        redirect(URL('view_task',args=task.id))
    return locals()


def delete_post():
    if request.env.request_method=="POST":
        post_id = request.vars.id
        post = db.post(post_id)
        if post and post.created_by == me:
            post.delete_record()
        return 'true'
    return 'false'

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
