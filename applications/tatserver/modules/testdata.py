# -*- coding: utf-8 -*-
# from __future__ import division
from lxml import etree

def dictlist(node):
    res = {}
    res[node.tag] = []
    xmltodict(node, res[node.tag])
    reply = {}
    reply[node.tag] = {'value':res[node.tag], 'attributes':node.attrib}
    return reply

def xmltodict(node, res):
    rep = {}
    if len(node):
        # n = 0
        for n in list(node):
            rep[node.tag] = []
            value = xmltodict(n, rep[node.tag])
            if len(n):
                value = {'value':rep[node.tag], 'attributes':n.attrib}
                # print value
                res.append({n.tag:value})
            else :
                # print rep[node.tag][0]
                res.append(rep[node.tag][0])
    else:
        value = {}
        value = {'value':node.text, 'attributes':node.attrib}
        # print value
        res.append({node.tag:value})
    return

def fromstring(strdict=None):
    root = etree.fromstring(strdict)
    return dictlist(root)

def parse(filename=None):
    try:
        tree = etree.parse(filename)
        return dictlist(tree.getroot())
    except:
        etree.fromstring(open(filename).read())
     
def dict2xml(d):
    from xml.sax.saxutils import escape
    def unicodify(o):
        if o is None:
            return u'';
        return unicode(o)
    lines = ['"<?xml version=/"1.0 / " encoding=/"utf - 8 / "?>"']
    def addDict(node, offset):
        for name, value in node.iteritems():
            if name == "attributes":
                strqq = lines[len(lines) - 1]
                index = strqq.find(u"<")
                strqq = strqq[index + 1:len(strqq) - 1]
                for x, y in value.iteritems():
                    strqq = strqq + u" " *4 + u"%s='%s'" % (x, y)
                lines[len(lines) - 1] = u" " * index + u"<%s>" % (strqq)
            else:
                if isinstance(value, dict):
                    lines.append(offset + u"<%s>" % name)
                    addDict(value, offset + u" " * 4)
                    lines.append(offset + u"</%s>" % name)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            addDict(item, offset + u" " * 4)
                        else:
                            lines.append(offset + u"<%s>%s</%s>" % (name, escape(unicodify(item)), name))
                else:
                    if value != "":
                        pass
    addDict(d, u"")
    lines.append(u"")
    return u"/n".join(lines)   


def xml2dict(xml_string):
    tree = etree.fromstring(xml_string)
    return dictlist(tree)


def time_2_second(time):
    time_list=time.split(':')
    sectime=((int(time_list[0]))*3600 + (int(time_list[1]))*60 + int(time_list[2]))
    return sectime

def second_2_time(second):
    return str(second/3600)+':'+str(second%3600/60)+':'+str(second%3600%60 )


class TestData(object):
    
    def __init__(self,testdata):
        # try:
        self.tree = etree.fromstring(testdata.data)
        # self.tree = etree.parse(testdata)
        # except:
        #     self.tree = etree.fromstring(open(testdata).read())
        self.res = dictlist(self.tree)
        self.data = {}

    def __head_parse(self,res):
        for data in res['RESULTS']['value']:
            if data.has_key("PLANTYPE"):
                self.plan_type = data['PLANTYPE']['value']
            elif data.has_key("LOG"):
                self.log_dir = data['LOG']['value']
            elif data.has_key("CASES"):
                case = data['CASES']['value']
        return case

    def __loop_parse(self,loop):
        success_times = 0
        for data in loop['LOOP']['value']:
            if data.has_key("TIME"):
                runtime = time_2_second(data['TIME']['value'])
            elif data.has_key("SUCCESSTIMES"):
                success_times = int(data['SUCCESSTIMES']['value'])
        return (runtime,success_times)

    def __case_parse(self,case):
        total_runtime = 0
        total_success_time = 0
        passrate = "NA"
        avgtime = "NA"
        for data in case['Case']['value']:
            if data.has_key("NAME"):
                name = data['NAME']['value'].split("_")[-1]
            elif data.has_key("TOTALTIMES"):
                total_times = int(data['TOTALTIMES']['value'])
            elif data.has_key("DATA"):
                if data['DATA']['value']!=None:
                    loop_times = len(data['DATA']['value'])
                    for loop in data['DATA']['value']:
                        runtime,success_times = self.__loop_parse(loop)
                        total_runtime =total_runtime + runtime
                        total_success_time = total_success_time + success_times
        if total_times !=0:
            passrate = str('%.2f'%(float(total_success_time*100)/(total_times*loop_times))+"%")
            avgtime = str(second_2_time(total_runtime/loop_times))
        self.data[name]={"passrate":passrate,"runtime":str(second_2_time(total_runtime)),"avgtime":avgtime}
               
    def parse_data(self):      
        for cases in self.__head_parse(self.res):
            self.__case_parse(cases)                
    
        return self.data
if __name__ == '__main__':
    pass