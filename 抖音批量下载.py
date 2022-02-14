from selenium import webdriver
import pyautogui as pg
import time
import requests
import cv2
import os

####################自定义下载参数#############################
# 任意参数出错,直接导致下载失败

url_count = 100         #需要爬视频取个数 ,确认好视频个数
tabulation = 1          #0作品; 1喜欢; 2收藏; 注：只能爬取自己的收藏，爬取他人的喜欢视频前确认是否公开
video_path = "C:/Users/xiao'fang/桌面/video/" #视频保存目录,注意末尾“/”,  注：若不存在请提前创建完成
you_url = "" #账号主页

####################自定义下载参数#############################

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
drive = webdriver.Chrome(options=options)
drive.get(you_url)

####################自定义函数#################################
#获取验证码图片url
def get_img():
    data = drive.find_element_by_class_name("captcha_verify_img--wrapper").find_elements_by_tag_name("img")
    url_a = data[0].get_attribute("src")
    url_b = data[1].get_attribute("src")
    return url_a,url_b

#下载文件
def download(path,url):
    data = requests.get(url).content
    while True:
        time.sleep(0.2)
        if len(data)>5:
            break
    with open(path,"wb") as f:
        f.write(data)

#图片去噪
def canny(img):
    img = cv2.GaussianBlur(img,(3,3),0)
    return cv2.Canny(img,50,150)

#获取滑块移动距离
def distance():
    img_b = cv2.imread("b.png", 0)
    img_a = cv2.imread("a.jpeg", 0)
    img_b = cv2.resize(img_b,(271,271))
    img_a = cv2.resize(img_a,(1360,848))
    res = cv2.matchTemplate(canny(img_b), canny(img_a), cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    data = max_loc[0]
    w, h = img_b.shape[::-1]
    w1, h1 = img_a.shape[::-1]
    data += w/2
    data = (data/w1)*271      #滑块首尾距离271
    data += (data-135.5)*0.3  #偏移调整参数0.3 (0.1~0.5)
    data = round(data,1)      #保留一位小数
    print(data)
    return data

#获取滑块位置
def location_hk():
    rect = drive.find_element_by_class_name("sc-kkGfuU").rect  #滑块相对浏览器位置
    position = drive.get_window_position()           #浏览器位置
    x = position['x']+rect['x']+rect['width']/2
    y = position['y']+rect['y']+rect['height']/2+120 #偏移量(误差)120
    return x,y

#移动滑块
def move_hk(x,y,data):
    pg.moveTo(x,y,1)
    pg.mouseDown(x,y,button='left')
    pg.moveTo(x+200,y+1,1)
    pg.moveTo(x+90,y-1,1)
    pg.moveTo(x+130,y-3,1)
    pg.moveTo(x+data,y-1,1.5)
    pg.mouseUp(x+data,y-1,button='left')

#执行验证
def YZ():
    url_a,url_b = get_img()
    download("a.jpeg",url_a)
    download("b.png",url_b)
    data = distance()
    x,y = location_hk()
    os.remove("a.jpeg")
    os.remove("b.png")
    move_hk(x,y,data)

#获取视频名字
kong = 1
def get_name():
    global kong
    try:
        span = drive.find_element_by_class_name("z8_VexPf").find_element_by_class_name("Nu66P_ba")
        name = span.text
    except:
        name = ""
    if name=="":
        name = str(kong)
        kong+=1
    name = video_path+name+".mp4"
    return name
#解析主页URL
def Analyzing(url):
    drive.get(url)
    while True:
        try:
            try: #判断是否出现人机验证
                drive.find_element_by_id("verify-points")
                print("正在进行人机验证，请勿移动鼠标！")
                YZ()
                break
            except:
                False
            video = drive.find_element_by_tag_name("video")
            vidio_URL = video.find_elements_by_tag_name("source")
            vidio_URL = vidio_URL[3].get_attribute('src')
            break
        except:
            time.sleep(0.5)
    vidio_name = get_name()
    return vidio_URL,vidio_name
####################自定义函数#################################

####################自动人机验证##########################
a = 0
while True:
    try:
        drive.find_element_by_class_name("secsdk-captcha-drag-icon")
        print("正在进行人机验证，请勿移动鼠标！")
        YZ()
        time.sleep(2)
    except:
        time.sleep(0.5)
        a+=1
        if a>=5:
            print("未发现人机认证窗口！")
            break
####################账号登录##############################
while True:
    try:
        logging = drive.find_element_by_class_name("web-login")
        logging = drive.find_element_by_class_name("login-guide__btn")
        logging.click()
        print("请登陆")
        break
    except:
        time.sleep(1)
while True:
    try:
        drive.find_element_by_id("login-pannel")
        time.sleep(1)
    except:
        print("登录成功")
        break
####################点击对应列表##########################
while True:
    try:
        button = drive.find_elements_by_class_name("CANY1MjK")
        button[tabulation].click()
        time.sleep(1)
        print("已进入对应列表")
        break
    except:
        time.sleep(1)
###################获取列表视频链接###########################
while True:
    try:
        ul = drive.find_elements_by_class_name("ARNw21RN")[tabulation]
        li = ul.find_elements_by_class_name("ECMy_Zdt")
        count = len(li)
        break
    except:
        time.sleep(1)
######################获取指定个数链接############################
while True:
    drive.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    while True:
        li = ul.find_elements_by_class_name("ECMy_Zdt")
        if len(li)>count:
            break
        time.sleep(0.5)
    count = len(li)
    print("已发现",count,"个")
    if count>=url_count:
        break
print("结束")
li = ul.find_elements_by_class_name("ECMy_Zdt")
####################获取主页URL#############################
list1_URL = []
for i in range(url_count):
    a = li[i].find_element_by_tag_name("a")
    url = a.get_attribute('href')
    list1_URL.append(url)
    print("已解析到URL%d个"%(i+1))
#####################解析主页URL#########################
list2_URL = []
list_name = []
# txt = open("video_URL.txt",'a',encoding='utf-8')
for i in range(url_count):
    vidio_URL,vidio_name = Analyzing(list1_URL[i])
    list2_URL.append(vidio_URL)
    list_name.append(vidio_name)
    # txt.write(vidio_URL+"\n")
    print("已解析到下载链接%d个"%(i+1))
# txt.close()
drive.close()
#####################下载视频############################
for i in range(url_count):
    path = list_name[i]
    url = list2_URL[i]
    download(path,url)
    print("已下载视频%d个"%(i+1))
#####################任务结束############################
