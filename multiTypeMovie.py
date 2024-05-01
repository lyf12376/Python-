import json

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

url = 'https://movie.douban.com/chart'
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/58.0.3029.110 Safari/537.3'
}


def fetch_chart_info(url, type_name):
    url = 'https://movie.douban.com' + url
    service = Service(r"D:\chromedriver-win32-124\chromedriver-win32\chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/58.0.3029.110 Safari/537.3'
    }
    driver.get(url)
    time.sleep(3)
    # 爬取api接口
    api = driver.execute_script('return JSON.stringify(window.performance.getEntries())')
    # 将一个字符串转化为Json对象列表
    api = json.loads(api)
    name = []
    for i in api:
        name.append(i.get('name'))

    for i in name:
        if 'https://movie.douban.com/j/chart/top_list?' in i:
            response = requests.get(i, headers=headers)  # 发送GET请求
            if response.status_code == 200:  # 确保响应状态码是200
                content = response.text
                obj = json.loads(content)  # 解析JSON

                # 构建目录名并确保不包含非法字符
                dir_name = type_name.replace('/', '_')
                # 确保保存json文件的目录存在
                os.makedirs(rf'排行榜\{dir_name}', exist_ok=True)  # 创建目录，如果目录已存在则忽略

                # 定义文件路径
                now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                file_path = rf'排行榜\{dir_name}\{now}.json'  # 假设每个type_name目录下只有一个叫做data.json的文件

                # 将JSON对象保存到文件
                with open(file_path, 'w', encoding='utf-8') as fp:
                    json.dump(obj, fp, ensure_ascii=False, indent=4)
                print(f"数据已保存到 {file_path}")
            else:
                print(f"请求失败，状态码：{response.status_code}")


req = requests.get(url, headers=header)  # 使用requests获得网页HTML内容
content = req.text

soup = BeautifulSoup(content, 'html.parser')
movieTypes = soup.find('div', class_='types').find_all('a')
type_name = []
types = []
for t in movieTypes:
    type_name.append(t.get_text())
    types.append(t.get('href'))
    # print(t.get('href'))

# for t in range(len(types)):
#     fetch_chart_info(types[t], type_name[t])

# 多线程获取电影信息
with ThreadPoolExecutor(max_workers=10) as executor:
    # 提交所有的任务并收集Future对象
    futures = {executor.submit(fetch_chart_info, types[t], type_name[t]) for t in range(len(types))}
