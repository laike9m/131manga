# -*- coding:gbk -*-
#import urllib.request
import os
import pickle
from multiprocessing import Process, Pool
import httplib2
import parse_131
import fractions
from assistfunc import getThreeDigit
from concurrent import futures

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
                parseE1 = parse_131.parseEpisode()
                parseE2 = parse_131.parseEpisode()
                parseE3 = parse_131.parseEpisode()
                parseE4 = parse_131.parseEpisode()
                temppageurl = self.manga[key][0]    #���浱ǰ����ͼƬ������ҳurl
                N = self.manga[key][1]              #ҳ��

                '''��concurrent.futures����'''
                with futures.ThreadPoolExecutor(max_workers=4) as executor:
                    for i in range(1,int((N+1)/4)):
                        executor.submit(self.page_task,temppageurl,(i-1)*4+1,parseE1,episodedir,key)
                        executor.submit(self.page_task,temppageurl,(i-1)*4+2,parseE2,episodedir,key)
                        executor.submit(self.page_task,temppageurl,(i-1)*4+3,parseE3,episodedir,key)
                        executor.submit(self.page_task,temppageurl,(i-1)*4+4,parseE4,episodedir,key)
                    left = N+1-4*int((N+1)/4)   #���µ�ҳ��
                    if left:
                        if left == 1:
                            executor.submit(self.page_task,temppageurl,N,parseE1,episodedir,key)
                        elif left == 2:
                            executor.submit(self.page_task,temppageurl,N-1,parseE1,episodedir,key)
                            executor.submit(self.page_task,temppageurl,N,parseE2,episodedir,key)
                        elif left == 3:
                            executor.submit(self.page_task,temppageurl,N-2,parseE1,episodedir,key)
                            executor.submit(self.page_task,temppageurl,N-1,parseE2,episodedir,key)
                            executor.submit(self.page_task,temppageurl,N,parseE3,episodedir,key)
                        
    def page_task(self,temppageurl,i,parseE,episodedir,key):
        '''Ϊ����ThreadPoolExecutor,��ÿһҳ������д��һ��������,���ܲ��ܼӿ��ٶ�'''
        parts = temppageurl.split('/')
        parts.pop()
        parts.append(str(i)+'.html')
        temppageurl = '/'.join(parts)
        parseE.feed(temppageurl)
        localfile = open(os.path.join(episodedir,key+'-'+getThreeDigit(i)+'.jpg'),'wb')#ͼƬ����X��-i.jpg
        h = httplib2.Http('.cache')  #��������Ŀ¼�����Զ�����
        data = h.request(parseE.picurl)[1]
        localfile.write(data)
        localfile.close()
        self.schedule += fractions.Fraction(1,self.sumofpages) #ÿ������1/sumpages��ô��
        float_schedule = str(float(self.schedule))  #����û��ֱ�ӱ��str�������ȱ��float
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
                ���������������ʵ����û������        
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
        #����������,ʵ�ʵ�ÿһҳ���ɶ��߳�
        self.download(self.comicname, self.manga, self.localdir, self.webtype,self.pipeout,self.sumofpages)
            
    def download(self,comicname,manga,localdir,webtype,pipeout,sumofpages):
        #�������̵�����
        d = download(comicname,manga,localdir,webtype,pipeout,sumofpages)
        d.download()
                
if __name__ == '__main__':
    pass