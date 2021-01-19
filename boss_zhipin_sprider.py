#encoding:utf-8
from bs4 import BeautifulSoup
import time
import ast
from selenium.webdriver import ChromeOptions
from selenium import webdriver
import random
import pymysql
import json
import requests


"如果pycharm 报 gbk 编码错误就把下方注释开启"
# import sys
# import io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030')

"数据存储位置--- mysql "
# con = pymysql.connect(host='localhost',user='root',password='song',database='boss_zp',port=3306)
# cur = con.cursor()

"selenium 使用代理 --- 根据代理官方文档来，最后得到的是代理 "
'opt .add_argument("–proxy-server=http://ip:端口")# 一定要注意，等号两边不能有空格'

# apis = 'https://tps.kdlapi.com/api/gettps/?orderid=951099579655470&num=1&format=json&sep=1' # 隧道IP代理的API链接
# res = requests.get(apis)
# jsdata = json.loads(res.text)['data']['proxy_list'][0]
# option = ChromeOptions()

"网页懒加载模式--在爬取职位详情页的 会加载地图部分"
# capa = DesiredCapabilities.CHROME
# capa["pageLoadStrategy"] = "none"  # 懒加载模式，不等待页面加载完毕
# option.add_argument('--host-resolver-rules=MAP passport.zhipin.com 127.0.0.1')



"爬取网页，boss直聘有两个可以爬 一个是 www.zhipin.com 和 m.zhipin.com"
"这两个反爬机制都是一样的"

class login_zhipin():
    """
    登录直聘

    """
    def __init__(self):
        self.login_url = "https://login.zhipin.com/?ka=header-login"

    def logins(self):

        global driver
        option = ChromeOptions()
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        driver = webdriver.Chrome(r"chromedriver/chromedriver.exe", options=option)

        driver.maximize_window()
        driver.get(self.login_url)
        time.sleep(5)
        driver.find_element_by_xpath('//*[@id="wrap"]/div[2]/div[1]/div[2]/div[2]').click()
        driver.implicitly_wait(10)
        while True:
            try:
                index = driver.find_element_by_xpath('//*[@id="header"]/div[1]/div[2]/ul/li[1]/a').text
                if str(index) == "首页":
                    break
                else:
                    pass
            except:
                pass

class get_list_info():

    """获取搜索得到结果页面信息"""

    def __init__(self,url):

        self.url= url
        pass
    def get_gw_content(self):

        global driver

        driver.get(self.url)
        time.sleep(4)
        html = driver.page_source
        html = BeautifulSoup(html, 'lxml')


        # 下方是获取信息的 赛选方式，我这里默认只获取岗位的关键字和这内容URL  根据自己所需要获取
        # 自我测试 爬取 5-6小时跳一次验证码

        zi_info = html.find_all('div', class_="job-primary")
        for zi in zi_info:
            span_a = zi.find_all('span', class_="job-name")[0].find('a')['href']
            url = 'https://www.zhipin.com' + str(span_a)
            tag_text = str(
                zi.find_all('div', class_="info-append clearfix")[0].find('div', class_="tags").text).replace('\n', ' ')


            infos = [url, tag_text]


            # 下方是写入数据方式：

            with open('booss_infos.txt', 'a+', encoding='utf-8') as f:
                f.write(str(infos) + '\n')
                f.close()
            print(self.url)
            print(infos)


        try:
            #自循环判断，这类的所有页面，并自动爬取
            nxet_page = 'https://www.zhipin.com' + str(html.find_all('a', ka="page-next")[0]['href'])
            if nxet_page != "":
                number = random.randint(5,18)
                time.sleep(number)
                get_list_info(nxet_page).get_gw_content()
            else:
                pass

        except:
            pass

