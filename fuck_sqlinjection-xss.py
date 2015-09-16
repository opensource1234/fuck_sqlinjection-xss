#coding=utf-8

import urllib2
import urllib
import os
import sys
import getopt
import time
import re
import cookielib
import random
import string
import chardet
import subprocess
import httplib
import cgi

from platform import system
from random import randint
from pytesser import *
from shibie import *


reload(sys)  
sys.setdefaultencoding('utf8')  



# 目标站点
host = ""
hhost = ""

# 爬到的页面url及target
urls = []
target = {}

# 一些全局变量
sqli            = True
xss             = True
read_sqlmap     = '/usr/share/sqlmap/output'
output          = './output'




# Spider类:
# 爬取目标站点所有页面
# 解析form表单
# by zhuangzhuang
class Spider:

    def __init__(self,website):#初始化参数
        self.siteURL = website#定义要访问的链接
        self.dic={}#定义返回的字典｛网址->form表｝

    def getPage(self):#得到字符串网页信息
        kongbai=''
        url = self.siteURL
        str=''
        #print url
        request = urllib2.Request(url,headers={
            'Connection': 'Keep-Alive',
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'
        })
        try:
            response = urllib2.urlopen(request)
        except:
            pass
        if 'html' not in response.info().get('content-type'):
            # print('111111111111111111111111111111')
            return kongbai
        #return response.read().decode('gbk')
        '''while 1:
            data=response.read(2048)
            str+=data
            if not len(data):
                break'''
        try:
            data=response.read()
        except:
            data=''
        encoding_dict = chardet.detect(data)
        #print encoding
        web_encoding = encoding_dict['encoding']
        if web_encoding == 'utf-8' or web_encoding == 'UTF-8':
            html = data
        else :
            html = data.decode('gbk','ignore').encode('utf-8')
        str=html
        #print(str)
        str1=str.replace("\n","")
        return str1
    def getPage1(self,urll):#得到字符串网页信息
        kongbai=''
        url = urll
        str=''
        #print url
        request = urllib2.Request(url,headers={
            'Connection': 'Keep-Alive',
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'
        })
        try:
            response = urllib2.urlopen(request,timeout=3)
        except:
            return kongbai
        if 'html' not in response.info().get('content-type'):
            return kongbai
        #return response.read().decode('gbk')
        '''while 1:
            data=response.read(2048)
            str+=data
            if not len(data):
                break'''
        data=response.read()
        encoding_dict = chardet.detect(data)
        #print encoding
        web_encoding = encoding_dict['encoding']
        if web_encoding == 'utf-8' or web_encoding == 'UTF-8':
            html = data
        else :
            html = data.decode('gbk','ignore').encode('utf-8')
        str=html
        #print(str)
        str1=str.replace("\n","")
        return str1
    def matchform(self,str1):#输入网页字符串，得到form表
        str1=str1.replace("\t","")
        str1=str1.replace("\r","")
        pattern = re.compile(r"<form.*?</form>")
        return re.findall(pattern,str1)
    def getzidain(self,list):#输入form表，得到字典
        self.dic[self.siteURL]=list
        #print(self.dic)
        return self.dic
    def getwebsite(self,str):#输入网页字符串，得到所有网页链接表
        #str=self.getPage()
        kongbai=[]
        if len(str)==0:
            return kongbai
        pattern = re.compile('\.(.*?)\.com')
        goal=re.search(pattern,self.siteURL)
        try:
            haha=goal.group(1)
        except:
            haha='你'
        pattern = re.compile(r'href=\"(.+?)\"')
        #print len(re.findall(pattern,str))
        dict={}
        list=[]
        list1=[]
        list2=[]
        list3=[]
        for a in re.findall(pattern,str):
            if a.find(haha)!=-1:
                if a.find('http')==-1:
                    if a.find('/')!=-1 or a.find('//')!=-1:
                        if a.find('//')!=-1:
                            a='http:'+a
                        else:
                            match=re.search('(\/\/.*?)\/',self.siteURL)
                            if match:
                                a='http:'+match.group(0)+a
                            else:
                                a=self.siteURL+a
                    else:
                        match=re.search('\/\/.*\/',self.siteURL)
                        if match:
                            a='http:'+match.group(0)+a
                        else:
                            a=self.siteURL+'/'+a
                b=[a,'']
                dict[b[0]] =b[1]
            else:
                if a.find('http')==-1:
                    if a.find('/')!=-1 or a.find('//')!=-1:
                        if a.find('//')!=-1:
                            a='http:'+a
                        else:
                            match=re.search('(\/\/.*?)\/',self.siteURL)#一个/的情况
                            if match:
                                a='http:'+match.group(0)+a
                            else:
                                a=self.siteURL+a
                    else:
                        match=re.search('\/\/.*\/',self.siteURL)
                        if match:
                            a='http:'+match.group(0)+a
                        else:
                            a=self.siteURL+'/'+a
                b=[a,'']
                dict[b[0]] =b[1]
        for e in dict.items():
            list1.append(e[0]+e[1])
        for c in list1[:]:
            match=re.search(r'.*\?.*?=',c)
            if match:
                k=match.group(0)
                if k not in list3:
                    list3.append(k)
                    list2.append(c)
                for d in list1[:]:
                    if d.find(k)!=-1:
                        list1.remove(d)
        list1.extend(list2)
        return list1
        #return re.findall(pattern,str)
    
    def getcanshu(self,a):#输入表单，得到相应信息
        all=[]
        panduan=["checkbox","text","password","radio","hidden","select","textarea"]
        pattern = re.compile(r'<input.*?>|<textarea.*?>|<select.*?</select>',re.I)
        #print(re.findall(pattern,a))
        for b in re.findall(pattern,a):
            c=[]
            pattern = re.compile(r'type.*?=.*?\"(.+?)\"',re.I)
            if re.findall(pattern,b):
                c.append(re.findall(pattern,b)[0])
            elif b.find("textarea")!=-1:
                c.append("textarea")
            elif b.find("select")!=-1:
                c.append("select")
                
            pattern = re.compile(r'name()*=()*"(.*?)"',re.I)
            if re.findall(pattern,b):
                for g in re.findall(pattern,b):
                    c.append(g[2])
            else:
                c.append('')
            pattern = re.compile(r'value()*=()*"(.*?)"',re.I)
            if re.findall(pattern,b):
                guodu=[]
                for g in re.findall(pattern,b):
                    guodu.append(g[2])
                c.append(tuple(guodu))
                    #print(re.findall(pattern,b))
            else:
                c.append(())
            all.append(c)
        #print(all)
        chuli=[]
        for d in all:
            if d[0] not in panduan:
                chuli.append(d)
        for k in chuli:
            all.remove(k)
        chuli1=[]
        for e in all:
            for f in all:
                if e!= f and e[0]==f[0] and e[1] ==f[1]:
                    e[2]=e[2]+f[2]
                    chuli1.append(f)
        for l in chuli1:
            all.remove(l)
        return all
    '''    
    def getcanshu(self,a):#输入字典，得到相应信息表单
        all=[]
        panduan=["checkbox","text","password","radio","hidden","select","textarea","yanzheng"]
        pattern = re.compile(r'<input.*?>.*?<img.*?>|<input.*?>|<textarea.*?>|<select.*?</select>',re.I)
        #print(re.findall(pattern,a))
        for b in re.findall(pattern,a):
            print(b)
            c=[]
            pattern = re.compile(r'type.*?=.*?\"(.+?)\"',re.I)
            if re.findall(pattern,b):
                if b.find('img')!=-1:
                    c.append('yanzheng')
                else:
                    c.append(re.findall(pattern,b)[0])
            elif b.find("textarea")!=-1:
                c.append("textarea")
            elif b.find("select")!=-1:
                c.append("select")
                
            pattern = re.compile(r'name()*=()*"(.*?)"',re.I)
            if re.findall(pattern,b):
                for g in re.findall(pattern,b):
                    c.append(g[2])
            else:
                c.append('')
            pattern = re.compile(r'value()*=()*"(.*?)"',re.I)
            if re.findall(pattern,b):
                guodu=[]
                for g in re.findall(pattern,b):
                    guodu.append(g[2])
                c.append(tuple(guodu))
                    #print(re.findall(pattern,b))
            else:
                pattern = re.compile(r"src.*?=.*?'(.*?)'",re.I)
                if re.findall(pattern,b):
                    c.append(tuple(re.findall(pattern,b)))
                else:
                    c.append(())
            all.append(c)
        #print(all)
        chuli=[]
        for d in all:
            if d[0] not in panduan:
                chuli.append(d)
        for k in chuli:
            all.remove(k)
        chuli1=[]
        for e in all:
            for f in all:
                if e!= f and e[0]==f[0] and e[1] ==f[1]:
                    e[2]=e[2]+f[2]
                    chuli1.append(f)
        for l in chuli1:
            all.remove(l)
        return all
    '''
    
    def getallform(self):#得到所有列表字典
        urls = []
        allform={}
        str1=self.getPage()
        list=self.getwebsite(str1)
        for a in list:
            wangye=self.getPage1(a)
            list1=self.getwebsite(wangye)
            formlist=self.matchform(wangye)
            allform[a]=formlist
            for b in list1:
                wangye1=self.getPage1(b)
                list2=self.getwebsite(wangye1)
                formlist1=self.matchform(wangye1)
                allform[b]=formlist1
                for c in list2:
                    wangye2=self.getPage1(c)
                    formlist2=self.matchform(wangye2)
                    allform[c]=formlist2
        for url in allform:
            urls.append(url)
                                                    
        for k, v in allform.items():
            if not v and k.find('?')==-1:
                allform.pop(k)
        return allform, urls




