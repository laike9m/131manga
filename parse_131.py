# -*- coding:gbk -*-
import html.parser
import urllib.request
import httplib2
import pickle
import re
#import types
import assistfunc


class parseEpisode(html.parser.HTMLParser):
    #该类用于解析每一话的每一页，并把要下载的图片的url搞出来。会在parse131中存在一个实例，feed进每一页
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
                self.numofpage = int(data.lstrip('/'))#获取页面总数
            else:
                self.flag2 = 1
                self.currentpage = int(data) #获取当前页面数
        if '当前' in data:
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
        根据输入的131中某部漫画的主地址，对漫画的结构进行分析，并用parseEpisode类对每一话进行分析
        最终得到名为 manga的字典：
    {第一话：[url_1,pages_1],第二话：[url_2,pages_2],……,第N话:[url_N,pages_N]}
    '''
    def __init__(self,url):
        parts = url.split('/')      #一开始的url形如 http://comic.131.com/content/qingnian/15666.html
        parts.pop(len(parts)-2)     #先以/进行分割，然后去掉类型信息，处在倒数第二的位置
        url = '/'.join(parts)       #重新组合
        url = url.rstrip('.html')   #去掉末尾的.html
        self.url = url              #最后变成形如 http://comic.131.com/content/15666
        self.flag1 = 0
        self.manga = {}             #存储整部漫画的结构信息
        self.comicname = ''         #漫画的名字
        self.tempname = ''          #临时变量，每次保存<a>的title
        html.parser.HTMLParser.__init__(self)
        self.parseE = parseEpisode()#用一个parseEpisode实例实现每一页的信息提取
        
    def handle_data(self,data):
        if self.flag1 == 1:
            self.flag1 = 0
            if assistfunc.findchar(data,['话','卷','篇','章','特典','本','集']):
                self.manga[data] = []   #保证它是一个list，如果直接写[data]的话会变成set！
                self.manga[data].append(self.templink)
                if self.comicname == '':
                    self.comicname = self.tempname
                    
    def handle_starttag(self,tag,attrs):
        if tag == 'a':
            content = self.get_starttag_text()
            for name,value in attrs:
                if name == 'href':
                    self.templink = value   #存储可能是第一页的url
                if name == 'title':
                    self.tempname = value.split()[0]
                    break
            if self.url in content:
                self.flag1 = 1
                
    def getNumOfPages(self):
        #给定某一话第一页的url,分析出这一话总共的页数
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