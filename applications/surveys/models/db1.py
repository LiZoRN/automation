# -*- coding: utf-8 -*-

db.define_table('survey',
                Field('name',requires=IS_NOT_EMPTY()),
                Field('description','text',requires=IS_NOT_EMPTY()),
                Field('choices','list:string'),
                Field('requires_login','boolean',default=True),
                Field('results','list:integer',writable=False),
                Field('uuid',writable=False),
                auth.signature)

db.define_table('vote',
                Field('survey','reference survey'),
                auth.signature)