# 生成n字节随机字符串
def get_randstr(n):
    randstr = ''
    ch = ''
    
    for i in xrange(n):
        ch = string.join(random.sample(['z','y','x','w','v','u','t','s','r','q','p','o','n','m','l','k','j','i','h','g','f','e','d','c','b','a','0','1','2','3','4','5','6','7','8','9'], 1)).replace(' ','')
        randstr += ch
        
    return randstr



# 填写表单得到POST字符串，并指定其中一个参数的值为Payload
def get_POST_data(parsedform, param, payload):
    
    postdata = {}
    
    for postparam in parsedform:
        if postparam == param:
            postdata[postparam[1]] = payload
        else:
            if postparam[0].lower() in ['text', 'password', 'textarea',]:
                postdata[postparam[1]] = get_randstr(4)
            elif postparam[0].lower() in ['checkbox', 'radio', 'select',]:
                postdata[postparam[1]] = postparam[2][0]
            elif postparam[0].lower() == 'hidden':
                postdata[postparam[1]] = postparam[2][0]
            else:
                pass
    
    return postdata


# dict转化成list
def dict_to_list(d, middle):
    l = []
    for key,value in d.iteritems():
        l.append("%s%s%s" % (str(key), str(middle), str(value)))
    return l


# 获取GET请求页面源码
def get_source(url):
    
    if url == '':
        return ''
    
    headers = {}
    headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'
    request = urllib2.Request(url, headers=headers)
    
    try:
        response = urllib2.urlopen(request)
        source = response.read()
    except:
        source = ''
    
    return source


