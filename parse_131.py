# -*- coding:gbk -*-
import html.parser
import urllib.request
import httplib2
import pickle
import re
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
        if '��ǰ ' in data:
            self.flag1 = 1

    def handle_starttag(self,tag,attrs):
        '''
        �������������һ����ͨ��js����̬����ͼƬ
        �ڶ�����ֱ�Ӽ��أ�
        '''
        if tag == 'script':
            istarget = 0         
            for key,value in attrs:
                if key == 'id' and value == 'imgjs':
                    istarget = 1
                if key == 'src' and istarget:
                    istarget = 0
                    patt = r"\?img=([^& ]+)"
                    matchobj = re.search(patt,value)
                    self.picurl = matchobj.group(1)
        if tag == 'img':
            istarget = 0
            for key,value in attrs:
                if key == 'id' and value == 'comicBigPic':
                    istarget = 1
                if istarget:
                    #import pydevd;pydevd.settrace()
                    if key == 'src':
                        self.picurl = value
    
    def feed(self,url):
        h = httplib2.Http('.cache')
        request,data = h.request(url,headers={'accept-encoding':'gzip,identity',})
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
        self.flag1 = 0              #��һ��flag,�ж��ѽ���<ul class='mh_fj'>
        self.flag2 = 0              #�ڶ���flag,�ж��ѽ���<li>
        self.flag_of_cover = 0      #��ȡ����ʱ�õ���flag
        self.upto15 = 0             #ÿһ��tab���洢15��,5��3��
        self.manga = {}             #�洢���������Ľṹ��Ϣ
        self.comicname = ''         #����������
        self.tempname = ''          #��ʱ������ÿ�α���<a>��title
        self.coverimage = ''        #���������URL
        html.parser.HTMLParser.__init__(self)
        self.parseE = parseEpisode()#��һ��parseEpisodeʵ��ʵ��ÿһҳ����Ϣ��ȡ
        
    def handle_data(self,data):
        if self.flag2:
            self.flag2 = 0
            #ֱ���������1->001һ�����ݽ������,��������������ҳ���,���滻��3λ��
            #���ڵ�һ������û�������������,�ͱ��ֲ���
            number = re.search(r'\d+',data)
            if number and number.end() != len(data):
                data = data.replace(number.group(),assistfunc.getThreeDigit(int(number.group())))
            self.manga[data] = []   #��֤����һ��list�����ֱ��д[data]�Ļ�����set��
            self.manga[data].append(self.templink)
            if self.comicname == '':
                self.comicname = self.tempname
            self.upto15 += 1
            if self.upto15 == 15:#��������,����Ҫ��ʼ��һ��<ul>�ļ���
                self.flag1 = 0
                
                
    def handle_starttag(self,tag,attrs):
        '''�µ��½���ȡ�취,ͨ��<ul class='nh_fj'>�ȶ�flag1,�ٰ��ϰ취��flag2'''
        if tag == 'ul':
            for name,value in attrs:
                if name == 'class' and value == 'mh_fj':
                    self.upto15 = 0     #���������������handledata��,��Ϊ��ҳ�����һ��tab����ǰ��,�������ķ־���15
                    self.flag1 = 1
        if self.flag1 and tag == 'a':
            content = self.get_starttag_text()
            for name,value in attrs:    #attrs��[(name1,value1),(name2,value2)]һ��tuple��ɵ�list
                if name == 'href':
                    self.templink = value   #�洢�����ǵ�һҳ��url
                if name == 'title':
                    self.tempname = value.split()[0]#value����title="������ʳ���� ȫ1��(��)"����һ���־�������������
                    break
            if self.url in content:
                if attrs[1][0] == 'title':#�������������,��Ϊ��ʱ���ұ�������ͬ�����������½�,Ҳ����url
                    self.flag2 = 1
                elif len(attrs) > 2 and attrs[2][0] == 'title':#�����������Ϊ��ɫ�ķ־�,title�ڵ�����
                    self.flag2 = 1
        
        '''Ѱ�ҷ���'''
        if tag == 'dl':
            content = self.get_starttag_text()
            for name,value in attrs:
                if name == 'class' and value == 'dt':
                    self.flag_of_cover = 1
                
        if tag == 'img' and self.flag_of_cover:
            content = self.get_starttag_text()
            for name,value in attrs:
                if name == 'src':
                    self.flag_of_cover = 0
                    self.coverimage = value #����cover��URL
                    
    def getNumOfPages(self):
        #����ĳһ����һҳ��url,��������һ���ܹ���ҳ��
        for key in self.manga:
            self.parseE.feed(self.manga[key][0])
            numofpages = self.parseE.numofpage
            assistfunc.dictOfListAppend(self.manga,key,numofpages)

if __name__ == '__main__':
    testpage = parse131('http://comic.131.com/content/qingnian/17974.html')
    data = urllib.request.urlopen("http://comic.131.com/content/qingnian/17974.html").read().decode('utf-8')
    testpage.feed(data)
    
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