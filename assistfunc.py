# -*- coding:gbk -*-
#���ڶ���һЩ�����ĺ���

def quicksort(s, l, r):
    '''
        ���������㷨��L��һ��list����˵built-in��sort()�������죬�д�����
        ����python��Ƭ�ǿ��������Ի�����Ҫl,r����
    list�ǿ��޸ĵ����ͣ����Ե����������еݹ�ʱ���൱�ڴ����ã����ں�����ᱻ�޸�    
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
    #ȷ��ĳ���ַ�������û����һ��list�г��ֹ�����
    for each in char:
        if string.find(each) != -1:
            return True
    return False

def dictOfListAppend(dic,key,additem):
    #��һ��value��list���ֵ��ܹ������list�����Ԫ��
    tempvalue = []
    for item in dic[key]:
        tempvalue.append(item)
    tempvalue.append(additem)
    dic[key] = tempvalue
    
def getThreeDigit(num):
    #��������ҳ��淶��3λ����ʾ�������ַ���������1->'001'��21->'021'
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