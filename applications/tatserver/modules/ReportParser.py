
#-*- coding: UTF-8 -*-


import re
import os
import xmlrpclib

from xml.etree import ElementTree

def time_2_second(time):
    if time:
        time_list=time.split(':')
        sectime=((int(time_list[0]))*3600 + (int(time_list[1]))*60 + int(time_list[2]))
        return sectime
    else:
        return 0

def second_2_time(second):
    return "{:0>2d}".format(int(second/3600))+':'+"{:0>2d}".format(int(second%3600/60))+':'+"{:0>2d}".format(int(second%3600%60 ))


class Report():
    def __init__(self,data):
        if isinstance(data, file):
            self.data = ElementTree.fromstring(data.read())
            data.close()
        elif isinstance(data, str):
            self.data = ElementTree.fromstring(data)
        else:
            self.data = ElementTree.fromstring(data.data)
        self.case = {}

    def getTestType(self):
        try:
            return self.data.find("PLANTYPE").text
        except:
            return None
        
    def getPlanName(self):
        try:  
            return self.data.find("PLANNAME").text
        except:
            return None

    def getSW(self):
        try:
            return self.data.find("SW").text
        except:
            return None
        
    def getTestStatus(self):      
        try:
            return self.data.find("wStatus").text
        except:
            return None
        
    def getTimeStamp(self):
        try:  
            return self.data.find("TimeStamp").text
        except:
            return None

    def parser(self):
        self.type = self.getTestType()
        self.status = self.getTestStatus()
        self.name = self.getPlanName()
        self.sw = self.getSW()
        runtime = 0
        try:
            for case in self.data.find("CASES"):
                try:
                    loopnum = len(case.find("DATA"))
                    looptime = 0
                    #for index,data in enumerate(case.find("DATA")):
                    for data in case.find("DATA"):
                        time = data.find("TIME").text
                        runtime += time_2_second(time)
                        looptime += time_2_second(time)
                    self.case.update({case.find("NAME").text:{"passrate":str('%.2f'%float(case.find("SuccessRate").text)+"%"),"runtime":second_2_time(looptime),"avgtime":second_2_time((looptime/loopnum))}})
                except:
                    print "No LOOP Found!!!"
                    continue 
        except:
            print "No CASES Found!!!"         
        self.mtbf = second_2_time(runtime)

    def parse2dict(self):
        self.parser()
        return {"type":self.type,"mtbf":self.mtbf,"status":self.status,"case":self.case,"sw":self.sw,"planname":self.name}

    def dump(self):  
        print "Test type : %s"%self.type
        print "Test status : %s"%self.status
        print "Test mtbf : %s"%self.mtbf
        print "Test cases : %s"%self.case   
        print "sw : %s"%self.sw   
        print "name : %s"%self.name           
                            
if __name__ == '__main__':
    f = open(r"D:\TAT\server\agent2015\data\Logs\a700c245\20150211175647\TestData.xml","r")
    report = Report(f)
    report.parser()
    report.dump()



