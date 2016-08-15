# -*- coding: utf-8 -*-

db.define_table('category',Field('name'),requires=(IS_SLUG(),IS_LOWER(),IS_NOT_IN_DB(db,'category.name')))

db.define_table('post',
                Field('category','reference category',readable=False,writable=False),
                Field('title','string',requires=IS_NOT_EMPTY()),
                Field('url',requires=IS_EMPTY_OR(IS_URL())),
                Field('body','text'),
                Field('votes','integer',default=0,readable=False,writable=False),
                auth.signature)

db.define_table('vote',
               Field('post','reference post'),
               Field('score','integer',default=+1),
               auth.signature)

db.define_table('comm',
                Field('post','reference post',readable=False,writable=False),
                # Field('parent_comm','reference comm'),
                Field('votes','integer'),
                Field('body','text'),
                auth.signature)

db.define_table('comm_vote',
               Field('comm','reference comm'),
               Field('score','integer',default=+1),
               auth.signature)

def author(id):
    if id == None:
        return "Unknown"
    else:
        user = db.auth_user(id)
        return A('%(first_name)s %(last_name)s'%user,_href=URL("list_by_author",args=user.id))

from gluon.contrib.populate import populate
if db(db.auth_user).count()<2:
    populate(db.auth_user,100)
    db.commit()
if db(db.post).count()<2:
    populate(db.post,500)
    db.commit()
if db(db.comm).count()<2:
    populate(db.comm,1000)
    db.commit()