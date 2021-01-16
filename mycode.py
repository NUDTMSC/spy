mycode=r'''

# coding=utf-8
import threading
from time import time,sleep,localtime
from pprint import pprint
import os
import sys

start_time=time()
maxthread=10            #最大线程数
run_timeout=60         #最长运行时间
lock=threading.Lock()   #线程锁
thread_count=0          #正在运行的线程数
exitFlag = 0
page_i=0

def mywrite_line(filename,the_content,mode='a+'):
    lock.acquire()
    with open(filename,mode) as file:
        file.write(the_content+'\n')
    lock.release()

def read_oldurl():
    oldurl=open('url.txt','a+')
    oldurl.seek(0)
    oldurl=list(oldurl)
    i=0
    ret=[[],[]]
    while i<len(oldurl):
        sep_index=oldurl[i].find(':')
        ret[0].append(oldurl[i][:sep_index])
        ret[1].append(oldurl[i][sep_index+1:-1])
        i+=1
    return ret
def get_jpgurl(s0):#获取最高画质版本的url
    try:
        if s0.find('Higher quality')==-1:
            s1=s0[s0.find(r'<td>current</td>'):]
            s2=s1[s1.find('/project'):s1.find('">')]
            s2='https://www.baka-tsuki.org'+s2
        else:
            s0=s0[:s0.find('Higher quality')]
            while s0.find('<tr>')!=-1:
                s0=s0[s0.find('<tr>')+4:]
            s1=s0
            s2=s1[s1.find('/project'):]
            s2=s2[:s2.find('">')]
            s2='https://www.baka-tsuki.org'+s2
        
        return s2
    except:
        print('图片url解析失败')
        return None
def get_content(url):#获取网页源码
    import requests
    import time
    s=requests.session()
    headers={
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding':'gzip, deflate',
    'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control':'max-age=7200',
    'Upgrade-Insecure-Requests':'1',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75',
    }
    s.headers.update(headers)
    flag=0
    while flag<3:
        starttime=time.time()
        try:
            
            html=s.get(url=url)

            return html.text,html.content
        except:
            flag+=1
            print('error: 获取不到以下网页的源码   尝试次数：%d   本次用时：%f\n%s'%(flag,time.time()-starttime,url))
            time.sleep(1)
    print('error: 多次尝试仍然没有获得以下网页的源码\n%s'%url)
    return None,None
def savepic(url,dir):#图片读取和保存
    null,piccontent=get_content(url)
    if piccontent==None:
        return
    try:
        f =open(dir)
        f.close()
    except IOError:
        with open(dir, 'wb') as file:
            file.write(piccontent)
def get_picname(url):#通过url提取图片章节和图片名
    #example:
    # url='https://www.baka-tsuki.org/project/images/f/f2/GT_Index_v01_000.jpg'
    na=url
    while na.find(r':')!=-1:
        na=na[na.find(r':')+1:]
    
    return na
def read_page_index():
    lines=list(open('jpgpage.txt'))
    i=1
    index=[]
    while lines[i]!='end\n':
        jpgpage=lines[i][:-1]
        index.append(jpgpage)
        i+=1
    return index
def get_jpgpage():
    global page_i
    if page_i<len(page_index):
        page_i+=1
        return page_index[page_i-1]
    else:
        return None


def download_pic(threadName):
    if exitFlag:
        threadName.exit()
    global maxthread
    global oldurl
    files = os.listdir()                         # 读入已下载的文件
    lock.acquire()
    jpg_page=get_jpgpage()
    lock.release()
    while jpg_page!=None:
        start1=time()
        pic_name=get_picname(jpg_page)
        if pic_name in files:
            jpg_page=get_jpgpage()
            print(pic_name+'--图片已存在')
            mywrite_line('run_logs.txt',pic_name+'--图片已存在')

            continue
        if pic_name not in oldurl[0]:                  #没有找到图片下载链接
            jpg_content,null=get_content(jpg_page)      #获取图片下载链接
            jpgurl=get_jpgurl(jpg_content)
            if jpgurl!=None:

                mywrite_line('url.txt',pic_name+':'+jpgurl)
                mywrite_line('run_logs.txt',threadName+'：获取图片下载链接完成，用时：%f    链接:%s'%(time()-start1,jpgurl))
                print(threadName+'：获取图片下载链接完成，用时：%f    链接:%s'%(time()-start1,jpgurl))
                

            else:
                mywrite_line('run_logs.txt',threadName+'----'+pic_name+'获取图片下载链接失败')
                print(threadName+'----'+pic_name+'获取图片下载链接失败')
                

                continue
        else:
            jpgurl=oldurl[1][oldurl[0].index(pic_name)]
            print(threadName+'：链接已存在    链接:%s'%(jpgurl))
            mywrite_line('run_logs.txt',threadName+'：链接已存在    链接:%s'%(jpgurl))

        print(threadName+'：开始下载图片%s   链接：%s'%(pic_name,jpgurl))
        mywrite_line('run_logs.txt',threadName+'：开始下载图片%s   链接：%s'%(pic_name,jpgurl))

        savepic(jpgurl,pic_name)                #图片下载
        start3=time()

        print(threadName+':图片下载完成，url:'+jpgurl+'，用时%f'%(start3-start1))
        mywrite_line('run_logs.txt',threadName+':图片下载完成，url:'+jpgurl+'，用时%f'%(start3-start1))

        jpg_page=get_jpgpage()
class myThread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        global thread_count
        print ("开始线程：" + self.name)
        mywrite_line('run_logs.txt',"开始线程：" + self.name)
        
        download_pic(self.name)
        
        lock.acquire()
        thread_count-=1
        lock.release()
        print ("退出线程：" + self.name)
        print('剩余线程：%d'%thread_count)
        mywrite_line('run_logs.txt',"退出线程：" + self.name + '\n剩余线程：%d'%thread_count)



page_index = read_page_index()
oldurl=read_oldurl()
pprint(page_index)
pprint(oldurl)
try:
    os.system('del '+'timeout.txt')
except:
    print('')

start_timea=localtime(start_time)
mywrite_line('run_logs.txt','\n\n\n\n\n-----------------------%d/%d/%d  %d:%d:%d---------------------------------'%(
    start_timea.tm_year,start_timea.tm_mon,start_timea.tm_mday,start_timea.tm_hour,start_timea.tm_min,start_timea.tm_sec))
# 创建新线程
threads=[]
for j in range(maxthread):
    threads.append(myThread(j, "Thread-%d"%j))
    print('线程%d创建成功'%j)
# 开启新线程
for t in threads:
    lock.acquire()
    thread_count+=1
    lock.release()
    t.setDaemon(True)
    t.start()

timeout_flag=0
while timeout_flag<run_timeout and thread_count>0:
    sleep(1)
    timeout_flag+=1
if(timeout_flag>=run_timeout):
    mywrite_line('timeout.txt','剩余线程：%d'%thread_count)
    mywrite_line('run_logs.txt','运行超时，剩余线程：%d'%thread_count)

mywrite_line('run_logs.txt',"退出主线程"+'\n总用时%f'%(time()-start_time))
print("退出主线程")
print('总用时%f'%(time()-start_time))

'''








mybat=r'''
cd %~dp0
python code.py
del code.py
exit
'''
