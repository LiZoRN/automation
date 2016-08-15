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
response.generic_patterns = ['*'] if request.is_local else []

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
from gluon.contrib.login_methods.janrain_account import use_janrain
use_janrain(auth, filename='private/janrain.key')

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

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

STATUSES = ('assigned','accepted','rejected','reassigned','completed')

import datetime
week = datetime.timedelta(days=7)
db.define_table('task',
                Field('title',requires=IS_NOT_EMPTY()),
                Field('description','text'),
                Field('assigned_to','reference auth_user'),
                Field('status',requires=IS_IN_SET(STATUSES),default=STATUSES[0]),
                Field('deadline','datetime',default=request.now+week),
                auth.signature)

auth.enable_record_versioning(db)

db.define_table('post',
                Field('task','reference task'),
                Field('body','text',requires=IS_NOT_EMPTY()),
                auth.signature)
db.define_table('email',
                Field('sendto','list:string'),
                Field('subject'),
                Field('body','text'),
                Field('sender'),
                Field('status',requires=IS_IN_SET(('pending','sent','failed'))),
                auth.signature)

def fullname(user):
    if user == None:
        return "Unknown"
    return "%(first_name)s %(last_name)s"%user

def show_status(status,row=None):
    return SPAN(status,_class=status)

db.task.status.represent = show_status
db.task.created_on.represent = lambda v,row:SPAN(prettydate(v))
db.task.deadline.represent = lambda v,row:SPAN(prettydate(v),_class='overdue' if v<request.now else None)

def send_email_realtime(to,subject,message,sender):
    if not isinstance(to,list):to = [to]
    mail.settings.sender = sender
    return mail.send(to=to,subject=subject,message=message or '(no message)')

db.define_table('notify_email',
                Field('send_to','list:string'),
                Field('subject'),
                Field('msg','text'),
                Field('sender'),
                Field('status',requires=IS_IN_SET(('pending','sent','failed'))),
                Field('queued_datetime','datetime',default=request.now),
                Field('sent_on','datetime',default=None),
                auth.signature)

def send_email_deferred(to,subject,message,sender):
    if not isinstance(to,list):to = [to]
    db.email.insert(send_to=to,subject=subject,msg=message,sender=sender,
                    status='pending')
    scheduler.queue_task(send_pending_emails)


def send_pending_emails():
    rows = db(db.email.status=='pending').select()
    for row in rows:
        if send_email(to=row.send_to,subject=row.subject,message=row.msg,sender=row.sender):
            row.status = 'sent'
        else:
            row.status = 'failed'

EMAIL_POLICY = 'deferred'

def send_email(to,subject,message,sender):
    if EMAIL_POLICY == 'realtime':
        return send_email_realtime(to,subject,message,sender)
    else:
        return send_email_deferred(to,subject,message,sender)

