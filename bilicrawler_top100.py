import bilicrawler_video
import pandas as pd
import time, os, sys, requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BlockingScheduler
#import chromedriver_autoinstaller
#from webdriver_manager.chrome import ChromeDriverManager

def get_top100(category='game'):
    # tid - 分区rid编码，默认值 4 为游戏分区
    url = f'https://www.bilibili.com/v/popular/rank/{category}/'

    # selenium
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')

    # options.binary_location = "/home/data/chromedriver.exe"
    # options.add_argument("--no-sandbox")
    # chromedriver_autoinstaller.install()

    driver = webdriver.Chrome(options=options)
    # driver = webdriver.Chrome(ChromeDriverManager().install())
    # driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.implicitly_wait(5)
    driver.get(url)
    time.sleep(10)

    rankitems = driver.find_elements(By.CLASS_NAME, "rank-item")

    top100 = {}
    for item in rankitems:
        top100[item.get_attribute("data-rank")] = item.get_attribute("data-id")
    return top100

def compute_score(output):
    bvid    = output[0]
    views   = int(output[1])
    danmu   = int(output[2])
    likes   = int(output[3])
    coins   = int(output[4])
    favs    = int(output[5])
    shares  = int(output[6])
    comments= int(output[7])
    dt      = datetime.fromisoformat(output[8])

    # testing this algorithm
    score = coins*0.4 + favs*0.3 + danmu*0.4 + comments*0.4 + views*0.25 + likes*0.4 + shares*0.6

    # if uploaded today, score gets a 1.5 factor boost
    print("正在抓取上传日期...")
    url = "https://www.bilibili.com/video/" + bvid
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    dt_upload = soup.find("meta", itemprop="uploadDate")["content"]
    dt_upload = datetime.fromisoformat(dt_upload)
    delta = dt - dt_upload
    if delta.days <= 1:
        score *= 1.5
    print("上传日期抓取完成")
    return score
    

"""writes out output from get_video_info() to csv file"""
def write_csv(output,outpath):
    if os.path.exists(outpath):
        # append new row to existing csv
        df = pd.read_csv(outpath)
        df.loc[len(df)] = output
    else:
        # if this is first time, make a new one
        df = pd.DataFrame(data=[output],columns=['bvid','播放量','弹幕量','点赞量','投币量','收藏量','分享量','评论量','抓取时间','flag','排名','分数'])
    
    df.to_csv(outpath,index=False,encoding="utf_8_sig")
    
    return 

def crawl_top100(category):
    outpath = "B站排行榜_"+category+".csv"
    top100 = get_top100(category)
    # print(top100)
    for i in range(1, 101):
        print("正在抓取第"+str(i)+"名...")
        aid = top100[str(i)]
        bvid, resp = bilicrawler_video.get_bvid(aid)
        print("视频信息抓取完成")
        output = bilicrawler_video.get_video_info(bvid, video_info=resp)
        output.append(i)
        score = compute_score(output)
        output.append(score)
        write_csv(output, outpath)
        time.sleep(5)
    print("B站排行榜抓取完毕!")

def yes_no(question):
    yes = set(['yes','y', 'ye', ''])
    no = set(['no','n'])
     
    while True:
        choice = input(question).lower()
        if choice in yes:
           return True
        elif choice in no:
           return False
        else:
           print("Please respond with 'yes' or 'no'")

if __name__ == "__main__":
    # deal with user input
    category = sys.argv[1]
    if not category.isalpha():
        raise ValueError("输入排行榜类别必须为英文字母!")
    interval = float(sys.argv[2]) # in hours
    start_dt = datetime.fromisoformat(sys.argv[3])
    end_dt = datetime.fromisoformat(sys.argv[4])

    # soft checks
    if interval > 24:
        if not yes_no("输入的间隔时间大于24小时,确定继续运行吗?(yes/no)"):
            raise ValueError("Undesired input interval")
    elif interval < 1:
        if not yes_no("输入的间隔时间小于1小时,确定继续运行吗?(yes/no)"):
            raise ValueError("Undesired input interval")
    # hard checks
    if start_dt < datetime.now():
        raise ValueError("Start time is in the past!")
    if end_dt < datetime.now():
        raise ValueError("End time is in the past!")
    if start_dt > end_dt:
        raise ValueError("Start time is after end time!")

    # schedule main to run
    scheduler = BlockingScheduler()
    job = scheduler.add_job(crawl_top100, args=[category],
                            trigger='interval', hours=interval,
                            start_date=start_dt, end_date=end_dt, jitter=60)
    print("APScheduler - current scheduled jobs:")
    print(scheduler.get_jobs())
    scheduler.start()
    scheduler.shutdown()
