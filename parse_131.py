# -*- coding:gbk -*-
import html.parser
import urllib.request
import httplib2
import pickle
import re
#import types
import assistfunc


class parseEpisode(html.parser.HTMLParser):
    #�������ڽ���ÿһ����ÿһҳ������Ҫ���ص�ͼƬ��url�����������parse131�д���һ��ʵ����feed��ÿһҳ
    def __init__(self):
        self.flag1 = 0
        self.flag2 = 0
        self.numofpage = 0
        self.currentpage = 0
        self.picurl = ''
        html.parser.HTMLParser.__init__(self)
        
    def handle_data(self,data):
        if self.flag1 == 1:
            if self.flag2 == 1:
                self.flag1 = 0
                self.flag2 = 0
                self.numofpage = int(data.lstrip('/'))#��ȡҳ������
            else:
                self.flag2 = 1
                self.currentpage = int(data) #��ȡ��ǰҳ����
        if '��ǰ' in data:
            self.flag1 = 1

    def handle_starttag(self,tag,attrs):
        if tag == 'script':
            istarget = 0         
            for key,value in attrs:
                if key == 'id' and value == 'imgjs':
                    istarget = 1
                if key == 'src' and istarget:
                    istarget = 0
                    patt = r"\?img=([^& ]+)"
                    #value = http://131js.131.com/channel/comic/img.js?img=http://res6.comic.131.com/ab/f2/bcd0da3723fa0293f33c1ca3d626f8b014b6.jpg
                    matchobj = re.search(patt,value)
                    self.picurl = matchobj.group(1)
                    #print(self.picurl)
    
    def feed(self,url):
        h = httplib2.Http('.cache')
        request,data = h.request(url,headers={'accept-encoding':'gzip,identity','cache-control':'no-cache'})
        data = data.decode('utf-8')
       # data = urllib.request.urlopen(url).read().decode('utf-8')
        html.parser.HTMLParser.feed(self, data)
      
class parse131(html.parser.HTMLParser):
    '''
        ���������131��ĳ������������ַ���������Ľṹ���з���������parseEpisode���ÿһ�����з���
        ���յõ���Ϊ manga���ֵ䣺
    {��һ����[url_1,pages_1],�ڶ�����[url_2,pages_2],����,��N��:[url_N,pages_N]}
    '''
    def __init__(self,url):
        parts = url.split('/')      #һ��ʼ��url���� http://comic.131.com/content/qingnian/15666.html
        parts.pop(len(parts)-2)     #����/���зָȻ��ȥ��������Ϣ�����ڵ����ڶ���λ��
        url = '/'.join(parts)       #�������
        url = url.rstrip('.html')   #ȥ��ĩβ��.html
        self.url = url              #��������� http://comic.131.com/content/15666
        self.flag1 = 0
        self.manga = {}             #�洢���������Ľṹ��Ϣ
        self.comicname = ''         #����������
        self.tempname = ''          #��ʱ������ÿ�α���<a>��title
        html.parser.HTMLParser.__init__(self)
        self.parseE = parseEpisode()#��һ��parseEpisodeʵ��ʵ��ÿһҳ����Ϣ��ȡ
        
    def handle_data(self,data):
        if self.flag1 == 1:
            self.flag1 = 0
            if assistfunc.findchar(data,['��','��','ƪ','��','�ص�','��','��']):
                self.manga[data] = []   #��֤����һ��list�����ֱ��д[data]�Ļ�����set��
                self.manga[data].append(self.templink)
                if self.comicname == '':
                    self.comicname = self.tempname
                    
    def handle_starttag(self,tag,attrs):
        if tag == 'a':
            content = self.get_starttag_text()
            for name,value in attrs:
                if name == 'href':
                    self.templink = value   #�洢�����ǵ�һҳ��url
                if name == 'title':
                    self.tempname = value.split()[0]
                    break
            if self.url in content:
                self.flag1 = 1
                
    def getNumOfPages(self):
        #����ĳһ����һҳ��url,��������һ���ܹ���ҳ��
        for key in self.manga:
            self.parseE.feed(self.manga[key][0])
            numofpages = self.parseE.numofpage
            assistfunc.dictOfListAppend(self.manga,key,numofpages)

if __name__ == '__main__':
    testpage = parse131('http://comic.131.com/content/shaonian/16117.html')
    testpage.feed(urllib.request.urlopen("http://comic.131.com/content/shaonian/16117.html").read().decode('utf-8'))
    #page = parseEpisode()
    #page.feed('http://comic.131.com/content/16117/187873/3.html')
    testpage.getNumOfPages()
    for each in testpage.manga.items():
        print(each)
        
    with open('testpage_manga.pickle','wb') as f:
        pickle.dump(testpage.manga,f)
        
    print(testpage.comicname)
    #print(type(testpage.manga))
    testpage.close()
#page.close()