# -*- coding:gbk -*-
'''
ע������ļ��ڱ���exe��ʱ��Ҫ����Ϊ131manhua����Ϊsetup.py���治��������
'''
from tkinter import *
import tkinter.ttk as ttk
import os
from tkinter.filedialog import askdirectory
import threading
from multiprocessing import Process,Pipe
import download_131

class MyDownloadProcess(Process):
    #ʹ���ص�ʱ������tk������loop
    def __init__(self,url,dirname,webtype,pipeout):
        self.url = url
        self.dir = dirname
        self.webtype = webtype
        self.pipeout = pipeout    #�����ܵ���д���
        Process.__init__(self)
    def run(self):
        test = download_131.download_131(self.url,self.dir,self.webtype,self.pipeout)
        test.finaldownload()
        os.system('rd /S /Q %s'%('.cache'))  #��ϵͳ����ɾ��cache�ļ���
        temp = '1000'
        self.pipeout.send(temp)

def progressbar(pipein,progress,showstate):
    from time import clock
    k = 0
    while True:
        schedule = float(pipein.recv())
        if schedule > 0 and k == 0:
            k = 1
            start = clock()
        if schedule <= 1:
            progress['value'] = 100 * schedule  #����д['value']��.value����
        else:
            end = clock()
            showstate['text'] = '������ϣ�����ʱ%d��'%(end-start)
            break
  

class GUI:
    def __init__(self):
        self.tk = Tk()
        self.tk.resizable(0, 0)
        self.tk.title('131����������')
        self.tk.iconbitmap('icon2.ico')
        self.url = Entry(self.tk,width=60)
        self.url.grid(row=0,column=0,columnspan=2,padx=10,pady=5)
        
        self.button1 = Button(self.tk,text='ѡ��洢·��',command=self.choosedir,width=7)
        self.button1.grid(row=1,column=0,padx=10,pady=5,sticky=W+S+N+E)
        
        self.storedir = Entry(self.tk,text='',width=33)
        self.storedir.grid(row=1,column=1,padx=10,pady=5,sticky=W+E+S+N)
        
        self.showstate = Label(self.tk,text='',font=('����', 10))
        self.showstate.grid(row=2,column=1,ipadx=10,ipady=5,sticky=W)
        
        self.progress = ttk.Progressbar(self.tk,orient="horizontal",mode="determinate")
        self.progress.grid(row=3,column=1,padx=10,pady=5,sticky=W+N+S+E)
        self.progress["maximum"] = 100  #maximum���붨�壡��Ȼ�ǲ����ڵģ�
       
        self.button2 = Button(self.tk,text='��ʼ����',width=7,command=self.download)
        self.button2.grid(row=2,rowspan=2,column=0,pady=5,padx=10,sticky=W+S+N+E)

        
        self.tk.mainloop()
        
    def setflag_download(self):
        self.flag_download = 1

    def choosedir(self):
        self.storedir['state'] = NORMAL
        self.storedir.delete(0, END)
        self.dirname = askdirectory()
        self.storedir.insert(0, self.dirname)
        self.storedir['state'] = 'readonly' #'readonly'�ǿ�ѡ���ɸģ�DISABLEDֱ���޷�ѡ��
    
    def download(self):
        self.progress['value'] = 0
        if self.url.get() == '':
            self.showstate['text'] = '������������ҳ��ĵ�ַ'
            return
        if self.dirname == '':
            self.showstate['text'] = '��ѡ�����������·��'
            return
        
        pipein,pipeout = Pipe()
        threading.Thread(target=progressbar,args=(pipein,self.progress,self.showstate)).start()
        download_process = MyDownloadProcess(self.url.get(),self.dirname,'131',pipeout)
        self.showstate['text'] = 'downloading����'
        download_process.start() #ֻҪ����join���򲻻�����ԭ�����߳�

        


if __name__ == '__main__':
    '''
        �����ĵã�
        �޷����أ�����ܵ������������ı���������ĵĹؼ��֣����确����
    '''
    gui = GUI()
