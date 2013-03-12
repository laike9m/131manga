# -*- coding:gbk -*-
import download
import urllib.request
import httplib2
import parse_131

class download_131(download.multiprodownload,parse_131.parse131):
    #这个类继承了之前对网页分析和下载的类，完成所有任务
    def __init__(self,url,localdir,webtype,pipeout):
        self.originalurl = url
        self.localdir = localdir
        self.webtype = webtype
        self.pipeout = pipeout
        parse_131.parse131.__init__(self,url)       #如果不通过self调用函数，那么self不能省略
        self.download_init()
        
    def myfeed(self):
        h = httplib2.Http('.cache')
        request,data = h.request(self.originalurl,headers={'accept-encoding':'gzip,identity'})
        #request,data = h.request(self.originalurl,headers={'accept-encoding':'gzip,identity','cache-control':'no-cache'})
        data = data.decode('utf-8')
        #data = urllib.request.urlopen(self.originalurl).read().decode('utf-8')
        self.feed(data) #这个feed就是原始的feed
        
    def download_init(self):
        #下载前的初始化，分析出漫画结构，得到self.manga，self.comicname
        self.myfeed()
        self.getNumOfPages()    
        download.multiprodownload.__init__(self,self.comicname,self.manga,self.localdir,self.webtype,self.pipeout)
        
    def finaldownload(self):
        #叫finaldownload，不然和multiprodownload类的download重名，很麻烦
        self.multiprodownload()
        
if __name__ == '__main__':
    from time import clock
    start = clock()
    #http://comic.131.com/content/shaonian/16117.html mowu
    test = download_131('http://comic.131.com/content/shaonian/16740.html',
                        r'C:\Users\dell\Desktop',
                        '131')
    test.finaldownload()
    end = clock()
    print(end-start) #以微秒计
    #print('下载完毕')