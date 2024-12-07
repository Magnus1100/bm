import requests
from bs4 import BeautifulSoup
import time
import csv
import random

# 设置请求头，模仿浏览器访问
headers = {'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3'}

# 所有语言选项
languages = ['en', 'zh-CN', 'ru', 'ja', 'de', 'fr', 'es', 'it', 'pl', 'ko']

# 用于存储已获取评论的ID，避免重复
seen_review_ids = set()


# 定义函数来爬取评论
def get_reviews(language, page_num):
    # 构建URL
    url = f'http://steamcommunity.com/app/2183900/reviews/?userreviewsoffset={10 * (page_num - 1)}&p={page_num}&numperpage=10&browsefilter=toprated&appid=433850&l={language}&filterLanguage=default&searchText=&forceanon=1'

    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"请求URL: {url} | 状态码: {response.status_code}")

        # 如果返回的状态码不是200，可能请求失败
        if response.status_code != 200:
            print(f"请求失败，状态码: {response.status_code}")
            return []

        html = response.text
    except requests.exceptions.RequestException as e:
        print(f"请求错误 ({language}, page {page_num}): {e}")
        return []

    soup = BeautifulSoup(html, 'html.parser')
    reviews = soup.find_all('div', {'class': 'apphub_Card'})

    # 如果没有找到评论，可能是页面结构变化，打印响应内容以便调试
    if not reviews:
        print(f"没有找到评论 ({language}, page {page_num})，查看页面内容：")
        print(html)

    return reviews


# 将评论内容写入CSV文件
def write_to_csv(review_data):
    with open('../reviews.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(review_data)


# 用于获取所有评论的函数
def fetch_all_reviews():
    # 在CSV中写入表头
    with open('../reviews.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Nickname', 'Title', 'Play Hours', 'Profile Link', 'Comment'])

    # 遍历所有语言
    for language in languages:
        print(f"正在爬取语言：{language}")
        page_num = 1
        review_counter = 0  # 评论计数器

        while True:
            reviews = get_reviews(language, page_num)

            # 如果没有评论，说明已到达最后一页，跳出循环
            if not reviews:
                print(f"没有更多评论了 ({language})。")
                break

            # 处理评论
            for review in reviews:
                try:
                    review_id = review.find('div', {'class': 'apphub_CardContentAuthorName'}).find('a').attrs['href']

                    # 检查评论是否已被爬取过
                    if review_id in seen_review_ids:
                        continue

                    # 将评论ID加入已爬取集合
                    seen_review_ids.add(review_id)

                    # 获取评论的相关信息
                    nick = review.find('div', {'class': 'apphub_CardContentAuthorName'}).text.strip()
                    title = review.find('div', {'class': 'title'}).text.strip()
                    hour = review.find('div', {'class': 'hours'}).text.split(' ')[0].strip()
                    link = review.find('div', {'class': 'apphub_CardContentAuthorName'}).find('a').attrs['href']
                    comment = review.find('div', {'class': 'apphub_CardTextContent'}).text.strip()

                    # 将数据写入CSV
                    review_data = [nick, title, hour, link, comment]
                    write_to_csv(review_data)

                    # 增加评论计数
                    review_counter += 1

                    # 输出当前语言和评论序号
                    print(f"语言: {language} | 当前评论: {review_counter}")

                except AttributeError as e:
                    # 如果某些评论的元素缺失，跳过
                    print(f"跳过评论 ({language}, page {page_num}): {e}")
                    continue

            # 等待1秒以避免频繁请求
            time.sleep(random.uniform(1, 3))  # 使用随机延时，避免被识别为爬虫

            # 继续处理下一页
            page_num += 1


# 调用函数开始爬取评论
fetch_all_reviews()
