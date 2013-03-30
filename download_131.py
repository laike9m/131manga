# -*- coding:gbk -*-
import download
import urllib.request
import httplib2
import parse_131

class download_131(download.multiprodownload,parse_131.parse131):
    #�����̳���֮ǰ����ҳ���������ص��࣬�����������
    def __init__(self,url,localdir,webtype,pipeout,dontdownload=None):
        self.originalurl = url
        self.localdir = localdir
        self.webtype = webtype
        self.pipeout = pipeout
        self.dontdownload = dontdownload    #�����صķ־��б�
        parse_131.parse131.__init__(self,url)       #�����ͨ��self���ú�������ôself����ʡ��
        self.download_init()
        
    def myfeed(self):
        h = httplib2.Http('.cache')
        request,data = h.request(self.originalurl,headers={'accept-encoding':'gzip,identity'})
        #request,data = h.request(self.originalurl,headers={'accept-encoding':'gzip,identity','cache-control':'no-cache'})
        data = data.decode('utf-8')
        #data = urllib.request.urlopen(self.originalurl).read().decode('utf-8')
        self.feed(data) #���feed����ԭʼ��feed
        
    def download_init(self):
        '''����ǰ�ĳ�ʼ���������������ṹ���õ�self.manga��self.comicname'''
        self.myfeed()
        '''�����Ѿ��õ���self.manga,����dontdownload��manga����ɾ�������dondownload��None��ô�Ͳ�ɾ��'''
        if self.dontdownload:
            for key in list(self.manga.keys()):
                if key in self.dontdownload:
                    del self.manga[key]
        self.getNumOfPages()    
        download.multiprodownload.__init__(self,self.comicname,self.manga,self.localdir,self.webtype,self.pipeout)
        
    def finaldownload(self):
        #��finaldownload����Ȼ��multiprodownload���download���������鷳
        self.multiprodownload()

        
if __name__ == '__main__':
    pass