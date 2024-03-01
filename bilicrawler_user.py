import requests
from datetime import datetime
import time
import wbi_sig
import json

url = 'https://api.bilibili.com/x/web-interface/archive/stat?aid=10313792'
header = {'User-Agent':'Mozilla/5.0'}
jscontent = requests.get(url, headers=header, verify=False).content.decode()
jsDict = json.loads(jscontent)


### 尝试从B站api请求用户信息
header = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

uuid = str(29157642)
print("uuid: "+uuid)

# 请求基本用户信息 - 每次都成功，没问题
url_user = "https://api.bilibili.com/x/relation/stat?vmid={}&jsonp=jsonp".format(uuid)

user = requests.get(url_user, headers=header).json()['data']
# print(user)

# 提取用户关注与被关注数量
following = str(user['following'])
follower = str(user['follower'])

print("following: "+following)
print("follower: "+follower)

# 请求详细用户信息 - 有问题

# 尝试旧api，可以成功抓取一次，但之后开始返回{'code': -799, 'message': '请求过于频繁，请稍后再试', 'ttl': 1}，等几个小时又能抓取一次，之后同样被拒
url_userinfo = "https://api.bilibili.com/x/space/acc/info?mid=29157641"
tryuserinfo = requests.get(url_userinfo, headers=header).json()

# 新api，但是需要wbi签名 w_rid 怎么获得？
# {'code': -403, 'message': '访问权限不足', 'ttl': 1}
currenttime = datetime.now()
wts = time.mktime(datetime.timetuple(currenttime))

url_userinfo = "https://api.bilibili.com/x/space/wbi/acc/info?mid={uuid}&jsonp=jsonp&wts={wts}&w_rid={w_rid}".format(
                    uuid = uuid, wts = wts, w_rid = w_rid)

cookies = dict(cookies_are='SESSDATA=xxx')

getuserinfo = requests.get(url_userinfo, cookies=cookies, headers=header).json()
try:
    userinfo = getuserinfo['data']
except:
    print(getuserinfo)
# print(userinfo)


# 一些网上相关的代码
img_key, sub_key = wbi_sig.getWbiKeys()

signed_params = wbi_sig.encWbi(
    params={
        'foo': '114',
        'bar': '514',
        'baz': 1919810
    },
    img_key=img_key,
    sub_key=sub_key
)
query = wbi_sig.urllib.parse.urlencode(signed_params)
print(signed_params)
print(query)
# url_userinfo = "https://api.bilibili.com/x/space/wbi/acc/info?mid=2&wts=1689328252&w_rid=9b6d68d7699c8d9d3c8d3c24b4266892"


# 提取用户名、性别、等级、生日
name = str(userinfo['name'])
sex = str(userinfo['sex'])
level = str(userinfo['level'])
birthday = str(userinfo['birthday'])

print("name: "+name)
print("sex: "+sex)
print("level: "+level)
print("birthday: "+birthday)

# url_test = "http://api.bilibili.cn/userinfo/user={}".format(name)

# testdata = requests.get(url_test, headers=header).json()['data']


### 试着用一下别人写好的爬虫
from bilibili_api import Credential, user, sync

# credential信息需要自己在浏览器工具里找
credential = Credential(sessdata="72bdd9f9%2C1704765982%2Cef52a%2A72103j061JuzEhe0Q9VU65xG8V5xb7Usn8Nk0IviB2hSfsC5rS6dBnDwuVT_2m-r1D-6K0mwAARQA", 
                        bili_jct="f9bc3017c58c6dce861a7b9ae33faa20", 
                        buvid3="70FFC046-BB14-CB25-4522-041F9227468B42315infoc")

credential = Credential(buvid3="3A943933-D3AD-099B-9B30-BAFC9B3F8E8101405infoc")

targetuser = user.User(uid=int(uuid), credential=credential)

# 第一次运行的时候没加sleep，又被请求过于频繁封住了
# ResponseCodeException: 接口返回错误代码：-799，信息：请求过于频繁，请稍后再试。
user_info = await targetuser.get_user_info()
await asyncio.sleep(5)
relation_info = await targetuser.get_relation_info()
await asyncio.sleep(5)
up_stat = await targetuser.get_up_stat()


