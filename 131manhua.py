# -*- coding:gbk -*-
'''
ע������ļ��ڱ���exe��ʱ��Ҫ����Ϊ131manhua����Ϊsetup.py���治��������
'''
from tkinter import *
from tkinter import font
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from PIL import Image,ImageTk
import os,sys
from tkinter.filedialog import askdirectory
import threading
from multiprocessing import Process,Pipe,freeze_support
import parse_131
import httplib2
import download_131
import webbrowser

class MyDownloadProcess(Process):
    #ʹ���ص�ʱ������tk������loop.�����������ؽ���
    def __init__(self,url,dirname,dontdownloadlist,webtype,pipeout):#tkinter�Ŀؼ����ܱ�pickle
        self.url = url
        self.dir = dirname
        self.webtype = webtype
        self.pipeout = pipeout    #�����ܵ���д���
        self.buttonlist = []
        self.dontdownloadlist = dontdownloadlist   #�����صķ־��б�
        Process.__init__(self)
        
    def run(self):
        test = download_131.download_131(self.url,self.dir,self.webtype,self.pipeout,self.dontdownloadlist)
        test.finaldownload()
        os.system('rd /S /Q %s'%('.cache'))  #��ϵͳ����ɾ��cache�ļ���
        temp = '1000'
        self.pipeout.send(temp)        
        sys.stdout.flush()   
        sys.stderr.flush()

class MyDownloadProcess_many(Process):
    #�ಿ�������ؽ���
    def __init__(self,url_list,name_list,dirname,webtype,pipeout):
        self.url_list = url_list
        self.name_list = name_list
        self.dir = dirname
        self.webtype = webtype
        self.pipeout = pipeout    #�����ܵ���д���
        Process.__init__(self)
    
    def run(self):
        for url in self.url_list:
            temp = 'name ' + self.name_list[self.url_list.index(url)] #��ȡ��ǰ���ص�����������,����ȥ
            self.pipeout.send(temp)
            test = download_131.download_131(url,self.dir,self.webtype,self.pipeout)
            test.finaldownload() 
            if url == self.url_list[-1]:
                temp = '1000'
            else:
                temp = '100'
            self.pipeout.send(temp)
        os.system('rd /S /Q %s'%('.cache'))  #��ϵͳ����ɾ��cache�ļ���
        sys.stdout.flush()   
        sys.stderr.flush()

def progressbar(pipein,progress,showstate):
    from time import clock
    k = 0
    while True:
        content = pipein.recv()
        if content.startswith('name '):
            showstate['text'] = '��������' + content.split()[1]
        else:
            schedule = float(content)
            if schedule > 0 and k == 0:
                k = 1
                start = clock()
            if schedule <= 1:
                progress['value'] = 100 * schedule  #����д['value']��.value����
            elif schedule < 500:    #��Զಿ��������ʱ,����������һ��������Ҫ�˳�progressbar�߳�
                pass
            else:
                end = clock()
                showstate['text'] = '������ϣ�����ʱ%d��'%(end-start)
                progress['value'] = 100
                break
  

