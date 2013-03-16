# -*- coding:gbk -*-
#import urllib.request
import os
import pickle
from multiprocessing import Process, Pool
import httplib2
import parse_131
import fractions
from assistfunc import getThreeDigit
'''
webtype:网站的类型，用来区分每一页的url命名规律
131：  页面 = 相同部分/n.html,图片url得通过parse_131.parseEpisode找
'''

class download:
    '''
        根据拆分成的 list(见update_mangaforprocessor函数)进行下载，包括创建每一话的文件夹，建立连接，
        创建缓存目录，创建图片文件并写入，删除缓存目录。其中也用到了parse131类，因为每一张图片的 URL都需要从
        它所在页面的 html里面获取，即需要feed给 parse131
    webtype 参数表明了网站的类型，这是为以后的扩展留的接口：
    if self.webtype == '131' 中有对于131的所有操作，如果要扩展，就需要加入例如(以178为例)
    if self.webtype == '178' 然后在里面写对应于178的下载操作。
        其实更好的方式是让每一个网站的下载类都去继承多进程下载类 multiprodownload，并重写download方法
    '''
    def __init__(self,comicname,manga,localdir,webtype,pipeout,sumofpages):
        self.comicname = comicname          #漫画的名字
        self.manga = manga                  #manga字典，存放该实例所需要下载的各话信息
        self.localdir = localdir          #本地存储路径
        self.webtype = webtype
        self.pipeout = pipeout
        self.sumofpages = sumofpages    #总漫画页数
        self.schedule = fractions.Fraction(0,1)#下载进度记录 
        
    def makepagelist(self):
        #根据webtype和manga把任意一话的所有页的
        pass
    
    def download(self):
        #用来在本地创建存储漫画的文件夹
        self.localdir = os.path.join(self.localdir,self.comicname)
        if not os.path.exists(self.localdir): 
            os.mkdir(self.localdir)
        for key in self.manga:
            #创建每一话的文件夹，执行每一话的下载
            episodedir = os.path.join(self.localdir,key)
            if not os.path.exists(episodedir):
                os.mkdir(episodedir)
            if self.webtype == '131':
                #处理131的下载
                parseE = parse_131.parseEpisode()
                temppageurl = self.manga[key][0]    #保存当前下载图片所在网页url
                N = self.manga[key][1]              #页数
                for i in range(1,N+1):
                    #执行每一张图片的下载
                    if i > 1:
                        #更新当前下载图片所在网页url，算法是先以/分割，把最后一部分改成i.html，再拼起来
                        parts = temppageurl.split('/')
                        parts.pop()
                        parts.append(str(i)+'.html')
                        temppageurl = '/'.join(parts)
                    parseE.feed(temppageurl)
                    localfile = open(os.path.join(episodedir,key+'-'+getThreeDigit(i)+'.jpg'),'wb')#图片名：X话-i.jpg
                    #httplib2.debuglevel = 1         #发送请求时显示
                    h = httplib2.Http('.cache')  #创建缓存目录，会自动清理
                    response,data = h.request(parseE.picurl)
                    localfile.write(data)
                    localfile.close()
                    #每下完一张图片，更新进度条
                    self.schedule += fractions.Fraction(1,self.sumofpages) #每次增加1/sumpages这么多
                    float_schedule = str(float(self.schedule))  #分数没法直接变成str，所以先变成float
                    #import pydevd;pydevd.settrace()
                    self.pipeout.send(float_schedule)

class multiprodownload():
    #多线程下载类，通用
    def __init__(self,comicname,manga,localdir,webtype,pipeout):
        self.numofprocessor = int(os.popen('echo %NUMBER_OF_PROCESSORS%').read())#处理器数量，即最终开出的进程数量
        self.comicname = comicname          #漫画的名字
        self.manga = manga                  #manga字典，存放该实例所需要下载的各话信息
        self.localdir = localdir          #本地存储路径
        self.webtype = webtype
        self.pipeout = pipeout
        self.numofepisode = len(manga)      #总话数
        x = 0
        for value in manga.values():
            x = x + value[1]
        self.sumofpages = x         #总页数，用来计算进度条
             
    def update_mangaforprocessor(self):
        '''
                根据处理器数量和总话数决定如何给每个进程分配任务
                将原来的 manga字典分成每个处理器一个字典，然后存入该list
                最后生成形如下面的list（假设有两个处理器）
                [
                 {第1话:[url_1,pages_1],第2话:[url_2,pages_2]},   //分配给processor1
                 {第3话:[url_3,pages_3],第4话:[url_4,pages_4]}    //分配给processor2
                ]
                
        '''
        self.mangaforprocessor = [] 
        average = self.numofepisode/self.numofprocessor
        int_average = int(self.numofepisode/self.numofprocessor)
        if average == int_average:
            #正好能够整除，则直接平均分配
            tempdict = {}
            count = 0
            for key in list(self.manga.keys()):
                tempdict[key] = self.manga[key]
                count = count + 1
                if count % average == 0:
                    #够数了，就把这个tempdict插入mangaforprocessor，然后清空tempdict
                    self.mangaforprocessor.append(tempdict)
                    tempdict = {}
        else:
            #不能整除，则先按int_average分配，然后再依次添加到各个处理器的dict
            #int_average*self.numofprocessor是按照整数部分来分配的话数，后面的就是未分配的
            tempdict = {}
            count = 0
            mangalist = list(self.manga.keys())
            for key in mangalist[0:int_average*self.numofprocessor]:
                tempdict[key] = self.manga[key]
                count = count + 1
                if count % int_average == 0:
                    self.mangaforprocessor.append(tempdict)
                    tempdict = {}
            count = 0
            for key in mangalist[int_average*self.numofprocessor:]:
                self.mangaforprocessor[count][key] = self.manga[key]
                count = count + 1
                
    def multiprodownload(self):
        '''
        #多进程下载
        self.update_mangaforprocessor()
        pool = Pool(processes = self.numofprocessor if self.numofprocessor<=4 else 4)      
        for i in range(self.numofprocessor):
            pool.apply_async(self.download, (self.comicname,self.manga,self.localdir,self.webtype))
        pool.close()
        pool.join()
        '''
        #单进程下载，测试用
        self.download(self.comicname, self.manga, self.localdir, self.webtype,self.pipeout,self.sumofpages)
            
    def download(self,comicname,manga,localdir,webtype,pipeout,sumofpages):
        #单个进程的下载
        #import pydevd;pydevd.settrace()
        d = download(comicname,manga,localdir,webtype,pipeout,sumofpages)
        d.download()
                
if __name__ == '__main__':
    '''
    test = download('魔物娘的(相伴)日常',
                    {'第一话':['http://comic.131.com/content/16117/148636/1.html',29]},
                     'dir',
                    '131')
    test.download()
    '''
    with open('testpage_manga.pickle','rb') as f:
        manga = pickle.load(f)
    print(manga)
    testmulti = multiprodownload('魔物娘的(相伴)日常',
                                 manga,
                                 r'C:\Users\dell\Desktop',
                                 '131')
    testmulti.multiprodownload()