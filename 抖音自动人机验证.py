from selenium import webdriver
import time
import requests
import cv2
import os
import pyautogui as pg

you_url = 'https://www.douyin.com/user/MS4wLjABAAAAGA9bHrExvrQmowuVfRZxjG4s07M7EUjf1PlaHRHqdls' #作者主页
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])

#获取验证图片url
def get_img():
    data = drive.find_element_by_class_name("captcha_verify_img--wrapper").find_elements_by_tag_name("img")
    url_a = data[0].get_attribute("src")
    url_b = data[1].get_attribute("src")
    return url_a,url_b

#下载验证图片
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
    img = cv2.GaussianBlur(img, (3, 3), 0)
    return cv2.Canny(img, 50, 150)

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
    data += (data-135.5)*0.3  #偏移参数0.3 (0.1~0.5)
    data = round(data,1)      #保留一位小数
    print(data)
    return data

#获取滑块位置
def location_hk():
    rect = drive.find_element_by_class_name("sc-kkGfuU").rect  #滑块相对浏览器位置
    position = drive.get_window_position()           #浏览器位置
    x = position['x']+rect['x']+rect['width']/2
    y = position['y']+rect['y']+rect['height']/2+120 #偏移量120
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

#循环测试
while True:
    drive = webdriver.Chrome(options=options)
    drive.get(you_url)
    while True:
        try:
            drive.find_element_by_class_name("secsdk-captcha-drag-icon")
            url_a,url_b = get_img()
            download("a.jpeg",url_a)
            download("b.png",url_b)
            data = distance()
            x,y = location_hk()
            os.remove("a.jpeg")
            os.remove("b.png")
            move_hk(x,y,data)
            break
        except:
            time.sleep(0.5)
    time.sleep(3)
    print("开始下一次测试")
