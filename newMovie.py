import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


# def create_markdown_template(data_dict):
#     markdown_template = "# 电影信息\n\n"
#     for key, value in data_dict.items():
#         markdown_template += f"- **{key}**: {{{key}}}\n"
#     return markdown_template

class Comment:
    def __init__(self, name, star, date, location, vote, comment):
        self.name = name
        self.star = star
        self.date = date
        self.location = location
        self.vote = vote
        self.comment = comment

    def __str__(self):
        if self.star == '力荐':
            self.star = '5'
        elif self.star == '推荐':
            self.star = '4'
        elif self.star == '还行':
            self.star = '3'
        elif self.star == '较差':
            self.star = '2'
        else:
            self.star = '1'
        self.comment = self.comment.replace('\n', '')
        return f"评论人：{self.name}\n星级：{self.star}\n评论：{self.comment}\n日期：{self.date} 地点：{self.location}\n点赞：{self.vote}\n"


def fetch_movie_comment(base_href):
    service = Service(r"D:\chromedriver-win32-124\chromedriver-win32\chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    param = ['h', 'm', 'l']
    h_comment = []
    m_comment = []
    l_comment = []

    for p in param:
        href = base_href + f'comments?percent_type={p}&limit=20&status=P&sort=new_score'
        driver.get(href)
        time.sleep(3)  # 考虑使用显式等待
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        comment = soup.select('span[class="short"]')
        comment_info = soup.select('span[class="comment-info"]')
        comment_vote = soup.select('span[class="votes vote-count"]')

        for i in range(len(comment_info)):
            c = Comment(
                comment_info[i].select('a')[0].get_text(),
                comment_info[i].select('span')[1].get('title'),
                comment_info[i].select('span')[2].get_text().replace('\n', ''),
                comment_info[i].select('span')[3].get_text(),
                comment_vote[i].get_text(),
                comment[i].get_text()
            )
            if p == 'h':
                h_comment.append(c)
            elif p == 'm':
                m_comment.append(c)
            else:
                l_comment.append(c)

    driver.quit()
    return h_comment, m_comment, l_comment


def fetch_movie_info(href):
    # 创建WebDriver对象，打开一个浏览器窗口
    service = Service(r"D:\chromedriver-win32-124\chromedriver-win32\chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    driver.get(href)  # 使用Selenium的get方法打开链接
    time.sleep(3)  # 避免被网站限制访问，并且等待页面加载完成
    html = driver.page_source  # 获取网页源代码
    soup = BeautifulSoup(html, 'html.parser')
    driver.quit()

    name = ''
    value = []
    title = []
    director = []
    screenWriter = []
    actor = []
    types = []
    districts = ''
    language = ''
    showTime = []
    runtime = ''
    alias = ''
    imdb = ''
    rating = ''

    rating = soup.select('strong[class="ll rating_num"]')[0].get_text()
    name = soup.select('span[property="v:itemreviewed"]')[0].get_text()
    year = soup.select('span[class="year"]')[0].get_text()
    keys = soup.select('span[class="pl"]')
    directors = soup.select('a[rel="v:directedBy"]')
    screenWriters = soup.find('span', string='编剧').find_next_sibling().find_all('a')
    actors = soup.select('a[rel="v:starring"]')
    Types = soup.select('span[property="v:genre"]')
    districts = str(soup.find('span', string='制片国家/地区:').next_sibling)
    language = str(soup.find('span', string='语言:').next_sibling)
    showTimes = soup.select('span[property="v:initialReleaseDate"]')
    runtimes = soup.select('span[property="v:runtime"]')
    try:
        alias = str(soup.find('span', string='又名:').next_sibling)
    except:
        print('No alias')
    imdb = str(soup.find('span', string='IMDb:').next_sibling)

    title.append('片名')
    for i in range(10):
        title.append(keys[i].get_text())
    for d in directors:
        director.append(d.get_text())
    for s in screenWriters:
        screenWriter.append(s.get_text())
    for v in actors:
        actor.append(v.get_text())
    for t in Types:
        types.append(t.get_text())
    for s in showTimes:
        showTime.append(s.get_text())
    for r in runtimes:
        runtime = str(r.get_text())

    value.append(f'{name} {year}')
    value.append(','.join(director))
    value.append(','.join(screenWriter))
    value.append(','.join(actor))
    value.append(','.join(types))
    value.append(districts)
    value.append(language)
    value.append(','.join(showTime))
    value.append(runtime)
    value.append(alias)
    value.append(imdb)

    title.append("评分")
    value.append(rating)

    index = ['五星', '四星', '三星', '二星', '一星']
    for i in range(5):
        rating_per = soup.select('span[class="rating_per"]')[i].get_text()
        title.append(index[i])
        value.append(rating_per)

    # 电影简介
    summary = soup.select('span[property="v:summary"]')[0].get_text()
    title.append('简介')
    summary = summary.replace('\n', '').replace(' ', '')
    value.append(summary)

    h_comment, m_comment, l_comment = fetch_movie_comment(href)

    comments = [h_comment, m_comment, l_comment]

    info1 = dict(zip(title, value))

    return info1, comments


url = 'https://movie.douban.com/chart'
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/58.0.3029.110 Safari/537.3'
}
req = requests.get(url, headers=header)  # 使用requests获得网页HTML内容
content = req.text

soup = BeautifulSoup(content, 'html.parser')
movies = soup.select('a[class="nbg"]')
print(movies)

# 循环访问电影链接
with ThreadPoolExecutor(max_workers=10) as executor:
    # 提交所有的任务并收集Future对象
    futures = {executor.submit(fetch_movie_info, movie.get('href')) for movie in movies}

    for future in as_completed(futures):
        info, comments = future.result()
        movie_info_text = ""
        print(info)
        for key, value in info.items():
            if ":" in key or ":" in value:
                movie_info_text += f"{key}{value}\n"
            else:
                movie_info_text += f"{key}: {value}\n"
        # 获取当前日期
        now = time.strftime("%Y-%m-%d", time.localtime())
        # 保存到文件
        index = ['好评', '一般', '差评']
        os.makedirs(rf'排行榜\新片\{now}\{now}', exist_ok=True)
        with open(rf"排行榜\新片\{now}\{now}.txt", "a", encoding="utf-8") as f:
            f.write('Start\n')
            f.write(movie_info_text)
            for i in range(3):
                f.write(f"{index[i]}:\n")
                for comment in comments[i]:
                    f.write(comment.__str__())
            f.write('End\n')
            f.write("\n")
