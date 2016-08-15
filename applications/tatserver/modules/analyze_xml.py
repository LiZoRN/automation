#!/usr/bin/python
'''
analyze the XML, fetch the node value,and edit a xml doc to 
tell client the testplan version, tool version, and scripts
'''

    
from  xml.dom import  minidom
import os
from gluon import *
class xml(object):    
    def get_attrvalue(self, node, attrname):
        return node.getAttribute(attrname) if node else ''
    
    def get_nodevalue(self, node, index = 0):
        return node.childNodes[index].nodeValue if node else ''
    
    def get_xmlnode(self, node,name,sign):
        return node.getElementsByTagName(name) if node else ''
    
    def xml_to_string(self, filename='user.xml'):
        doc = minidom.parse(filename)
        return doc.toxml('UTF-8')
    
    def get_sub_node(self, node,node_search,sign):
        if sign=='toolversion':
            nodevalue=node[1].childNodes[0].nodeValue    
            return nodevalue  
        else:    
            clientname=[]
            scripts=[]
            for i in node:
                nodevalue=i.childNodes[0].nodeValue
                if node_search=='name':
                    clientname.append(nodevalue)
                elif node_search=='Case_File':
                    scripts.append(nodevalue)
                else:
                    return nodevalue
            if node_search=='name':
                return  clientname
            else:
                return  scripts
    
    def get_xml_data(self, filename='user.xml',node_search='Project',sign='appliversion'):
        doc = minidom.parse(filename) 
        root = doc.documentElement
        try:
            node=self.get_xmlnode(root,node_search,sign)
            return self.get_sub_node(node,node_search,sign)
        except:
            return ''
   
    def GenerateXml(self, clientname,planname):
        impl = minidom.getDOMImplementation()
        dom = impl.createDocument(None, 'Config', None)
        root = dom.documentElement  
       
        testplanE=dom.createElement('TESTPLAN')
        testplanT=dom.createTextNode(planname)
        testplanE.appendChild(testplanT)
        root.appendChild(testplanE)
       
        #for i in script:
            #scriptE=dom.createElement('script')
            #scriptT=dom.createTextNode(i)
            #scriptE.appendChild(scriptT)
            #root.appendChild(scriptE)
       
        
        os.system('mkdir /data/TAT/ClientName/' + clientname + ' >/dev/null 2>&1')
        os.system('touch /data/TAT/ClientName/' + clientname +'/currentpath.xml >/dev/null 2>&1')
        f= open('/data/TAT/ClientName/' + clientname+ '/currentpath.xml', 'w')
        dom.writexml(f,'\n',encoding='utf-8')
        f.close() 
