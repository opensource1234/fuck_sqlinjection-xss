#coding=utf-8

import urllib2
import urllib
import os
import sys
import thread

# dict转化成list
def dict_to_list(d, middle):
    l = []
    for key,value in d.iteritems():
        l.append("%s%s%s" % (str(key), str(middle), str(value)))
    return l

# 构造新的Get请求
def get_newurl(url, start, hashs, paramscp, param, value, fuzz):
    
    paramscp[param] = "%s%s" % (str(value), str(fuzz))
    newkeys = dict_to_list(params, '=')
    newkeys = '&'.join(newkeys)

    # 新的Get请求
    newurl = "%s%s%s" % (url[:start+1], newkeys, hashs)
    
    return newurl

# 检测是否存在Get类型的sql注入
def fuck_get_sqlinjection(target):
    
    # 测试结果
    result = {}
    
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
        for param,value in params.iteritems:
            
            paramscp = params.copy()
            
            # 加单引号
            newurl = get_newurl(url, start, hashs, paramscp, param, value, '\'')
            
            