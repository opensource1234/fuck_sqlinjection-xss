#coding=utf-8

import urllib2
import urllib
import os
import sys
import thread
import re

# 目标站点域名
host = "10.206.6.11"

# dict转化成list
def dict_to_list(d, middle):
    l = []
    for key,value in d.iteritems():
        l.append("%s%s%s" % (str(key), str(middle), str(value)))
    return l

'''
# 构造新的Get请求
def get_newurl(url, start, hashs, paramscp, param, value, fuzz):
    
    paramscp[param] = "%s%s" % (str(value), str(fuzz))
    newkeys = dict_to_list(params, '=')
    newkeys = '&'.join(newkeys)

    # 新的Get请求
    newurl = "%s%s%s" % (url[:start+1], newkeys, hashs)
    
    return newurl
'''

# 生成测试结果文件
def outputfile(url):
    global host
        
    result = ""
    path = "/usr/share/sqlmap/output/%s/log" % host
        
    if os.path.isfile(path):
        f = open(path, 'r')
        content = f.read()
        f.close()
        
        # 某个参数检测完之后删除对应sqlmap日志目录
        os.system("rm -r /usr/share/sqlmap/output/%s" % host)
            
        if content == '':
            pass
        else:
            result = "%s\n" % url
            result += re.search(r'---(.|\n)+---', content)
            result += "\n\n"
            
            filepath = "%s/result.txt" % host
            
            output = open(filepath, 'a')
            output.write(result)
            output.close()
    
    return 0


# 使用sqlmap进行GET注入测试
def sqlmap_get(url, param):
    
    os.system("sqlmap -u %s -p %s" % (url, str(param)))
    
    return 0

# 使用sqlmap进行POST注入测试
def sqlmap_post(url):
    
    os.system("sqlmap -u %s --forms" % url)
    
    return 0


# 检测是否存在GET类型的sql注入
def fuck_get_sqlinjection(target):
    
    for url in target:
        
        # 获得Get请求中的参数
        params = {}
        keys = ''
        hashs = ''
        
        start = url.index('?')
        if start < 0:
            continue
        else:
            end = url.index('#')
            
            if end > 0:
                keys = url[start+1:end]
                hashs = url[end:]
            else:
                keys = url[start+1:]
                
            keys = keys.split('&')
            map(lambda x:params.setdefault(x.split('=')[0], x.split('=')[1]), keys)
            
    
        # 通过改变参数的值进行sql注入测试     
        for param in params:
            
            try:
                sqlmap_get(url, param)
            except KeyboardInterrupt:
                continue
            finally:
                outputfile(url)

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
                
            
        
        


    
            
            
            
            
            