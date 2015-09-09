#coding=utf-8

import urllib2
import urllib
import os
import sys
import time
import re
import cookielib



# 目标站点域名
host = "10.206.6.11"

# 爬到的页面url
target = {'http://10.206.6.11/new.php?id=2':[],
          'http://10.206.6.11/book.php':[r'''<form name="from1" id="from1" method="post" action="book.php?action=add">
			<table border="0" cellspacing="0" cellpadding="0" id="fortab">
			<tr>
			<td>标题*：</td>
			<td><input name="title" type="text"/></td>
			</tr>
			<tr>
			<td>姓名*：</td>
			<td><input name="name" type="text" /></td>
			</tr>
			<tr>
			<td>Email*：</td>
			<td><input name="email" type="text" /></td>
			</tr>
			<tr>
			<td>浏览权限：</td>
			<td><select name="select">
    			<option value="all">所有人</option>
    			<option value="mst">管理员</option>
				</select>
			</td>
			
			<tr>
			<td>验证码*：</td>
			<td><input name="capt" type="text" size="5" maxlength="4" />
			<img id='rand' src='captcha.php'></img><a href='javascript:chk()'>看不清楚</a></td>
			</tr>
			
			</tr>
			<tr>
			<td>内容*：</td>
			<td><textarea name="ms" rows="10"/></textarea></td>
			</tr>
			</table>
			<input type="submit" name="submit" value="提交" class="submails" />
			</form>''',]}

# dict转化成list
def dict_to_list(d, middle):
    l = []
    for key,value in d.iteritems():
        l.append("%s%s%s" % (str(key), str(middle), str(value)))
    return l


# 获取页面源码
def get_source(url):
    
    headers = {}
    headers['User-Agent'] = 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)'
    
    request = urllib2.Request(url, headers=headers)
    response = urllib2.urlopen(request)
    
    return response.read()


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
    newkeys = dict_to_list(params, '=')
    newkeys = '&'.join(newkeys)

    # 新的Get请求
    newurl = "%s%s%s" % (url[:start+1], newkeys, hashs)
    
    return newurl


# 生成sql注入测试结果文件
def outputfile(url):
    global host
        
    result = ""
    path = "/usr/share/sqlmap/output/%s/log" % host
        
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
            result += (re.search(r'---(.|\n)+---', str(content))).group(0)
            result += "\n\n"
            
            filepath = "output/%s/result_sqlinjection.txt" % host
            
            try:
                output = open(filepath, 'r')
            
                # 若与已得到的结果不重复则写入
                out = output.read()
                if result in out:
                    output.close()
                else:
                    output.close()
                    
                    try:
                        output = open(filepath, 'a')
                        output.write(result)
                    except:
                        pass
                    finally:
                        output.close()
            except:
                pass
    
    return 0


# 生成XSS测试结果文件
def outputfile2(url, result):
    global host
    
    path = "output/%s/result_xss.txt" % host
    
    try:
        f = open(path, 'a')
        f.write("%s:\n%s" % (url, result))
    except:
        pass
    finally:
        f.close()
    
    return



# 使用sqlmap进行GET注入测试
def sqlmap_get(url, param):
    
    os.system("sqlmap -u %s -p %s --batch" % (url, str(param)))
    
    return 0

# 使用sqlmap进行POST注入测试
def sqlmap_post(url):
    
    os.system("sqlmap -u %s --forms --batch" % url)
    
    return 0

# 使用sqlmap进行COOKIES注入测试
def sqlmap_cookies(url, cookies):
    
    os.system("sqlmap -u %s --cookie=%s --batch" % (url, cookies))
    
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
                

# 检测是否存在COOKIES类型的注入
def fuck_cookies_sqlinjection(target):
    
    for url in target:
        start = url.find('?')
        
        if start < 0:
            continue
        else:
            
            # 获取页面cookies
            cj = cookielib.CookieJar()
    
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    
            opener.add_handler = [('User-agent','Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')]
    
            opener.open(url)
    
            cookies = []
            coo = ''
    
            for index,cookie in enumerate(cj):
                coo = re.search(r" (.+) for ", str(cookie))
                coo = coo.group(1)
                cookies.append(coo)
                
            cookies = ';'.join(cookies)
            
            cj.clear()
            
            # 如果没有获取页面cookies则跳过
            if cookies == '':
                continue
            
    
            # 测试cookies注入
            try:
                sqlmap_cookies(url, cookies)
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
        
        start, params, hashs = url_params(url)
        
        newurl = ''
        source = ''
        
        # 测试HTTP header中的XSS(CRLF注入)
        
        
        # 测试hash中的XSS
        if hashs == "":
            pass
        else:
            for line in lines:
                
                payload = "%s%s" % (hashs, line)
                
                newurl = get_newurl(url, start, payload, paramscp, param, value, '')
        
                print "[fragment XSS test] test : %s" % payload
                source = get_source(newurl)
                
                if line in source:
                    
                    print "[*] Maybe find a XSS!"
                    
                    result = "Maybe there is a XSS in fragment! Payload : %s" % payload
                    outputfile2(url, result)
                    
                    break        
                              
        # 测试GET参数中的XSS
        if params == {}:
            continue
        
        for param, value in params.iteritems():
            
            paramscp = params.copy()
            
            for line in lines:
                
                fuzz = line
                payload = "%s%s" % (str(value), fuzz)
                
                newurl = get_newurl(url, start, hashs, paramscp, param, value, fuzz)
                
                source = get_source(newurl)
                
                if fuzz in source:
                    
                    print "[*] Maybe find a XSS!"
                    
                    result = "Maybe there is a XSS in parameter %s! Payload : %s" % (str(param), payload)
                    outputfile2(url, result)                    
                    
                    break
    
    return



# 主函数
def main():
    
    global host
    global target
    
    path = "output/%s" % host
    
    # 判断该网站是否经过sql注入测试
    
    
    # 判断该网站是否经过xss测试
    
    
    # 创建测试结果目录及文件
    if os.path.isdir(path) is False:
        os.system("mkdir %s" % path)
    
    if os.path.isfile("%s/result_sqlinjection.txt" % path) is False:
        os.system("touch %s/result_sqlinjection.txt" % path)
    
    if os.path.isfile("%s/result_xss.txt" % path) is False:
        os.system("touch %s/result_xss.txt" % path)
        
    
    
    
    # 进行sql注入测试    
    fuck_cookies_sqlinjection(target)
    print '--------------------cookies over---------------------'
            
    time.sleep(5)    
       
    fuck_get_sqlinjection(target)
    print '----------------------get over-----------------------'
        
    time.sleep(5)
    fuck_post_sqlinjection(target)
    print '----------------------post over----------------------'
        
    time.sleep(5)
      
    return 0

if __name__ == '__main__':
    main()