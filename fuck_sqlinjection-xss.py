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


# 目标站点(test)
host = "10.206.6.11"
hhost = "http://10.206.6.11:80"

# 爬到的页面url(test)
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

# 一些全局变量
sqli            = True
xss             = True
read_sqlmap     = '/usr/share/sqlmap/output'
output          = './output'





# 爬取目标站点所有页面



# 生成n字节随机字符串
def get_randstr(n):
    randstr = ''
    ch = ''
    
    for i in xrange(n):
        ch = string.join(random.sample(['z','y','x','w','v','u','t','s','r','q','p','o','n','m','l','k','j','i','h','g','f','e','d','c','b','a','0','1','2','3','4','5','6','7','8','9'], 1)).replace(' ','')
        randstr += ch
        
    return randstr


# 解析form表单




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
    
    headers = {}
    headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'
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
    newkeys = dict_to_list(paramscp, '=')
    newkeys = '&'.join(newkeys)

    # 新的GET请求
    newurl = "%s%s%s" % (url[:start+1], newkeys, hashs)
    
    return newurl


# 生成sql注入测试结果文件
def outputfile(url):
    global host
    global read_sqlmap
        
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
    
    return 0



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
    
            opener.add_handler = [('User-agent','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0')]
    
            opener.open(url)
    
            cookies = []
            coo = ''
    
            for index,cookie in enumerate(cj):
                coo = re.search(r" (.+) for ", str(cookie))
                if coo is not None:
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
        
        
        # 测试hash中的XSS
        if hashs == "":
            pass
        else:
            for line in lines:
                
                payload = "%s%s" % (hashs, line)
                
                newurl = get_newurl(url, start, payload, paramscp, param, value, '')
        
                print "[fragment XSS test] : %s" % payload
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
                
                print "[get parameter XSS test] : %s" % payload
                
                newurl = get_newurl(url, start, hashs, paramscp, param, value, fuzz)
                
                source = get_source(newurl)
                
                if fuzz in source:
                    
                    print "[*] Maybe find a XSS!"
                    
                    result = "Maybe there is a XSS in get parameter %s! Payload : %s" % (str(param), payload)
                    outputfile2(url, result)                    
                    
                    break
    
    return


# 检测是否存在存储型XSS
def fuck_storage_xss(target):
    global hhost
    
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
            postdata = {}
            action = ''
            
            # 得到表单提交地址
            goal = re.search(r"action( |\n)*=( |\n)*\"((.|\n)*?)\"", form)
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
                            g = re.search(r'.*/', url)
                            direc = ''
                    
                            if g is not None:
                                direc = g.group(0)
                                action = "%s%s" % (direc, go)
                            else:
                                action = "%s/%s" % (url, go)
            
            else:
                continue
            
            # 填写表单参数
            parsedform = parseform(form)
            
            for param in parsedform:
                if param[0].lower() not in ['text', 'password', 'textarea',]:
                    continue
                
                for line in lines:
                    payload = line
                    
                    postdata = get_POST_data(parsedform, param, payload)
                    
                    # 提交表单
                    print "[post parameter XSS test] : %s" % payload
                    
                    post_data = urllib.urlencode(postdata)
                    req = urllib2.urlopen(action, post_data)
                    
                    source = get_source(url)
                    
                    if payload in source:
                        
                        print "[*] Maybe find a XSS!"
                        
                        result = "Maybe there is a XSS in post parameter %s! Payload : %s" % (str(param), payload)
                        outputfile2(url, result)                    
                        
                        break               
    
    return

# 帮助函数
def usage():
    print "Fuck XSS and SQLinjection Tool"
    print
    print "Usage: python fuck_sqlinjection-xss.py -t host"
    print r'''-s --sqli          - Only SQL injection detection.'''
    print r'''-x --xss           - Only XSS detection.'''
    print r'''-r --read_sqlmap=sqlmap_output_dir   
                                 - Specify sqlmap's output results directory.
                                   Default : /usr/share/sqlmap/output'''
    print r'''-o --output=result_output_dir        
                                 - Specify test result output directory.
                                   Default : ./output'''
    print r'''-h --help          - Call this using menu.'''
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
        elif o in ("-s", "--sqli"):
            if xss is False:
                xss = True
            else:
                sqli = False
        elif o in ("-x", "--xss"):
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
                hhost = "http://%s" % c
            else:
                hhost = c
                
                e = re.search(r'^http(|s)://(.*)', c)
                if e is not None:
                    host = e.group(2)
        else:
            assert False, "Unhandled Option"
        
        
    if hhost == "" or host == "":
        print "Please specity the target host by option -t"
        return
    
    path = "%s/%s" % (output, host)
    
    
    # 判断该网站是否经过sql注入测试
    
    
    # 判断该网站是否经过xss测试
    
    
    # 创建测试结果目录及文件
    if os.path.isdir(path) is False:
        os.system("mkdir %s" % path)
    
    if os.path.isfile("%s/result_sqlinjection.txt" % path) is False:
        os.system("touch %s/result_sqlinjection.txt" % path)
    
    if os.path.isfile("%s/result_xss.txt" % path) is False:
        os.system("touch %s/result_xss.txt" % path)
        
    
    
    '''
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
    '''
    '''
    # 进行XSS测试
    fuck_reflected_xss(target)
    print '------------ reflected xss over ------------'
    
    time.sleep(5)
    fuck_storage_xss(target)
    print '------------ storage xss over ------------'
    time.sleep(5)
    '''
     
    return 0

if __name__ == '__main__':
    main()