# 解析url
def url_params(url):
    
    start = -1
    params = {}
    hashs = ''
    
    start = url.find('?')
    end = url.find('#')
    
    if start < 0:
        if end > 0:
            hashs = url[end:]
    else:
        
        keys = ''
    
        if end > 0:
            keys = url[start+1:end]
            hashs = url[end:]
        else:
            keys = url[start+1:]
    
        keys = keys.split('&')
        map(lambda x:params.setdefault(x.split('=')[0], x.split('=')[1]), keys)
    
    return start, params, hashs



# 重构url
def get_newurl(url, start, hashs, paramscp, param, value, fuzz):
    
    paramscp[param] = "%s%s" % (str(value), str(fuzz))
    newkeys = dict_to_list(paramscp, '=')
    newkeys = '&'.join(newkeys)

    # 新的GET请求
    newurl = "%s%s%s" % (url[:start+1], newkeys, hashs)
    
    return newurl


# 生成sql注入测试结果文件
def outputfile(url):
    global host
    global read_sqlmap
    global output
        
    result = ""
    path = "%s/%s/log" % (read_sqlmap, host)
        
    if os.path.isfile(path):
        
        try:
            f = open(path, 'r')
            content = f.read()
        except:
            pass
        finally:
            f.close()
        
            # 某个参数检测完之后删除对应sqlmap日志目录
            os.system("rm -r /usr/share/sqlmap/output/%s" % host)
            
        if content == '':
            pass
        else:
            result = "%s\n" % url
            resu = re.search(r'---(.|\n)+---', str(content))
            if resu is not None:
                result += (resu).group(0)
            result += "\n\n"
            
            # 结果写入result.txt
            a = url
            b = 'SQL injection'
            c1 = re.search(r'Parameter:(.*?)\n', result)
            if c1 is not None:
                c = c1.group(1)
            d = result
            e = u'过滤'
            outresult(a, b, c, d, e)
            
            
            filepath = "%s/%s/result_sqlinjection.txt" % (output, host)
            
            try:
                f = open(filepath, 'a')
                f.write(result)
            except:
                pass
            finally:
                f.close()
           
    return 0


