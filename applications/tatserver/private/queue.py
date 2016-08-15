# -*- coding: utf-8 -*-

import time
import datetime
while True:
    rows = db((db.test_plan.status=='pendding')&(db.test_plan.begin_time <= datetime.datetime.now())).select()
    for row in rows:
        try:
            print "start pending row"
            for d,p in dbfile.gen_plan(row).items():
                #db_rpc.test_start(db(db.device.name == d).select().first().client.url,p)
                db_rpc.test_download(db(db.device.name == d).select().first().client.url,p)
            row.update_record(status = "running")
        except:
            traceback.print_exc()
            row.update_record(status="idle")
        db.commit()
    print "tick tick!!"
    time.sleep(60) # check every minute