class get_content():

    def __init__(self, url, gw_keytext):
        self.url = url
        self.gw_keytext = gw_keytext

    "下方是写入数据的方式，提前创建好 表 "
    # def c_mysql(self, brand_name, brand_address, zpzw, gwzz, gw_key):
    #     sql_insert_data = """
    #             insert into boss_excel(
    #                     brand_name,
    #                     brand_address,
    #                     zpzw,
    #                     gwzz,
    #                     gw_key
    #
    #             ) value (
    #
    #                     '%s',
    #                     '%s',
    #                     '%s',
    #                     '%s',
    #                     '%s'
    #
    #             );
    #
    #     """ % (brand_name, brand_address, zpzw, gwzz, gw_key)
    #     print(brand_name, "写入了数据中")
    #     cur.execute(sql_insert_data)
    #     con.commit()

    def zp_info(self):

        driver.get(self.url)
        time.sleep(1)
        html = driver.page_source

        if "您访问的页面不存在" in str(html):
            pass

        else:

            # 点击进行验证
            while True:
                try:
                    index_test = driver.find_element_by_xpath('//*[@id="header"]/div[1]/div[2]/ul/li[1]/a').text
                    if "首页" == index_test:
                        break
                    else:
                        pass
                except:
                    pass

            try:
                if "点击进行验证" not in str(html):

                    contnet = BeautifulSoup(html, 'lxml')

                    gw_name = str(contnet.find_all('div', class_="name")[0].find('h1').text).replace('\n', '').strip()

                    try:
                        brand_name = str(contnet.find_all('a', ka="job-detail-company_custompage")[0].text).replace(
                            '\n',
                            '').strip()
                    except:
                        brand_name = "网页无数据"
                    try:
                        brand_address = str(contnet.find_all('div', class_="location-address")[0].text).replace('\n',
                                                                                                                '').strip()
                    except:
                        brand_address = "网页无数据"
                    try:
                        gw_yq = str(contnet.find_all('div', class_="text")[0].text).strip()
                    except:
                        gw_yq = "网页无数据"

                    gw_key = self.gw_keytext


                    # 写入数据库
                    # self.c_mysql(brand_name, brand_address, gw_name, gw_yq, gw_key)

                elif "点击进行验证" in str(html):

                    while True:
                        try:
                            index_test = driver.find_element_by_xpath('//*[@id="header"]/div[1]/div[2]/ul/li[1]/a').text
                            if "首页" == index_test:
                                break
                            else:
                                pass
                        except:
                            pass

                    get_content(self.url, self.gw_keytext).zp_info()

            except:
                input("错误 请手动验证：")
                time.sleep(2)
                get_content(self.url, self.gw_keytext).zp_info()

#类对象说明

"login_zhipin()-------  登录操作"
"get_list_info() -------  获取关键搜索出来的页面，或者是分类出来的页面，以及翻页所有内容"
"get_content() -------  某岗位所有的信息，公司名称，地址，招聘要求，招聘岗位名称"



# 提示： 最好电话号码扫码登录，一个电话号可以抓取1-2天数据，验证需要手工验证。市面上暂无打码平台，但是我可以推荐：
# 打码平台1 ： http://www.ttshitu.com/test.html?spm=null
# 打码平台2 ：http://www.damatu1.com/codelist.asp
# 打码平台3：https://www.jsdati.com
# 打码平台4 http://www.chaorendama.com

"""
接码平台

01        神话 http://115.28.184.182:8000

02        短租 http://121.41.61.159:8888/help.jsp

03        海码 http://www.haima668.com:8008/download.html

04        悠码 http://www.6tudou.com:9000/download.html

05        云享 http://www.yunxiang001.com

06        解忧 http://www.jieyouma.com

07        收码 http://www.shou-ma.com

08        云速 http://www.yunsu01.com

09        讯码 http://www.xunma.net

10        速码 http://www.eobzz.com

11        60码 http://www.60ma.net

12        易码 http://www.51ym.me

13        商码 http://ma.d4z.cn

14        淘码 http://w6888.cn

15        集码 www.jima99.com

16        极速 http://jsjmpt.com

17        一码 http://yima998.com

18        云码 http://www.yzm7.com

19        七年 http://47.52.114.154

20        爱信 http://www.ixinsms.com

21        米粒 http://www.mili02.com

22        万码 http://www.yzm8888.cn

23        快码 http://www.51kmf.com

24        蚂蚁 http://www.66yzm.com

25        多米 http://www.du20.top

26        赞码 http://www.mg12588.com

27        星光 http://www.20982098.com

28        风火云 http://www.codedw.com

29        千万卡 http://www.yika66.com

30        科技虫 http://abc.aiputime.com

31        百万码 http://www.baiwanma.com

32        吸码皇 http://www.ximahuang.com

33        尚一品 http://www.shangyipin.net

34        芒果云 http://www.mangopt.com:9000/soft.html

35        柚子码 http://www.yzm9.com/homepage.html

36        快云平台 http://www.ky319.com:8000

37        麦子平台 http://www.maiziyzm.com

38        蜜蜂平台 http://mf-yzm.cn:9000

39        国际共享 http://www.gx-gj.com

40        星空语音 http://www.xk-yzm.com

41        thewolf http://thewolf.yyyzmpt.com/member.php?

打码平台：

1        联众 https://www.jsdati.com

2        极验 http://jiyan.c2567.com

3        若快 http://www.ruokuai.com

4        超人 http://www.chaorendama.com
"""









