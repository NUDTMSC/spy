def mywrite_line(filename,the_content,mode='a+'):
    with open(filename,mode) as file:
        file.write(the_content+'\n')

def mkdir(path):
    import os
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)            #makedirs 创建文件时如果路径不存在会创建这个路径
def get_illustration():#获取某一章所有插画页面的url
    from selenium import webdriver
    from time import sleep #导入时间包
    from selenium.webdriver.common.keys import Keys
    from pprint import pprint

    mylink=[]
    driver = webdriver.Edge("D:\\Codefield\\python\\spy\\driver\\msedgedriver.exe")      # Edge浏览器
    # 打开网页
    urls=['https://www.baka-tsuki.org/project/index.php?title=To_Aru_Majutsu_no_Index_(German)',
            'https://www.baka-tsuki.org/project/index.php?title=Toaru_Majutsu_no_Index:_New_Testament',
            'https://www.baka-tsuki.org/project/index.php?title=Toaru_Majutsu_no_Index:_Genesis_Testament']

    #urls=['https://www.baka-tsuki.org/project/index.php?title=The_Unexplored_Summon_Blood_Sign']
    #urls=['https://www.baka-tsuki.org/project/index.php?title=Toaru_Majutsu_no_Index:_New_Testament']
    #urls=['https://www.baka-tsuki.org/project/index.php?title=Toaru_Majutsu_no_Index:_Genesis_Testament']
    for url in urls:
        try:
            driver.get(url) # 打开url网页 比如 driver.get("http://www.baidu.com")
        except:
            print('找不到illustration页面')

        # sleep(2) #使用时间包，休眠2s
        eles=driver.find_elements_by_link_text("Illustrations")#精确匹配超链接载体
        if len(eles)==0:
            eles=driver.find_elements_by_link_text("Illustrationen")
        for ele in eles:
            tems=ele.get_attribute('outerHTML')
            tems=tems[tems.find('/project'):]
            mylink.append('https://www.baka-tsuki.org'+tems[:tems.find('"')])
    driver.close()

    return(sorted(set(mylink),key=mylink.index))
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
    while flag<10:
        starttime=time.time()
        try:
            
            html=s.get(url=url,timeout=60)

            return html.text,html.content
        except:
            flag+=1
            print('error: 获取不到以下网页的源码   尝试次数：%d   本次用时：%f\n%s'%(flag,time.time()-starttime,url))
            time.sleep(1)
    print('error: 多次尝试仍然没有获得以下网页的源码\n%s'%url)
    return None,None



def get_jpgpage(s0):#提取某一章插画页面url
    ret=[]
    while s0.find('class="image"')!=-1:
        s1=s0[:s0.find('class="image"')]
        while s1.find('href=')!=-1:
            s1=s1[s1.find('href=')+4:]
        s2=s1[s1.find('/project'):]
        s2=s2[:s2.find('"')]
        s2='https://www.baka-tsuki.org'+s2
        s0=s0[s0.find('class="image"')+10:]
        ret.append(s2)
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
def get_dirname(url,odir):#提取文件夹路径
    di=url
    di=di[:di.find('_Illu')]
    while di.find(':')!=-1:
        di=di[di.find(':')+1:]
    di=odir+di
    return di
def get_picname(url):#通过url提取图片章节和图片名
    #example:
    # url='https://www.baka-tsuki.org/project/images/f/f2/GT_Index_v01_000.jpg'
    na=url
    while na.find(r':')!=-1:
        na=na[na.find(r':')+1:]
    
    return na

def makepicdir(url,odir):#创建文件夹
    path=get_dirname(url,odir)
    mkdir(path)
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
    #print('下载成功:'+filname)    

#url='https://www.baka-tsuki.org/project/index.php?title=Toaru_Majutsu_no_Index:_New_Testament_Band_1_Illustrationen'
# savepic(urls,'D:/WMX/小说/魔禁插画/')
#makepicdir(url,'D:/WMX/小说/魔禁插画/')
#from pprint import pprint
#pprint(get_illustration())