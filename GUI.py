# -*- coding:gbk -*-
'''
注：这个文件在编译exe的时候要改名为131manhua，因为setup.py里面不能有中文
'''
from tkinter import *
import tkinter.ttk as ttk
import os
from tkinter.filedialog import askdirectory
import threading
import download_131

class MyThread(threading.Thread):
    #使下载的时候不阻塞tk的正常loop
    def __init__(self,url,dirname,webtype,showstate,pipeout):
        self.url = url
        self.dir = dirname
        self.showstate = showstate
        self.webtype = webtype
        self.pipeout = pipeout    #匿名管道的写入端
        threading.Thread.__init__(self)
    def run(self):
        #http://comic.131.com/content/shaonian/16117.html mowu
        from time import clock
        start = clock()
        test = download_131.download_131(self.url,self.dir,self.webtype,self.pipeout)
        test.finaldownload()
        end = clock()
        os.system('rd /S /Q %s'%('.cache'))  #用系统命令删除cache文件夹
        self.showstate['text'] = '下载完毕，共耗时%d秒'%(end-start)
        temp = '1000'
        os.write(self.pipeout,temp.encode())

def progressbar(pipein,progress):
    while True:
        schedule = float(os.read(pipein,32))
        if schedule <= 1:
            progress['value'] = 100 * schedule  #必须写['value']，.value不行
        else:
            break
  

class GUI:
    def __init__(self):
        self.tk = Tk()
        self.tk.resizable(0, 0)
        self.tk.title('131漫画下载器')
        self.tk.iconbitmap('icon2.ico')
        self.url = Entry(self.tk,width=60)
        self.url.grid(row=0,column=0,columnspan=2,padx=10,pady=5)
        
        self.button1 = Button(self.tk,text='选择存储路径',command=self.choosedir,width=7)
        self.button1.grid(row=1,column=0,padx=10,pady=5,sticky=W+S+N+E)
        
        self.storedir = Entry(self.tk,text='',width=33)
        self.storedir.grid(row=1,column=1,padx=10,pady=5,sticky=W+E+S+N)
        
        self.showstate = Label(self.tk,text='',font=('宋体', 10))
        self.showstate.grid(row=2,column=1,ipadx=10,ipady=5,sticky=W)
        
        self.progress = ttk.Progressbar(self.tk,orient="horizontal",mode="determinate")
        self.progress.grid(row=3,column=1,padx=10,pady=5,sticky=W+N+S+E)
        self.progress["maximum"] = 100  #maximum必须定义！不然是不存在的！
       
        self.button2 = Button(self.tk,text='开始下载',width=7,command=self.download)
        self.button2.grid(row=2,rowspan=2,column=0,pady=5,padx=10,sticky=W+S+N+E)

        
        self.tk.mainloop()
        
    def setflag_download(self):
        self.flag_download = 1

    def choosedir(self):
        self.storedir['state'] = NORMAL
        self.storedir.delete(0, END)
        self.dirname = askdirectory()
        self.storedir.insert(0, self.dirname)
        self.storedir['state'] = 'readonly' #'readonly'是可选不可改，DISABLED直接无法选择
    
    def download(self):
        self.progress['value'] = 0
        if self.url.get() == '':
            self.showstate['text'] = '请输入漫画主页面的地址'
            return
        if self.dirname == '':
            self.showstate['text'] = '请选择漫画保存的路径'
            return
        
        pipein,pipeout = os.pipe()
        threading.Thread(target=progressbar,args=(pipein,self.progress)).start()
        download_thr = MyThread(self.url.get(),self.dirname,'131',self.showstate,pipeout)
        self.showstate['text'] = 'downloading……'
        download_thr.start() #只要不用join，则不会阻塞原来的线程
        


if __name__ == '__main__':
    '''
        调试心得：
        无法下载，最可能的问题是漫画的标题出现了心的关键字，比如‘本’
    '''
    gui = GUI()
