# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

from ReportParser import Report,time_2_second,second_2_time
import json

def index():
    response.flash = T("Welcome to TAT Server!")
    return dict(message=T('Hello World'))

def mem_analysis(db_meminfo):
    return json.dumps(eval(db_meminfo.memory_data))

def current():
    #db_meminfo = db(db.meminfo.device_report == request.args(0,cast=int)).select().first() or redirect(URL('index'))
    db_meminfo = db(db.meminfo.device_report == request.args(0,cast=int)).select().first()
    json_memdata = mem_analysis(db_meminfo)
    return locals()

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