# 生成XSS测试结果文件
def outputfile2(result):
    global host
    global output
    
    path = "%s/%s/result_xss.txt" % (output, host)
    
    try:
        f2 = open(path, 'a')
        f2.write(result)
    except:
        pass
    finally:
        f2.close()
    
    return 0



# 使用sqlmap进行GET注入测试
def sqlmap_get(url, param):
    
    os.system("sqlmap -u %s -p %s --batch" % (url, str(param)))
    
    return 0

# 使用sqlmap进行POST注入测试
def sqlmap_post(url):
    
    os.system("sqlmap -u %s --forms --batch" % url)
    
    return 0

# 使用sqlmap进行HTTP Header注入测试
def sqlmap_header(url, cookies):
    
    if cookies == '':
        os.system("sqlmap -u %s --level 3 --batch" % url)
    else:
        os.system("sqlmap -u %s --cookie=%s --level 3 --batch" % (url, cookies))
    
    return 0


# 检测是否存在GET类型的sql注入
def fuck_get_sqlinjection(target):
    
    for url in target:
        
        start, params, hashs = url_params(url)
        
        if params == {}:
            continue
        
    
        # 依次对各参数进行GET注入测试     
        for param in params:
            
            try:
                sqlmap_get(url, param)
            except KeyboardInterrupt:
                continue
            finally:
                outputfile(url)
    
    return

# 检测是否存在POST类型的sql注入
def fuck_post_sqlinjection(target):
    
    for url, forms in target.iteritems():
        
        if forms == []:
            continue
        else:
            try:
                sqlmap_post(url)
            except KeyboardInterrupt:
                continue
            finally:
                outputfile(url)
    
    return
                

# 检测是否存在HTTP Header类型的注入
def fuck_header_sqlinjection(target):
    
    for url in target:
        start = url.find('?')
        
        if start < 0:
            continue
        else:
            
            # 获取页面cookies
            cj = cookielib.CookieJar()
    
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    
            opener.add_handler = [('User-agent','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0')]
            
            try:
                opener.open(url)
            except:
                pass
    
            cookies = []
            coo = ''
    
            for index,cookie in enumerate(cj):
                coo = re.search(r" (.+) for ", str(cookie))
                if coo is not None:
                    coo = coo.group(1)
                    cookies.append(coo)
                
            cookies = ';'.join(cookies)
            
            cj.clear()
            
    
            # 测试HTTP Header注入
            try:
                sqlmap_header(url, cookies)
            except:
                continue
            finally:
                outputfile(url)
                
    return


