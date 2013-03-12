# -*- coding:gbk -*-
#用于定义一些辅助的函数

def quicksort(s, l, r):
    '''
        快速排序算法，L是一个list。据说built-in的sort()函数更快，有待测试
        由于python分片是拷贝，所以还得需要l,r参数
    list是可修改的类型，所以当作参数进行递归时，相当于传引用，即在函数里会被修改    
    '''
    i = l
    j = r
    if r - l < 1:
        return
    X = s[i]
    while i < j:
        while i < j and s[j] >= X:
            j = j - 1
        if i < j:
            s[i] = s[j]
        while i < j and s[i] < X:
            i = i + 1
        if i < j:
            s[j] = s[i]
    s[i] = X
    quicksort(s,l,i-1)
    quicksort(s,i+1,r)



def findchar(string,char):
    #确定某个字符串中有没有另一个list中出现过的字
    for each in char:
        if string.find(each) != -1:
            return True
    return False

def dictOfListAppend(dic,key,additem):
    #让一个value是list的字典能够在这个list中添加元素
    tempvalue = []
    for item in dic[key]:
        tempvalue.append(item)
    tempvalue.append(additem)
    dic[key] = tempvalue
    
def getThreeDigit(num):
    #将漫画的页码规范成3位数显示，返回字符串，比如1->'001'，21->'021'
    if num < 10: 
        return '00'+str(num)
    elif num > 9 and num < 100:
        return '0'+str(num)
    elif num > 99:
        return str(num)
    else:
        return False
                
if __name__ == '__main__':
    s = [72,6,57,88,60,42,83,73,48,85]
    quicksort(s,0,len(s)-1)
    print(s)