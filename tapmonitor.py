import time, os, sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
import pandas as pd

### 抓取评论文字 https://wenku.baidu.com/view/040a483fab114431b90d6c85ec3a87c240288a7d.html?_wkts_=1689565805909&bdQuery=taptap%E7%88%AC%E8%99%AB

def str2value(str):
    if type(str) == float or type(str) == int:
        return str
    
    # 移除非数量相关字符
    for ch in str:
        if not (ch.isdigit() or ch == "." or ch == "%" or ch == "万"):
            str = str.replace(ch,"")

    idxWAN = str.find('万')
    idxPCT = str.find('%')
    if idxWAN != -1:
        value = float(str[:idxWAN])*1e4
    elif idxPCT != -1:
        value = float(str[:idxPCT])*1e-2
    else:
        value = float(str)
    return value

def get_game_info(app_id):
    app_id = str(app_id)
    url = 'https://www.taptap.cn/app/'+app_id+'/review'

    # selenium
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    driver.get(url)
    time.sleep(10)

    # extract data
    name = driver.find_element(By.XPATH, '//*[@id="191385"]/div[2]/div/div/div[2]/header/div[2]/div[1]/div/h1/span').text

    downloads = driver.find_element(By.XPATH, '//*[@id="191385"]/div[2]/div/div/main/div[1]/div[1]/div[1]/div[3]/span[1]/span[2]').text
    downloads = str2value(downloads)
    time.sleep(5)

    follows = driver.find_element(By.XPATH, '//*[@id="191385"]/div[2]/div/div/main/div[1]/div[1]/div[1]/div[3]/span[2]/span[2]').text
    follows = str2value(follows)
    time.sleep(5)

    rating = driver.find_element(By.XPATH, '//*[@id="191385"]/div[2]/div/div/main/div[1]/div[1]/div[2]/div').text
    rating = str2value(rating)
    time.sleep(5)

    comments = driver.find_element(By.XPATH, '//*[@id="191385"]/div[2]/div/div/main/div[2]/div/div[2]/div/div[1]/div/div[2]/a/div/a/span').text
    comments = str2value(comments)
    time.sleep(5)

    fivestar = driver.find_element(By.XPATH, '//*[@id="191385"]/div[2]/div/div/main/div[2]/div/div[3]/div/div[1]/div/div[1]/div/div[2]/div[1]/div[2]/div').get_attribute('style')
    time.sleep(5)
    fourstar = driver.find_element(By.XPATH, '//*[@id="191385"]/div[2]/div/div/main/div[2]/div/div[3]/div/div[1]/div/div[1]/div/div[2]/div[2]/div[2]/div').get_attribute('style')
    time.sleep(5)
    threestar = driver.find_element(By.XPATH, '//*[@id="191385"]/div[2]/div/div/main/div[2]/div/div[3]/div/div[1]/div/div[1]/div/div[2]/div[3]/div[2]/div').get_attribute('style')
    time.sleep(5)
    twostar = driver.find_element(By.XPATH, '//*[@id="191385"]/div[2]/div/div/main/div[2]/div/div[3]/div/div[1]/div/div[1]/div/div[2]/div[4]/div[2]/div').get_attribute('style')
    time.sleep(5)
    onestar = driver.find_element(By.XPATH, '//*[@id="191385"]/div[2]/div/div/main/div[2]/div/div[3]/div/div[1]/div/div[1]/div/div[2]/div[5]/div[2]/div').get_attribute('style')
    time.sleep(5)

    fivestar_pct = str2value(fivestar)
    fourstar_pct = str2value(fourstar)
    threestar_pct = str2value(threestar)
    twostar_pct = str2value(twostar)
    onestar_pct = str2value(onestar)

    # round(comments * fivestar_pct) + round(comments * fourstar_pct) + round(comments * threestar_pct) + round(comments * twostar_pct) + round(comments * onestar_pct)

    # 论坛 is at a different url
    url_topic = 'https://www.taptap.cn/app/'+app_id+'/topic'
    driver.implicitly_wait(5)
    driver.get(url_topic)
    time.sleep(10)

    follows_topic = driver.find_element(By.XPATH, '//*[@id="tap"]/div[1]/main/div[2]/div/div[1]/div[1]/div[2]/div/div[1]/p/span[1]').text
    follows_topic = str2value(follows_topic)
    time.sleep(5)

    posts_topic = driver.find_element(By.XPATH, '//*[@id="tap"]/div[1]/main/div[2]/div/div[1]/div[1]/div[2]/div/div[1]/p/span[3]').text
    posts_topic = str2value(posts_topic)

    # compile results
    timenow = datetime.now().isoformat(" ")
    output = [name, downloads, follows, rating, comments, fivestar_pct, fourstar_pct, threestar_pct, twostar_pct, onestar_pct, follows_topic, posts_topic, timenow]
    driver.quit()

    return output

"""writes out output from get_video_info() to csv file"""
def write_csv(output,outpath):
    if os.path.exists(outpath):
        # append new row to existing csv
        df = pd.read_csv(outpath)
        df.loc[len(df)] = output
    else:
        # if this is first time, make a new one
        df = pd.DataFrame(data=[output],columns=['游戏名','下载量','关注量','评分','评论量','五星评论占比','四星评论占比','三星评论占比','二星评论占比','一星评论占比','论坛关注量','论坛帖子量','数据获取时间'])
    
    df.to_csv(outpath,index=False,encoding="utf_8_sig")
    
    return 

if __name__ == "__main__":
    # user input
    app_id = sys.argv[1] # app_id = "191385" 逆水寒
    try:
        interval = int(sys.argv[2]) # later enable users to choose which to specify
        outname = sys.argv[3]+".csv"
    except:
        interval = 60 # minutes
        outname = "TapTap爬虫结果.csv"
    outpath = os.getcwd()+"\\"+outname

    i = 1
    print("开始抓取TapTap游戏app_id="+app_id+"...")
    while True:
        print("...开始第"+str(i)+"次抓取..."+str(datetime.now()))
        output = get_game_info(app_id)

        print("...抓取成功，第"+str(i)+"次导出数据..."+str(datetime.now()))
        write_csv(output,outpath)
        i += 1

        print("...开始为期"+str(interval)+"分钟等待..."+str(datetime.now()))
        time.sleep(interval*60)
        print("等待完成")