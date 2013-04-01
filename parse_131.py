# -*- coding:gbk -*-
import html.parser
import urllib.request
import httplib2
import pickle
import re
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
        if '当前 ' in data:
            self.flag1 = 1

    def handle_starttag(self,tag,attrs):
        '''
        有两种情况，第一种是通过js来动态加载图片
        第二种是直接加载？
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
        self.flag1 = 0              #第一层flag,判断已进入<ul class='mh_fj'>
        self.flag2 = 0              #第二层flag,判断已进入<li>
        self.flag_of_cover = 0      #获取封面时用到的flag
        self.upto15 = 0             #每一个tab最多存储15章,5行3列
        self.manga = {}             #存储整部漫画的结构信息
        self.comicname = ''         #漫画的名字
        self.tempname = ''          #临时变量，每次保存<a>的title
        self.coverimage = ''        #漫画封面的URL
        html.parser.HTMLParser.__init__(self)
        self.parseE = parseEpisode()#用一个parseEpisode实例实现每一页的信息提取
        
    def handle_data(self,data):
        if self.flag2:
            self.flag2 = 0
            #直接在这里把1->001一劳永逸解决问题,先用正则把数字找出来,再替换成3位数
            #对于第一卷这种没有数字在里面的,就保持不变
            number = re.search(r'\d+',data)
            if number and number.end() != len(data):
                data = data.replace(number.group(),assistfunc.getThreeDigit(int(number.group())))
            self.manga[data] = []   #保证它是一个list，如果直接写[data]的话会变成set！
            self.manga[data].append(self.templink)
            if self.comicname == '':
                self.comicname = self.tempname
            self.upto15 += 1
            if self.upto15 == 15:#到了上限,就需要开始另一个<ul>的检索
                self.flag1 = 0
                
                
    def handle_starttag(self,tag,attrs):
        '''新的章节提取办法,通过<ul class='nh_fj'>先定flag1,再按老办法定flag2'''
        if tag == 'ul':
            for name,value in attrs:
                if name == 'class' and value == 'mh_fj':
                    self.upto15 = 0     #在这里清零而不在handledata里,因为网页把最后一个tab放在前面,它包含的分卷不到15
                    self.flag1 = 1
        if self.flag1 and tag == 'a':
            content = self.get_starttag_text()
            for name,value in attrs:    #attrs是[(name1,value1),(name2,value2)]一堆tuple组成的list
                if name == 'href':
                    self.templink = value   #存储可能是第一页的url
                if name == 'title':
                    self.tempname = value.split()[0]#value形如title="东方美食猎人 全1话(完)"，第一部分就是漫画的名字
                    break
            if self.url in content:
                if attrs[1][0] == 'title':#加这个限制条件,因为有时候右边栏有相同漫画的最新章节,也包含url
                    self.flag2 = 1
                elif len(attrs) > 2 and attrs[2][0] == 'title':#此情况是字体为红色的分卷,title在第三个
                    self.flag2 = 1
        
        '''寻找封面'''
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
                    self.coverimage = value #保存cover的URL
                    
    def getNumOfPages(self):
        #给定某一话第一页的url,分析出这一话总共的页数
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