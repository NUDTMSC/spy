from function import *
from pprint import pprint
import threading
import time
import os
from mycode import *
maxthread=10
root_dir='D:\\WMX\\小说\\魔禁插画test\\'
mkdir(root_dir)
lock=threading.Lock()
thread_count=0
exitFlag = 0

if not os.path.exists(root_dir+'\\illustration.txt'):
    il_index = get_illustration()
    for illustration in il_index:
        mywrite_line(root_dir+'\\illustration.txt',illustration)
else:
    il_index=[]
    with open(root_dir+'\\illustration.txt','r') as file:
        illustrations=list(file)
    for illustration in illustrations:
        il_index.append(illustration[:-1])
    
pprint(il_index)
print(len(il_index))

illu_i=0

start_time=time.time()
start_timea=time.localtime(start_time)
mywrite_line(root_dir+'logs.txt','\n\n\n\n\n-----------------------%d/%d/%d  %d:%d:%d---------------------------------'%(
    start_timea.tm_year,start_timea.tm_mon,start_timea.tm_mday,start_timea.tm_hour,start_timea.tm_min,start_timea.tm_sec))


def get_illu():
    global illu_i
    if illu_i<len(il_index):
        illu_i+=1
        return il_index[illu_i-1]
    else:
        return None
def save_picpage(threadName):
    lock.acquire()
    illu=get_illu()
    lock.release()
    global root_dir
    while illu!=None:
        if exitFlag:
            threadName.exit()
        start1=time.time()
        dirname=get_dirname(illu,root_dir)  #最后不带\\
        if not os.path.exists(dirname+'\\jpgpage.txt') or list(open(dirname+'\\jpgpage.txt'))[-1]!='end\n':#url文件存在
            #获取图片页面的网址
            threadstart_time=time.time()
            print(threadName+':'+illu)
            print(threadName+':'+dirname)
            illu_text,null=get_content(illu)
            jpgs=get_jpgpage(illu_text)
            #将图片的页面保存到文件里
            mkdir(dirname)                                          #创建图片文件夹
            mywrite_line(dirname+'\\jpgpage.txt',dirname,'w')
            for jpg_page in jpgs:
                mywrite_line(dirname+'\\jpgpage.txt',jpg_page)
            mywrite_line(dirname+'\\jpgpage.txt','end')
            print(threadName+'----目录：%s ----图片页面地址全部写入完成，总用时：%f'%(dirname,time.time()-threadstart_time))
        
        timeout_flag=0
        while 1:
            with open(dirname+'\\code.py','w',encoding='utf-8') as file:
                file.write(mycode)
            with open(dirname+'\\bat.bat','w',encoding='utf-8') as file:
                file.write(mybat)
            os.system('start '+dirname+'\\bat.bat')
            while os.path.exists(dirname+'\\code.py'):
                time.sleep(1)
            if os.path.exists(dirname+'\\timeout.txt') and timeout_flag<3:
                timeout_flag+=1
                print(dirname+'  下载超时%d次，总耗时时%f'%(timeout_flag,time.time()-start1))
            else:
                break


        os.system('del '+dirname+'\\bat.bat')
        if not os.path.exists(dirname+'\\timeout.txt'):
            print(dirname+'  下载完成，用时%f'%(time.time()-start1))
        else:
            print(dirname+'  下载失败，总用时%f'%(time.time()-start1))
        illu=get_illu()
class myThread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        global thread_count
        print ("开始线程：" + self.name)

        save_picpage(self.name)
        
        lock.acquire()
        thread_count-=1
        lock.release()
        print ("退出线程：" + self.name)
        print('剩余线程：%d'%thread_count)




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
    t.start()
#等待线程结束
for t in threads:
    t.join()

print ("退出主线程")
mywrite_line(root_dir+'logs.txt','用时：%f'%(time.time()-start_time))



