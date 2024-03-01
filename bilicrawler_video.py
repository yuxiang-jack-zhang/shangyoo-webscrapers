"""
B站视频爬虫,每小时抓取指定视频的基本信息(评论量,播放量,点赞量,投币量,弹幕量,收藏量)

Input:
    [s] upid of video
    [int] time interval in minutes (default 60)
    [string] output file name (default "B站爬虫结果.csv")
    
Output (per time interval):
    [csv file] output file

从终端运行示例：
python .\bilicrawler_video.py BV19k4y1P7PM 5 【新月同行】我的狮傩哪有这么可爱

"""

import pandas as pd
import json,requests,re,time,random
from bs4 import BeautifulSoup
from selenium import webdriver
import sys,os
from datetime import datetime

def bv2av(x):
    """BVID转AVID(也叫AID)的算法"""
    table = 'fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
    tr = {}
    for i in range(58):
        tr[table[i]] = i
    s = [11, 10, 3, 8, 4, 6]
    xor = 177451812
    add = 8728348608
    r = 0
    for i in range(6):
        r += tr[x[s[i]]] * 58 ** i
    return (r - add) ^ xor

def av2bv(av):
    bvid=''
    
    table = 'fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
    tr = {}
    for i in range(58):
        tr[table[i]] = i
    s = [11, 10, 3, 8, 4, 6, 2, 9, 5, 7]
    xor = 177451812
    add = 100618342136696320
    ret = av
    av = int(av)
    # 将AV号传入结果进行异或计算并加上 100618342136696320
    av = (av ^ xor) + add
    # 将BV号的格式（BV + 10个字符） 转化成列表方便后面的操作
    r = list('BV          ')
    # 将传入的数字对照字典进行转化
    for i in range(10):
        r[s[i]] = table[av // 58 ** i % 58]
    for i in range(len(r)):
        bvid += r[i]
    return bvid

def check_algorithm(size):
    size = int(size)

    total = 0
    correct = 0

    seed = list("307049856")
    for i in range(10):
        for j in range(10):
            for k in range(10):
                # for l in range(10):
                seed[-1] = str(i)
                seed[-2] = str(j)
                seed[-3] = str(k)
                # seed[-4] = str(l)
                aid = "".join(seed)
                url = f'https://api.bilibili.com/x/web-interface/archive/stat?aid={aid}'
                dic_header = {'User-Agent':'Mozilla/5.0'}
                resp = requests.get(url, headers=dic_header).json()['data']
                time.sleep(3+random.random())
                if resp:
                    total += 1
                    bvid_derive = av2bv(int(aid))
                    bvid_check = resp['bvid']
                    if bvid_derive == bvid_check:
                        correct += 1
                    else:
                        print(bvid_derive + "  |  " + bvid_check)
                else:
                    pass
    
    rate = correct/total
    print("Finished checking algorithm, success rate = " + str(rate))
    return

def get_aid(bvid):
    """
    converts [s]bvid to [s]aid
    outputs: [s]bvid, [response]resp if api access succeeded
    """
    if 'BV' in bvid:
        try:
            url = f'https://api.bilibili.com/x/web-interface/archive/stat?bvid={bvid}'
            dic_header = {'User-Agent':'Mozilla/5.0'}
            resp = requests.get(url, headers=dic_header).json()['data']
            return resp['aid'], resp
        except:
            return bv2av(bvid), None
    else:
        return bvid, None

def get_bvid(aid):
    """
    converts [s]aid to [s]bvid

    outputs: [s]aid, [None/response]resp if api access succeeded
    """
    if 'BV' not in aid:
        try:
            url = f'https://api.bilibili.com/x/web-interface/archive/stat?aid={aid}'
            dic_header = {'User-Agent':'Mozilla/5.0'}
            resp = requests.get(url, headers=dic_header).json()['data']
            return resp['bvid'], resp
        except:
            return av2bv(aid), None
    else:
        return aid, None

def create_proxy_ipzan(num=1):
    params = {
        "no": "20230720864528885447",
        "secret": "g9v8bji55rns4dg",
        "num": num,
        #"mode":
        "minute":1,
        "pool":"quality",
    }
    
    response = requests.get(
        url = "https://service.ipzan.com/core-extract?num=%s&no=%s&minute=%s&format=json&area=all&repeat=1&protocol=1&pool=%s&mode=auth&secret=%s"
                % (params["num"],params["no"],params["minute"],params["pool"],params["secret"]),
        #params=params,
        headers={
            "Content-Type": "text/plain; charset=utf-8",
        }
    )
    print('Response HTTP Status Code: {status_code}'.format(
    status_code=response.status_code))
    print('Response HTTP Response Body: {content}'.format(
    content=response.content))

    respJson = json.loads(response.content)
    if respJson['status'] != 200:
        return False
    if respJson['code'] != 0:
        print("message %s" % respJson['message'])
        return False
    
    ret_data_list = respJson['data']['list']

    if len(ret_data_list) <= 0:
        return False

    for ret_data in ret_data_list:
        #ret_data = ret_data_list[0]

        proxyMeta = "http://%(account)s:%(password)s@%(host)s:%(port)s" % {
                "account":ret_data['account'],
                "password":ret_data['password'],
                "host": ret_data['ip'],
                "port": ret_data['port'],
        }

        proxyUrl = "http://%(host)s:%(port)s" % {
                "host": ret_data['ip'],
                "port": ret_data['port'],
        }

        ip_info = {
                    "is_new":True,
                    "use_num":0,
                    "http": proxyMeta,
                    "https": proxyMeta,
                    "proxyUrl":proxyUrl,
                    "timestamp":ret_data["expired"]
        }

        #IpProxy.ip_info_list.append(ip_info)
        # IpProxy.ip_info_list.insert(0,ip_info)
        print(ip_info)

        # proxies = {
        # 'http': 'http://zproxy.lum-superproxy.io:22225',
        # 'https': 'http://zproxy.lum-superproxy.io:22225',
        # }

        # response = requests.get(url, proxies=proxies, auth=('USERNAME', 'PASSWORD'))
    return False
 
def proxyDemo():
    # 要访问的目标页面
    targetUrl = "http://httpbin.org/ip"
    # 要访问的目标HTTPS页面
    # targetUrl = "https://httpbin.org/ip"
    # 代理服务器
    proxyHost = "t.16yun.cn"
    proxyPort = "31111"
    # 代理隧道验证信息
    proxyUser = "16ZKBRLB"
    proxyPass = "234076"
    proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
    "host" : proxyHost,
    "port" : proxyPort,
    "user" : proxyUser,
    "pass" : proxyPass,
    }
    # 设置 http和https访问都是用HTTP代理
    proxies = {
    "http" : proxyMeta,
    "https" : proxyMeta,
    }
    # 设置IP切换头
    tunnel = random.randint(1,10000)
    headers = {"Proxy-Tunnel": str(tunnel)}
    resp = requests.get(targetUrl, proxies=proxies, headers=headers)
    print(resp.status_code)
    print(resp.text)
    return