# 检测是否存在反射型XSS
def fuck_reflected_xss(target):
    
    result = ''
    
    # 读取xss_payload文件        
    try:
        f = open("config/xss_payload.txt", "r")
        lines = f.readlines()
    except:
        pass
    finally:
        f.close()
        
    # 解析url并进行XSS测试    
    for url in target:
        
        start = -1
        params = {}
        hashs = ''
        
        try:
            start, params, hashs = url_params(url)
        except:
            continue
        
        newurl = ''
        source = ''
        
        
        # 测试hash中的XSS
        if hashs == "":
            pass
        else:
            for line in lines:
                line = line[:-1]
                
                payload = "%s%s" % (hashs, line)
                
                newurl = get_newurl(url, start, payload, paramscp, param, value, '')
        
                print "[fragment XSS test] : %s" % payload
                source = get_source(newurl)
                
                if str(line) in str(source):
                    
                    print "[*] Maybe find a XSS!"
                    
                    result = "Maybe there is a XSS in fragment!\nurl : %s\nPayload : %s\n" % (url, payload)
                    outputfile2(result)
                    
                    a = url
                    b = 'XSS'
                    c = 'fragment'
                    d = result
                    e = u'编码/过滤'
                    outresult(a, b, c, d, e)
                    
                    break        
                              
        # 测试GET参数中的XSS
        if params == {}:
            continue
        
        for param, value in params.iteritems():
            
            paramscp = params.copy()
            
            for line in lines:
                line = line[:-1]
                
                fuzz = line
                payload = "%s%s" % (str(value), fuzz)
                
                print "[get parameter XSS test] : %s" % payload
                
                newurl = get_newurl(url, start, hashs, paramscp, param, value, fuzz)
                
                try:
                    source = get_source(newurl)
                except:
                    continue
                
                if str(fuzz) in str(source):
                    
                    print "[*] Maybe find a XSS!"
                    
                    result = "Maybe there is a XSS in get parameter %s!\nurl: %s\nPayload : %s\n" % (str(param), url, payload)
                    outputfile2(result)
                    
                    a = url
                    b = 'XSS'
                    c1 = re.search(r'parameter(.*?)\n', result)
                    if c1 is not None:
                        c = c1.group(1)
                    d = result
                    e = u'编码/过滤'
                    outresult(a, b, c, d, e)
                    
                    break
    
    return


# 检测是否存在存储型XSS
def fuck_storage_xss(target):
    global hhost
    global urls
    
    # 存储型XSS标识
    flag = 1
    
    result = ''
        
    # 读取xss_payload文件        
    try:
        f = open("config/xss_payload.txt", "r")
        lines = f.readlines()
    except:
        pass
    finally:
        f.close()
        
    for url, forms in target.iteritems():
        
        if forms == []:
            continue
                
        # 填写form表单并提交
        for form in forms:
            method = re.search(r"action( |\n)*?=( |\n)*\"((.|\n)*?)\"", form)
            if method is None:
                continue
            if method.group(3).lower() == 'get':
                continue
            
            postdata = {}
            action = ''
            
            # 得到表单提交地址
            goal = re.search(r"action( |\n)*?=( |\n)*\"((.|\n)*?)\"", form)
            if goal is not None:
                go = goal.group(3)
            
                g = re.search(r'^http(s|)://', go)
                if g is not None:
                    action = go
                else:
                    g = re.search(r'^/', go)
                
                    if g is not None:
                        action = "%s%s" % (hhost, go)
                    else:
                        if go == '':
                            action = url
                        else:
                            g = re.search(r'^http(s|)://.*/', url)
                            direc = ''
                    
                            if g is not None:
                                direc = g.group(0)
                                action = "%s%s" % (direc, go)
                            else:
                                action = "%s/%s" % (url, go)
            
            else:
                continue
            
            # 填写表单参数
            spiderparseform = Spider(hhost)
            parsedform = spiderparseform.getcanshu(form)
            
            for param in parsedform:
                pay = 0
                
                if param[0].lower() not in ['text', 'password', 'textarea',]:
                    continue
                
                for line in lines:
                    
                    
                    line = line[:-1]
                    a = line.find('alert(1)')
                    
                    if a > 0:
                        line = line.replace("alert(1)", "alert(%s)" % str(flag))
                    
                    
                    payload = line
                    
                    postdata = get_POST_data(parsedform, param, payload)
                    
                    # 提交表单
                    print "[post parameter XSS test] : %s" % payload
                    
                    post_data = urllib.urlencode(postdata)
                    
                    try:
                        req = urllib2.urlopen(action, post_data)
                    except:
                        continue
                    
                    # 在整个站点寻找测试向量
                    for aurl in urls:
                        source = ''
                        
                        try:
                            source = get_source(aurl)
                        except:
                            continue
                        '''
                        finally:
                            print
                            print payload
                            print 
                            if source == '':
                                print '0'
                            else:
                                print '1'
                                f = open('test.txt', 'a')
                                f.write("\n\n\n\n\n\n\n\npayload:%s\nurl:%s\n%s" % (payload, aurl, source))
                                f.close()
                        '''
                        # payload = '</textarea><script>alert(1)</script>//'
                        if str(payload) in str(source):
                        
                            print "[*] Maybe find a XSS!"
                        
                            result = "Maybe there is a XSS in post parameter %s\nfrom : %s\nto : %s\nPayload : %s\n" % (str(param[1]), url, aurl, payload)
                            outputfile2(result)
                            
                            a = url
                            b = 'XSS'
                            c1 = re.search(r'parameter(.*?)\n', result)
                            if c1 is not None:
                                c = c1.group(1)
                            d = result
                            e = u'编码/过滤'
                            outresult(a, b, c, d, e)                            
                        
                            flag += 1
                            pay = 1
                        
                            break
                    if pay == 1:
                        break
                        
                        
          
             
    return

