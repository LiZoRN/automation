# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

POST_PER_PAGE = 10

def get_category():
    category_name = request.args(0)
    category = db.category(name=category_name)
    if not category:
        session.flash = 'page not found'
        redirect(URL('index'))
    return category

def index():
    rows = db(db.category).select()
    return locals()

@auth.requires_login()
def create():
    category = get_category()
    db.post.category.default = category.id
    form = SQLFORM(db.post).process(next='view/[id]')
    return locals()

@auth.requires_login()
def edit():
    id = request.args(0,cast=int)
    form = SQLFORM(db.post,id).process(next='view/[id]')
    return locals()

def view():
    id = request.args(0,cast=int)
    post = db.post(id)
    if auth.user:
        db.comm.post.default=id
        form=SQLFORM(db.comm).process()
    else:
        # form=A('login in to comment',_href=URL('user/login',vars=dict((URL('post','view',args=post.id)))))
        form=A('login in to comment',_href=URL('user/login'))
    comments = db(db.comm.post==post.id).select(orderby=~db.comm.created_on)
    return locals()

def list_by_datetime():
    response.view="post/list_by_votes.html"
    category = get_category()
    page = request.args(1,cast=int,default=0)
    start = page*POST_PER_PAGE
    stop = page+POST_PER_PAGE
    rows = db(db.post.category==category.id).select(orderby=~db.post.created_on,limitby=(start,stop))
    return locals()

def list_by_votes():
    category = get_category()
    page = request.args(1,cast=int,default=0)
    start = page*POST_PER_PAGE
    stop = page+POST_PER_PAGE
    rows = db(db.post.category==category.id).select(orderby=~db.post.votes,limitby=(start,stop))
    return locals()

def list_by_author():
    user_id = request.args(0,cast=int)
    page = request.args(1,cast=int,default=0)
    start = page*POST_PER_PAGE
    stop = page+POST_PER_PAGE
    rows = db(db.post.created_by==user_id).select(orderby=~db.post.created_on,limitby=(start,stop))

    return locals()

def vote_callback():
    vars = request.vars
    if vars:
        id = vars.id
        direction = +1 if vars.direction == 'up' else -1
        post = db.post(id)
        if post:
            vote = db.vote(post=id,created_by=auth.user.id)
            if not vote:

                post.update_record(votes=post.votes+direction)
                db.vote.insert(post=id,score=direction)
            elif vote.score!=direction:
                post.update_record(votes=post.votes+direction*2)
                vote.update_record(score=direction)
            else:
                pass
    return str(post.votes)


def comm_vote_callback():

    page = request.args(0,cast=int)
    direction = request.args(1)
    # todo
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
