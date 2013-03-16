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
webtype:��վ�����ͣ���������ÿһҳ��url��������
131��  ҳ�� = ��ͬ����/n.html,ͼƬurl��ͨ��parse_131.parseEpisode��
'''

class download:
    '''
        ���ݲ�ֳɵ� list(��update_mangaforprocessor����)�������أ���������ÿһ�����ļ��У��������ӣ�
        ��������Ŀ¼������ͼƬ�ļ���д�룬ɾ������Ŀ¼������Ҳ�õ���parse131�࣬��Ϊÿһ��ͼƬ�� URL����Ҫ��
        ������ҳ��� html�����ȡ������Ҫfeed�� parse131
    webtype ������������վ�����ͣ�����Ϊ�Ժ����չ���Ľӿڣ�
    if self.webtype == '131' ���ж���131�����в��������Ҫ��չ������Ҫ��������(��178Ϊ��)
    if self.webtype == '178' Ȼ��������д��Ӧ��178�����ز�����
        ��ʵ���õķ�ʽ����ÿһ����վ�������඼ȥ�̳ж���������� multiprodownload������дdownload����
    '''
    def __init__(self,comicname,manga,localdir,webtype,pipeout,sumofpages):
        self.comicname = comicname          #����������
        self.manga = manga                  #manga�ֵ䣬��Ÿ�ʵ������Ҫ���صĸ�����Ϣ
        self.localdir = localdir          #���ش洢·��
        self.webtype = webtype
        self.pipeout = pipeout
        self.sumofpages = sumofpages    #������ҳ��
        self.schedule = fractions.Fraction(0,1)#���ؽ��ȼ�¼ 
        
    def makepagelist(self):
        #����webtype��manga������һ��������ҳ��
        pass
    
    def download(self):
        #�����ڱ��ش����洢�������ļ���
        self.localdir = os.path.join(self.localdir,self.comicname)
        if not os.path.exists(self.localdir): 
            os.mkdir(self.localdir)
        for key in self.manga:
            #����ÿһ�����ļ��У�ִ��ÿһ��������
            episodedir = os.path.join(self.localdir,key)
            if not os.path.exists(episodedir):
                os.mkdir(episodedir)
            if self.webtype == '131':
                #����131������
                parseE = parse_131.parseEpisode()
                temppageurl = self.manga[key][0]    #���浱ǰ����ͼƬ������ҳurl
                N = self.manga[key][1]              #ҳ��
                for i in range(1,N+1):
                    #ִ��ÿһ��ͼƬ������
                    if i > 1:
                        #���µ�ǰ����ͼƬ������ҳurl���㷨������/�ָ�����һ���ָĳ�i.html����ƴ����
                        parts = temppageurl.split('/')
                        parts.pop()
                        parts.append(str(i)+'.html')
                        temppageurl = '/'.join(parts)
                    parseE.feed(temppageurl)
                    localfile = open(os.path.join(episodedir,key+'-'+getThreeDigit(i)+'.jpg'),'wb')#ͼƬ����X��-i.jpg
                    #httplib2.debuglevel = 1         #��������ʱ��ʾ
                    h = httplib2.Http('.cache')  #��������Ŀ¼�����Զ�����
                    response,data = h.request(parseE.picurl)
                    localfile.write(data)
                    localfile.close()
                    #ÿ����һ��ͼƬ�����½�����
                    self.schedule += fractions.Fraction(1,self.sumofpages) #ÿ������1/sumpages��ô��
                    float_schedule = str(float(self.schedule))  #����û��ֱ�ӱ��str�������ȱ��float
                    #import pydevd;pydevd.settrace()
                    self.pipeout.send(float_schedule)

class multiprodownload():
    #���߳������࣬ͨ��
    def __init__(self,comicname,manga,localdir,webtype,pipeout):
        self.numofprocessor = int(os.popen('echo %NUMBER_OF_PROCESSORS%').read())#�����������������տ����Ľ�������
        self.comicname = comicname          #����������
        self.manga = manga                  #manga�ֵ䣬��Ÿ�ʵ������Ҫ���صĸ�����Ϣ
        self.localdir = localdir          #���ش洢·��
        self.webtype = webtype
        self.pipeout = pipeout
        self.numofepisode = len(manga)      #�ܻ���
        x = 0
        for value in manga.values():
            x = x + value[1]
        self.sumofpages = x         #��ҳ�����������������
             
    def update_mangaforprocessor(self):
        '''
                ���ݴ������������ܻ���������θ�ÿ�����̷�������
                ��ԭ���� manga�ֵ�ֳ�ÿ��������һ���ֵ䣬Ȼ������list
                ����������������list��������������������
                [
                 {��1��:[url_1,pages_1],��2��:[url_2,pages_2]},   //�����processor1
                 {��3��:[url_3,pages_3],��4��:[url_4,pages_4]}    //�����processor2
                ]
                
        '''
        self.mangaforprocessor = [] 
        average = self.numofepisode/self.numofprocessor
        int_average = int(self.numofepisode/self.numofprocessor)
        if average == int_average:
            #�����ܹ���������ֱ��ƽ������
            tempdict = {}
            count = 0
            for key in list(self.manga.keys()):
                tempdict[key] = self.manga[key]
                count = count + 1
                if count % average == 0:
                    #�����ˣ��Ͱ����tempdict����mangaforprocessor��Ȼ�����tempdict
                    self.mangaforprocessor.append(tempdict)
                    tempdict = {}
        else:
            #�������������Ȱ�int_average���䣬Ȼ����������ӵ�������������dict
            #int_average*self.numofprocessor�ǰ�����������������Ļ���������ľ���δ�����
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
        #���������
        self.update_mangaforprocessor()
        pool = Pool(processes = self.numofprocessor if self.numofprocessor<=4 else 4)      
        for i in range(self.numofprocessor):
            pool.apply_async(self.download, (self.comicname,self.manga,self.localdir,self.webtype))
        pool.close()
        pool.join()
        '''
        #���������أ�������
        self.download(self.comicname, self.manga, self.localdir, self.webtype,self.pipeout,self.sumofpages)
            
    def download(self,comicname,manga,localdir,webtype,pipeout,sumofpages):
        #�������̵�����
        #import pydevd;pydevd.settrace()
        d = download(comicname,manga,localdir,webtype,pipeout,sumofpages)
        d.download()
                
if __name__ == '__main__':
    '''
    test = download('ħ�����(���)�ճ�',
                    {'��һ��':['http://comic.131.com/content/16117/148636/1.html',29]},
                     'dir',
                    '131')
    test.download()
    '''
    with open('testpage_manga.pickle','rb') as f:
        manga = pickle.load(f)
    print(manga)
    testmulti = multiprodownload('ħ�����(���)�ճ�',
                                 manga,
                                 r'C:\Users\dell\Desktop',
                                 '131')
    testmulti.multiprodownload()