# 输出结果文件
def outresult(a, b, c, d, e):
    global output
    global host
    
    
    line = "%s::::%s::::%s::::%s::::%s" % (a, b, c, d, e)
    
    line = line.replace('\n', '<br>')
    line = line + '\n'
    
    f = open('%s/%s/result.txt' % (output, host), 'a')
    f.write(line)
    f.close()
    
    return 0 


# 生成HTML结果文件
def shell_storm(location1,location2):
    '''
    os = system()
    if os == 'Linux':
        config_location = "config/sandi.conf"
    elif os == "Windows":
        config_location = "config\\sandi.conf"
    else:
        config_location = "config/sandi.conf"
    
    conf_file = open(config_location, "r").readlines()
    for cr in conf_file:
        cr = cr.rstrip()  
        match1 = re.search("BROWSER=", cr)
        if match1:
            browser = cr.replace("BROWSER=", "")
            browser = browser+" "
        match2 = re.search("OUTPUT=", cr)
        if match2:
            output = cr.replace("OUTPUT=", "")

    session = randint(11111, 99999)

    filename = "result-shell-storm-%d.html"%session 
    location = output+filename
    

'''
    head = """
    <!DOCTYPE html>
<html lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Sandi Result Page</title>

<style type="text/css">

    html, body, div, span, object, iframe,
    h1, h2, h3, h4, h5, h6, p, blockquote, pre,
    abbr, address, cite, code,
    del, dfn, em, img, ins, kbd, q, samp,
    small, strong, sub, sup, var,
    b, i,
    dl, dt, dd, ol, ul, li,
    fieldset, form, label, legend,
    table, caption, tbody, tfoot, thead, tr, th, td {
        margin:0;
        padding:0;
        border:0;
        outline:0;
        font-size:100%;
        vertical-align:baseline;
        background:transparent;
    }
    
    body {
        margin:0;
        padding:0;
        font:12px/15px "Helvetica Neue",Arial, Helvetica, sans-serif;
        color: #555;
        background:#f5f5f5 url(bg.jpg);
    }
    
    a {color:#666;}
    
    #content {width:85%; max-width:1000px; margin:1% auto 0;}
    
    /*
    Pretty Table Styling
    CSS Tricks also has a nice writeup: http://css-tricks.com/feature-table-design/
    */
    
    table {
        overflow:hidden;
        border:1px solid #d3d3d3;
        background:#fefefe;
        width:100%;
        margin:5% auto 0;
        -moz-border-radius:5px; /* FF1+ */
        -webkit-border-radius:5px; /* Saf3-4 */
        border-radius:5px;
        -moz-box-shadow: 0 0 4px rgba(0, 0, 0, 0.2);
        -webkit-box-shadow: 0 0 4px rgba(0, 0, 0, 0.2);
    }
    
    th, td {padding:18px 28px 18px; text-align:left; }
    
    th {padding-top:22px; text-shadow: 1px 1px 1px #fff; background:#e8eaeb;}
    
    td {border-top:1px solid #e0e0e0; border-right:1px solid #e0e0e0;}
    
    tr.odd-row td {background:#f6f6f6;}
    
    td.first, th.first {text-align:left}
    
    td.last {border-right:none;}
    
    /*
    Background gradients are completely unnecessary but a neat effect.
    */
    
    td {
        background: -moz-linear-gradient(100% 25% 90deg, #fefefe, #f9f9f9);
        background: -webkit-gradient(linear, 0% 0%, 0% 25%, from(#f9f9f9), to(#fefefe));
    }
    
    tr.odd-row td {
        background: -moz-linear-gradient(100% 25% 90deg, #f6f6f6, #f1f1f1);
        background: -webkit-gradient(linear, 0% 0%, 0% 25%, from(#f1f1f1), to(#f6f6f6));
    }
    
    th {
        background: -moz-linear-gradient(100% 20% 90deg, #e8eaeb, #ededed);
        background: -webkit-gradient(linear, 0% 0%, 0% 20%, from(#ededed), to(#e8eaeb));
    }
    


</style>

</head>
<body>
<center><h1>The result</h1></center>
<div id="content"  style="margin:0 auto;text-align:center">

    <table cellspacing="0"  >
    <tr><th>url</th><th>type</th><th>parameter</th><th>description</th><th>solution</td></tr>
    """
    location=location2
    try:
        file0 = open(location, "w")
        file0.write(head)
        file0.close()
        #req = httplib.HTTPConnection("shell-storm.org")
        #req.request("GET", "/api/?s="+str(value))
        #res = req.getresponse()
        res= open(location1,"r")
        data_1 = res.read().split('\n')
    except Exception, e:
        print "[!]Error : %s"%e
    for data in data_1:
        try:
            data0 = data.split("::::")
            url = data0[0]
            bugtype = data0[1]
            bugparameter = data0[2]
            description = cgi.escape(data0[3])
            description = description.replace('&lt;br&gt;','<br>')
            solution = data0[4]
        except(IndexError):
            pass
        if url:
            if bugtype:
                if bugparameter:
                    if description:
                        file1 = open(location, "a")
                        
                        current_info = "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"%(url,bugtype,bugparameter,description,solution)
                        file1.write(current_info+"\n")
                        file1.close()
    foot = """
         </table>

</div>

</body>
</html>
"""

    file2 = open(location, "a")
    file2.write(foot)
    file2.close()
    #subprocess.Popen(browser+location, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)