"""main scraper function"""
def get_video_info(bvid, video_info=None):
    # if video info is already provided, simply extract and return
    if video_info:
        views,danmaku,favorites,coins,shares,likes,comments = video_info['view'],video_info['danmaku'],video_info['favorite'],video_info['coin'],video_info['share'],video_info['like'],video_info['reply']
        flag = 'api'
        timenow = datetime.now().isoformat(" ")
        output = [bvid, views, danmaku, likes, coins, favorites, shares, comments, timenow, flag]
        return output
    
    # otherwise, let's get to web scraping
    try:
        # default to use the faster scraping method by requesting from api
        base_info_url = f'https://api.bilibili.com/x/web-interface/archive/stat?bvid={bvid}'

        # proxy = create_proxy_ipzan()

        dic_header = {'User-Agent':'Mozilla/5.0'}
        base_info = requests.get(base_info_url, headers=dic_header).json()['data']

        views,danmaku,favorites,coins,shares,likes,comments = base_info['view'],base_info['danmaku'],base_info['favorite'],base_info['coin'],base_info['share'],base_info['like'],base_info['reply']
        flag = 'api'
    except:
        # if api doesn't work, flag and use request from html
        print('error when scraping from api.bilibili! scraping from html instead...')
        flag = 'html'
        url = "https://www.bilibili.com/video/" + bvid
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # 播放量,点赞量,投币量,弹幕量,收藏量
        meta_description = soup.find("meta", itemprop="description")["content"]
        numbers = re.findall(
            r'[\s\S]*?视频播放量 (\d+)、弹幕量 (\d+)、点赞数 (\d+)、投硬币枚数 (\d+)、收藏人数 (\d+)、转发人数 (\d+)',
            meta_description)
        views, danmaku, likes, coins, favorites, shares = [int(n) for n in numbers[0]]

        # 提取评论量
        ##request can't get the comments section for some reason, kludge around with selenium webdriver, improve later
        driver = webdriver.Chrome()
        driver.get(url)
        soup2 = BeautifulSoup(driver.page_source, 'html.parser')

        total_reply = soup2.find(class_="total-reply").string
        comments = int(total_reply)

        driver.quit()

    # compile results
    timenow = str(datetime.now().isoformat(" "))
    output = [bvid, views, danmaku, likes, coins, favorites, shares, comments, timenow, flag]
    
    return output

"""writes out output from get_video_info() to csv file"""
def write_csv(output,outpath):
    if os.path.exists(outpath):
        # append new row to existing csv
        df = pd.read_csv(outpath)
        df.loc[len(df)] = output
    else:
        # if this is first time, make a new one
        df = pd.DataFrame(data=[output],columns=['bvid','播放量','弹幕量','点赞量','投币量','收藏量','分享量','评论量','抓取时间','flag'])
    
    df.to_csv(outpath,index=False,encoding="utf_8_sig")
    
    return 

if __name__ == "__main__":
    # user input
    bvid = sys.argv[1] # bvid = "BV19k4y1P7PM"

    try:
        interval = int(sys.argv[2]) # enable users to choose which to specify
    except:
        interval = 60 # minutes
    
    try:
        outname = sys.argv[3]+".csv"
    except:
        outname = "B站爬虫结果.csv"
    # outpath = os.getcwd()+"\\"+outname

    i = 1
    print("开始抓取B站视频bvid="+bvid+"...")
    while True:
        print("...开始第"+str(i)+"次抓取..."+str(datetime.now()))
        output = get_video_info(bvid)

        print("...抓取成功，第"+str(i)+"次导出数据..."+str(datetime.now()))
        write_csv(output,outname)
        i += 1

        print("...开始为期"+str(interval)+"分钟等待..."+str(datetime.now()))
        time.sleep(interval*60)