class GUI:
    def __init__(self):
        self.edition = 2.0
        self.tk = Tk()
        self.notebook = ttk.Notebook(self.tk)
        self.notebook.grid(column=0,columnspan=2,row=0)
        self.pane1 = Frame(self.notebook)    #�ѵ����������ط��ڵ�һ��pane����
        self.pane2 = Frame(self.notebook)    #�ڶ���pane�Ƕಿ��������
        self.tk.resizable(0, 0)
        self.tk.title('131����������')
        self.tk.iconbitmap('icon2.ico')
        self.dirname = ''
        
        self.notebook.add(self.pane1,text='������������')
        self.notebook.add(self.pane2,text='�ಿ��������')
        
        self.url = Entry(self.pane1,width=60)
        self.url.grid(row=0,column=0,columnspan=3,padx=(10,5),pady=5,sticky=W+E)
        
        '''pane1���ķ���ͼƬ'''
        self.cover = Canvas(self.pane1,height=320,width=240)
        self.cover.grid(row=1,column=0,rowspan=2,padx=(9,0),sticky=W)
        img = Image.open('img/mr.jpg')
        img = ImageTk.PhotoImage(img)
        self.cover.create_image(0,0,image=img,anchor=NW)    
        '''
        pane1�Ҳ�������־��б�,���漸�д�������stackoverflow
                ��һ��˵���˰�scrollbar�󶨵��ؼ��ϵķ���,���趨widget��x/yscrollcommand����Ϊsb.set
                ��sb��command����Ϊwidget.x/yview
                ��,����Ҫ��һ����,��Ҫ��pack����sb�ŵ��ؼ���,��Ӧ����sb�Ϳؼ���ͬ���ĵȼ�(��parent��ͬ),
                �ú���grid���ж���
        '''
        self.directory = Text(self.pane1,width=23,height=22,cursor='arrow')
        self.vsb = Scrollbar(self.pane1,orient="vertical")
        self.directory.config(yscrollcommand=self.vsb.set)
        self.vsb.config(command=self.directory.yview)
        self.directory.grid(column=1,row=1,sticky=N+S+E+W,padx=(4,0),pady=(1,0))
        self.vsb.grid(column=2,row=1,sticky=N+S,padx=(0,5),pady=1)
        self.l_chkbuttons = []    #����button��list,������,��Ӧ����
        self.r_chkbuttons = []
        self.l_start = 0
        self.r_start = 0
        '''pane1�Ҳ��ȫѡ/��ѡcheckbox'''
        self.quicksel = Canvas(self.pane1)
        self.quicksel.grid(row=2,column=1)
        self.var_selall = IntVar()
        self.var_selall.trace('w',lambda name,index,op,x=self.var_selall: self.do_selall(x))
        self.selall = Checkbutton(self.quicksel,text='ȫѡ',var=self.var_selall)
        self.selall.pack(side=LEFT,fill=BOTH)
        self.var_inversesel = IntVar()
        self.var_inversesel.trace('w',self.do_inversesel)
        self.inversesel = Checkbutton(self.quicksel,text='��ѡ',var=self.var_inversesel)
        self.inversesel.pack(side=LEFT,fill=BOTH)
        self.seltip = Label(self.quicksel,text='������shift��ѡ��',fg='lightblue')
        self.seltip.pack(side=LEFT)
        
        '''pane2'''
        self.list = Listbox(self.pane2,selectmode=EXTENDED,width=67,height=20,activestyle='none',bd=0)
        self.list.grid(row=0,column=0,sticky=N+S+W+E)
        self.sb2 = Scrollbar(self.pane2,command=self.list.yview, orient='vertical')
        self.list.config(yscrollcommand=self.sb2.set)
        self.sb2.grid(row=0,column=1,sticky=N+S)
        
        self.popup = Menu(self.list,tearoff=0)    #listbox�ϵ��Ҽ������˵�
        self.popup.add('command',label='ɾ��',command=self.delete)
        self.popup.add('command',label='ȫ�����',command=self.delete_all)
        self.list.bind('<Button-3>',self.do_popup)
        
        self.button1 = Button(self.tk,text='ѡ��洢·��',command=self.choosedir,width=7)
        self.button1.grid(row=1,column=0,padx=(10,0),pady=5,sticky=W+S+N+E)
        
        self.storedir = Entry(self.tk,text='',width=33)
        self.storedir.grid(row=1,column=1,padx=10,pady=5,sticky=W+E+S+N)
        
        self.showstate = Label(self.tk,text='',font=('����', 10))
        self.showstate.grid(row=2,column=1,ipadx=10,ipady=5,sticky=W)
        
        self.progress = ttk.Progressbar(self.tk,orient="horizontal",mode="determinate")
        self.progress.grid(row=3,column=1,padx=10,pady=5,sticky=W+N+S+E)
        self.progress["maximum"] = 100  #maximum���붨�壡��Ȼ�ǲ����ڵģ�
       
        self.button2 = Button(self.tk,text='��ʼ����',width=7,command=self.download)
        self.button2.grid(row=2,rowspan=2,column=0,pady=5,padx=(10,0),sticky=W+S+N+E)
        
        '''����ʾ����ʾ���°汾'''
        h = httplib2.Http('.cache')
        edition_latest = h.request('http://42.120.19.204/download/edition.txt')[1].decode()
        if float(edition_latest) > self.edition:
            f = font.Font(self.showstate,self.showstate.cget('font'))#��SO���Ĵ���,��ȡ�ؼ��е�����
            f.configure(underline = True)
            self.showstate.configure(font=f,)
            self.showstate.config(text='���°汾,����鿴',fg='blue') 
            self.showstate.bind('<Button-1>',self.getnewversion)
        else:
            self.showstate.config(text='�������°汾')
        
        self.last_content = ''  #�洢������֮ǰ�Ǵε�����,��ֹ�����ظ�������
        self.tk.after(2000,lambda:self.watch_clipboard())
        self.tk.protocol("WM_DELETE_WINDOW", self.winclose) #������رմ���ʱ�Ĳ���
        self.tk.mainloop()
    
    def getnewversion(self,event):
        webbrowser.open('http://bbs.131.com/thread-2607756-1-1.html')
        f = font.Font(self.showstate,self.showstate.cget('font'))#��SO���Ĵ���,��ȡ�ؼ��е�����
        f.configure(underline = False)
        self.showstate.configure(font=f)
        self.showstate.config(fg='black') 
        self.showstate.unbind('<Button-1>')
        self.showstate.config(text='������ʧЧ,��ֱ�ӵ�����������')
    
    def winclose(self):
        if messagebox.askokcancel("Quit", "�˳�131��������?"):
            if os.path.exists('cover.jpg'):
                os.remove('cover.jpg')  #ɾ��֮ǰ����ķ���ͼƬ
            self.tk.destroy()
    
    def watch_clipboard(self):  
        '''
        http://comic.131.com/content/shaonian/16051.html
                ���Ӽ����壬Ҫɸѡ��������URLȻ���Զ�������Ӧ��λ�ã���׼���£�
            (1) �Ȱ�http://�ߵ���Ȼ����'/'�ָ����Ϊ4
            (2) ��һ����comic.131.com
            (3) �ڶ�����content
        '''
        content = '' 
        ifadd = 0
        try:
            content = self.tk.clipboard_get()
        except TclError:
            pass
        parts = content.lstrip('http://').split('/')
        if self.last_content != content:
            if len(parts) == 4:
                if parts[0] == 'comic.131.com':
                    if parts[1] == 'content':
                        self.last_content = content
                        self.tk.clipboard_clear()
                        ifadd = messagebox.askokcancel('','���ⲿ�������������б�',default='ok')#ѡok����True
        if ifadd:
            self.showstate.config(text='���ڷ��������ṹ,���Ե�')
            temp_instance = parse_131.parse131(content)
            h = httplib2.Http('.cache')
            data = h.request(content)[1].decode()   #д��ͼƬ�ö��������ݾ����������,����feedҪ����
            temp_instance.feed(data)
            
            '''���ݵ�ǰѡ����tab����URLճ����λ��'''
            if self.notebook.select() == str(self.pane1):#����windowname���ж�ѡ���pane
                self.l_chkbuttons = []
                self.r_chkbuttons = []
                self.directory.delete('1.0', END)   #1.0�����һ�е�һ�е��ַ�,�����'�ַ�'����checkbox
                self.url.delete(0,END)
                self.url.insert(0,content + ' ' + temp_instance.comicname)    #����entry
                img = open('cover.jpg','wb')
                cover_data = h.request(temp_instance.coverimage)[1]
                img.write(cover_data)
                img.close()           
                img = Image.open('cover.jpg')#�����õ�PIL��,��Ϊtk�Դ���PhotoImage�޷���jpg
                img = ImageTk.PhotoImage(img)
                self.cover.image = img  #���������һ����޷���ʾ,ԭ��μ��ʼǡ�The Tkinter PhotoImage Class��
                self.cover.create_image(0,0,image=img,anchor=NW)
                '''�ѷ־���Ϣд��self.directory,ʵ���ǲ���һ��checkbox��directory��.���ݷ־���Ŀ����ż��,���в��'''
                volumes = list(temp_instance.manga.keys())
                volumes.sort()  #ע��,sort���޸�ԭ����list
                amount = len(volumes)   #�־���
                should_add = int(amount/2 if amount%2==0 else (amount+1)/2)  #������ʾ,ͬ���ұ�����ű���ߴ����
                i = 0
                for i in range(should_add-1):
                    tempvar1 = IntVar()
                    tempvar2 = IntVar()
                    cb_left = Checkbutton(self.directory,padx=0,pady=0,bd=0,text=volumes[i],bg='white',var=tempvar1)
                    cb_left.var = tempvar1  #�����������,����Ϊtempvar�Ǿֲ�����,����ѭ��֮���unbind��,var����Ҳû�ˡ���ͼƬһ����
                    self.l_chkbuttons.append(cb_left)
                    cb_left.bind('<Button-1>', self.l_selstart)         #����shiftѡ��ĺ���
                    cb_left.bind('<Shift-Button-1>', self.l_selrange)
                    cb_right = Checkbutton(self.directory,padx=0,pady=0,bd=0,text=volumes[i+should_add],bg='white',var=tempvar2)
                    cb_right.var = tempvar2
                    self.r_chkbuttons.append(cb_right)
                    cb_right.bind('<Button-1>', self.r_selstart)         #����shiftѡ��ĺ���
                    cb_right.bind('<Shift-Button-1>', self.r_selrange)
                    self.directory.window_create("end", align=TOP, window=cb_left)
                    self.directory.insert("end",'  ')
                    self.directory.window_create("end", align=TOP, window=cb_right)
                    self.directory.insert("end", "\n") # ǿ�ƻ���
                    i = i + 1
                tempvar1 = IntVar()
                cb_left = Checkbutton(self.directory,padx=0,pady=0,bd=0,text=volumes[i],bg='white',var=tempvar1)
                cb_left.var = tempvar1
                self.directory.window_create("end", align=TOP, window=cb_left)
                self.l_chkbuttons.append(cb_left)
                cb_left.bind('<Button-1>', self.l_selstart)
                cb_left.bind('<Shift-Button-1>', self.l_selrange)
                if (i+1)*2 <= amount:    #amount��ż�������
                    tempvar2 = IntVar()
                    cb_right = Checkbutton(self.directory,padx=0,pady=0,bd=0,text=volumes[i+should_add],bg='white',var=tempvar2)
                    cb_right.var = tempvar2
                    self.directory.insert("end",'  ')
                    self.directory.window_create("end", align=TOP, window=cb_right)
                    self.r_chkbuttons.append(cb_right)
                    cb_right.bind('<Button-1>', self.r_selstart)         #����shiftѡ��ĺ���
                    cb_right.bind('<Shift-Button-1>', self.r_selrange)
                self.directory.insert("end", "\n") # to force one checkbox per line
                self.showstate.config(text='�־�������')
                
            if self.notebook.select() == str(self.pane2):
                self.list.insert(END,content + ' ' + temp_instance.comicname)   #�����б�
                self.showstate.config(text='�־�������')
        
        self.tk.after(1000, self.watch_clipboard) 
    
    def l_selstart(self,event): #���ڷ־��б���ѡ��֮��,�趨��ʼ��,�Ա��ܹ���shiftѡ��
        self.l_start = self.l_chkbuttons.index(event.widget)#index�����������б��е����
    
    def l_selrange(self,event):#����֮ǰ��õ���ʼ������ڵĵ��λ��,�����ı���Щcb��״̬
        start = self.l_start
        end = self.l_chkbuttons.index(event.widget)
        sl = slice(min(start, end)+1, max(start, end))
        for cb in self.l_chkbuttons[sl]:
            cb.toggle()
        self.l_start = end
        
    def r_selstart(self,event):
        self.r_start = self.r_chkbuttons.index(event.widget)
    
    def r_selrange(self,event):
        start = self.r_start
        end = self.r_chkbuttons.index(event.widget)
        sl = slice(min(start, end)+1, max(start, end))
        for cb in self.r_chkbuttons[sl]:
            cb.toggle()
        self.r_start = end
        
    def do_selall(self,arg):    
        '''�����ȡ�����'ȫѡ'��ťʱ�Ĳ���'''
        state = arg.get()
        if state:
            for item in self.l_chkbuttons:
                item.select()
            for item in self.r_chkbuttons:
                item.select()
        else:
            for item in self.l_chkbuttons:
                item.deselect()
            for item in self.r_chkbuttons:
                item.deselect()
                
    def do_inversesel(self,*args):    
        for item in self.l_chkbuttons:
            item.toggle()
        for item in self.r_chkbuttons:
            item.toggle()
    
    def do_popup(self,event):#�ಿ���������б���Ҽ������˵�
        self.popup.post(event.x_root, event.y_root) #��x_root,y_root����Ҫ��x,y
    
    def delete(self):
        '''ɾ��list��ѡ�е���Ŀ'''
        sel_list = self.list.curselection() #selection_get()�᷵��ѡ������
        i = 0
        for index in sel_list:
            index = int(index)      #ע�ⷵ�ص�sel_list��Ԫ�ض���str
            index = index - i       #ÿ��ɾ��һ����ʣ�µ�index��Ӧ��-1
            self.list.delete(index)
            i = i + 1
    
    def delete_all(self):
        '''ɾ��list�е�ȫ����Ŀ'''
        self.list.delete(0, END)
                
    def choosedir(self):
        self.storedir['state'] = NORMAL
        self.storedir.delete(0, END)
        self.dirname = askdirectory()
        self.storedir.insert(0, self.dirname)
        self.storedir['state'] = 'readonly' #'readonly'�ǿ�ѡ���ɸģ�DISABLEDֱ���޷�ѡ��
    
    def download(self):
        self.progress['value'] = 0
        if self.dirname == '':
            self.showstate['text'] = '��ѡ�����������·��'
            return
        if self.notebook.select() == str(self.pane1):#������������
            if self.url.get() == '':
                self.showstate.config(text = '������������ҳ��ĵ�ַ')
                return
            pipein,pipeout = Pipe()
            threading.Thread(target=progressbar,daemon=True,args=(pipein,self.progress,self.showstate)).start()
            text_in_entry = self.url.get()  #url����������������,split��ȡ[0]��������url
            url = text_in_entry.split()[0]
            buttonlist = []
            dontdownloadlist = []
            buttonlist.extend(self.l_chkbuttons)
            buttonlist.extend(self.r_chkbuttons)
            for button in buttonlist:
                state = button.var.get()
                if not state:
                    dontdownloadlist.append(button['text'])
            download_process = MyDownloadProcess(url,self.dirname,dontdownloadlist,'131',pipeout)
            download_process.daemon = True
            self.showstate['text'] = 'downloading����'
            download_process.start() #ֻҪ����join���򲻻�����ԭ�����߳�
            
        elif self.notebook.select() == str(self.pane2):#�ಿ��������
            url_list = list(self.list.get(0,END))
            name_list = []  #�洢����������,����ʾ��ʾ�е�ʱ����,���û�֪�������µ�����һ��������
            for i in range(len(url_list)):
                name_list.append(url_list[i].split()[1])
                url_list[i] = url_list[i].split()[0]  #ͬ����ȡ��һ����
            pipein,pipeout = Pipe()
            threading.Thread(target=progressbar,daemon=True,args=(pipein,self.progress,self.showstate)).start()
            download_process = MyDownloadProcess_many(url_list,name_list,self.dirname,'131',pipeout)
            download_process.daemon = True
            self.showstate['text'] = 'downloading����'
            download_process.start() 



if __name__ == '__main__':
    freeze_support()
    gui = GUI()