# 帮助函数
def usage():
    print "Fuck XSS and SQLinjection Tool"
    print
    print "Usage: python fuck_sqlinjection-xss.py -t host"
    print r'''-s --sqli                        - Only SQL injection detection.'''
    print r'''-x --xss                         - Only XSS detection.'''
    print r'''-r --read_sqlmap=sqlmap_output_dir   
                                 - Specify sqlmap's output results directory.
                                   Default : /usr/share/sqlmap/output'''
    print r'''-o --output=result_output_dir        
                                 - Specify test result output directory.
                                   Default : ./output'''
    print r'''-h --help                        - Call this using menu.'''
    print
    print
    print "Examples: "
    print "python fuck_sqlinjection-xss.py -t www.test.com"
    print "python fuck_sqlinjection-xss.py -t 10.206.6.11 -s"
    print "python fuck_sqlinjection-xss.py -t http://www.test.com:81 --read_sqlmap=/temp/output"
    print "python fuck_sqlinjection-xss.py -t https://www.test.com --output=/temp"
    print
    print "Tip: if the protocol is HTTPS or port is not 80 , please don't omit!"
    
    sys.exit(0)




# 主函数
def main():  
    global host
    global hhost
    global target
    global urls
    
    global sqli
    global xss
    global read_sqlmap
    global output
    
    
    # 读取命令行选项
    try:
        opts, args = getopt.getopt(sys.argv[1:], "sxr:o:ht:", ["sqli", "xss", "read_sqlmap", "output", "help", "target_host"])
    except getopt.GetoptError as err:
        print str(err)
        usage()
    
    
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-x", "--xss"):
            if xss is False:
                xss = True
            else:
                sqli = False
        elif o in ("-s", "--sqli"):
            if sqli is False:
                sqli = True
            else:
                xss = False
        elif o in ("-r", "--read_sqlmap"):
            b = re.search(r'/$', a)
            
            if b is None:
                read_sqlmap = str(a)
            else:
                c = str(a)[:-1]
                read_sqlmap = c
        elif o in ("-o", "--output"):
            b = re.search(r'/$', a)
            
            if b is None:
                output = str(a)
            else:
                c = str(a)[:-1]
                output = c
        elif o in ("-t", "--target_host"):
            d = re.search(r'/$', a)
            
            if d is not None:
                c = str(a)[:-1]
            else:
                c = str(a)
           
            b = re.search(r'^http(s|)://', c)
            
            if b is None:
                host = c
                ss = host.find(':')
                if ss > 0:
                    host = host[:ss]
                
                hhost = "http://%s" % c
            else:
                hhost = c
                
                e = re.search(r'^http(|s)://(.*)', c)
                if e is not None:
                    host = e.group(2)
                    ss = host.find(':')
                    if ss > 0:
                        host = host[:ss]                    
        else:
            assert False, "Unhandled Option"
        
        
    if hhost == "" or host == "":
        print "Please specity the target host by option -t"
        return
    
    path = "%s/%s" % (output, host)
    
    
    if sqli == True:
        
        # 判断该网站是否经过sql注入测试
        if os.path.isfile("%s/result_sqlinjection.txt" % path) is True:
            an = raw_input("The site has tested SQL injection, whether to re test?[y/N]")
            
            if an == '':
                sqli = False
            else:
                ans = an[:1]
                
                if ans not in ('y', 'Y'):
                    sqli = False
                else:
                    os.system("rm %s/result_sqlinjection.txt" % path)
    
    
    if xss == True:
        
        # 判断该网站是否经过xss测试
        if os.path.isfile("%s/result_xss.txt" % path) is True:
            an = raw_input("The site has tested XSS, whether to re test?[y/N]")
            
            if an == '':
                xss = False
            else:
                ans = an[:1]
                
                if ans not in ('y', 'Y'):
                    xss = False        
                else:
                    os.system("rm %s/result_xss.txt" % path)
      
    if sqli == False and xss == False:
        print "[*] End."
        return

    
    
    # 创建测试结果目录
    if os.path.isdir(path) is False:
        os.system("mkdir %s" % path)
        
    # 创建result.txt
    if os.path.isfile("%s/result.txt" % path):
        os.system("rm %s/result.txt" % path)
        os.system("touch %s/result.txt" % path)
    
    if os.path.isfile("%s/result.html" % path):
        os.system("rm %s/result.html" % path)
    
    
    # 爬取目标站点
    print "[*] Start to crawl the site."
    
    spider = Spider(hhost)
    target,urls = spider.getallform()
    
    print "[*] Crawling down. The url list is: "
    print
    for aurl in urls:
        print aurl
    print
    print "[*] Start to scan in 5 seconds."
    time.sleep(1)
    print "[*] Start to scan in 4 seconds."
    time.sleep(1)
    print "[*] Start to scan in 3 seconds."
    time.sleep(1)    
    print "[*] Start to scan in 2 seconds."
    time.sleep(1)    
    print "[*] Start to scan in 1 seconds."
    time.sleep(1)
    print "[*] Start."
    print
    
    
    # 进行测试并输出结果文件
    if sqli == True:
        if os.path.isfile("%s/result_sqlinjection.txt" % path) is False:
            os.system("touch %s/result_sqlinjection.txt" % path)
        
        fuck_header_sqlinjection(target)
        #fuck_get_sqlinjection(target)
        fuck_post_sqlinjection(target)
        
        try:
            f = open("%s/result_sqlinjection.txt" % path, 'r')
            content = f.read()
        except:
            pass
        finally:
            f.close()
        
        if content == '':
            try:
                f = open("%s/result_sqlinjection.txt" % path, 'a')
                f.write("This tool has not found SQL injection.")
            except:
                pass
            finally:
                f.close()
                
                
    if xss == True:
        if os.path.isfile("%s/result_xss.txt" % path) is False:
            os.system("touch %s/result_xss.txt" % path)
        
        fuck_reflected_xss(target)
        fuck_storage_xss(target)
        
        try:
            f = open("%s/result_xss.txt" % path, 'r')
            content = f.read()
        except:
            pass
        finally:
            f.close()
        
        if content == '':
            try:
                f = open("%s/result_xss.txt" % path, 'a')
                f.write("This tool has not found XSS.")
            except:
                pass
            finally:
                f.close()
                           
    
    try:
        shell_storm("%s/result.txt" % path, "%s/result.html" % path)
        os.system("rm %s/result.txt" % path)
        
        print 'Opening the result...'
        os.system("iceweasel %s/result.html" % path)
    except:
        print 'Create HTML document failure!'
    
    
    print "[*] End."
    return 0

if __name__ == '__main__':
    main()