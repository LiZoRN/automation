
import pysvn
import time
import datetime
import re
import os
SVNURL = "https://172.16.11.192/svn/"
REPOSITORY = ["android5","android4"]   #we have two repository currently

TodayTime =  time.strftime("%Y-%m-%d", time.localtime()) 

class SvnScript:

    def __init__(self,workspace = r"..\script",svnurl = SVNURL,repositories = REPOSITORY):
        if not os.path.exists(workspace):
            os.makedirs(workspace)
        self.workspace = workspace
        self.svnurl = svnurl
        self.repositories = repositories
        self.client = pysvn.Client()
        #check out from svn
        # self.client.checkout()
    def list(self,url):
        "List the contents of a repository directory"
        for item in self.client.ls(url):
            print item.name
            print item.has_props
            print item.time
                                
    def update(self,path,flag="tags"):
        "Update the working copy" 
        self.client.update(os.path.join(path,flag))

    def pending_changes(self,path):
        "Determine pending changes"
        changes = self.client.status(path)
        print 'files to be added:'
        print [f.path for f in changes if f.text_status == pysvn.wc_status_kind.added]
        print 'files to be removed:'
        print [f.path for f in changes if f.text_status == pysvn.wc_status_kind.deleted]
        print 'files that have changed:'
        print [f.path for f in changes if f.text_status == pysvn.wc_status_kind.modified]
        print 'files with merge conflicts:'
        print [f.path for f in changes if f.text_status == pysvn.wc_status_kind.conflicted]
        print 'unversioned files:'
        print [f.path for f in changes if f.text_status == pysvn.wc_status_kind.unversioned]
    
    def determining_info(self):
        "Determining the repository info"
        for repository in self.repositories:
            entry = self.client.info(self.svnurl+repository)         
            print entry.url
            print entry.commit_revision.number
            print entry.commit_author
            print datetime.datetime.fromtimestamp(entry.commit_time)

    def check_svn_tag(self,tag):
        for repository in self.repositories:
            url = self.svnurl+repository
            for item in self.client.ls("%s/tags"%url):
                if (re.search(r"/%s$"%tag, item.name)!=None):
                    return repository
        return None

    def get_svn_tag(self):
        tags = {}
        for repository in self.repositories:
            url = self.svnurl+repository
            for item in self.client.ls("%s/tags"%url):
                try:
                    tags.update({re.findall(r"tags/(.*)$",item.name)[0]:item.name})
                except:
                    print "Find tags error!"
        return tags
 
    def get_script_by_tag(self,tag):
        "Get the script by tag"     
        begin = time.time()

        print("Check workspace....")
        for repository in self.repositories:
            path = os.path.join(self.workspace,repository,"tags")
            if not os.path.exists(path):
                print("Checkout from %s"%(SVNURL+repository))
                self.client.checkout(SVNURL+repository,os.path.join(self.workspace,repository))

        print("Get Script from workspace....") 
        for repository in self.repositories:
            for file in os.listdir(os.path.join(self.workspace,repository,"tags")):
                if tag == file:  
                    print("GET Script tag:%s Usage %s s"%(tag,(time.time()-begin)))
                    return os.path.join(path,file) 
                  
        print("The script is not in workspace,Sync to SVN Server....") 
        repository = self.check_svn_tag(tag)
        if None!=repository:
            repository_url= os.path.join(self.workspace,repository)
            self.update(repository_url)
            for file in os.listdir(os.path.join(repository_url,"tags")):
                if tag == file:  
                    print("Update&GET Script tag:%s Usage %s s"%(tag,(time.time()-begin)))
                    return os.path.join(path,file)      
        print("Failed to get Script by tag:%s Usage %s s"%(tag,(time.time()-begin)))
        
        
if __name__ == '__main__':

    pass