# -*- coding: utf-8 -*-
import traceback
import threading
class StabilityTask:

    instance=None
    mutex=threading.Lock()
    def __init__(self):
        print "stability task"
        StabilityTask.instance=self
        self.task = scheduler.queue_task(self.plan_task)

    @staticmethod
    def GetInstance():
        """Singleton"""
        if(StabilityTask.instance==None):
            StabilityTask.mutex.acquire()
            if(StabilityTask.instance==None):
                print('Init Instance')
                StabilityTask.instance=StabilityTask()
            else:
                print('Instance Exist!')
            StabilityTask.mutex.release()
        else:
            # print('Instance Exist!')
            pass
        return StabilityTask.instance

    def plan_task(self):
        while True:
            for row in db(db.test_plan).select():
                if row.status=="pending" and request.now>=row.begin_time:
                    try:
                        for d,p in dbfile.gen_plan(row).items():
                            db_rpc.test_start(db(db.device.name == d).select().first().client.url,p)
                            row.update_record(status = "running")
                    except:
                        traceback.print_exc()
                        row.update_record(status="idle")
            time.sleep(60)

#stabilitytask = StabilityTask.GetInstance()
