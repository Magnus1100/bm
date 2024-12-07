import requests
from bs4 import BeautifulSoup
import csv
import re  # 导入正则表达式库
from datetime import datetime  # 导入 datetime 模块

max_page = 3
game_id = '2183900'  # 游戏本体
# 定义 CSV 文件名
csv_file = '../WarhammerSM2_steam_reviews.csv'

# 设置请求头
headers = {'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3'}
# 使用 requests.Session() 来提高性能，减少每次请求的开销
session = requests.Session()

# 获取所有语言评论
languages = ['schinese', 'english', 'french', 'german', 'japanese', 'koreana', 'spanish', 'portuguese', 'italian',
             'russian', 'turkish']

# 存储已抓取的评论URL以避免重复抓取
seen_review_urls = set()


def parse_date_from_comment(comment_text, lang='schinese'):
    """
    从评论中提取日期并删除，适应多语言格式。
    支持格式：
        中文： "发布于：2023 年 11 月 11 日" 或 "发布于：11 月 25 日"
        英文： "published on 25 Nov 2024" 等
    """
    # 定义日期的正则表达式
    if lang == 'schinese':
        # 中文格式: "发布于：2023 年 11 月 11 日" 或 "发布于：11 月 25 日"
        date_pattern = r'发布于：(\d{4} 年 \d{1,2} 月 \d{1,2} 日|\d{1,2} 月 \d{1,2} 日)'
    else:
        # 英文格式: "published on 25 Nov 2024" 或其他类似格式
        date_pattern = r'published on (\d{1,2} \w+ \d{4})'

    # 使用正则表达式从评论中提取日期
    date_match = re.search(date_pattern, comment_text)

    if date_match:
        date_str = date_match.group(1)  # 提取到的日期字符串

        # 如果是中文格式：2023 年 11 月 11 日
        if '年' in date_str:
            date_obj = datetime.strptime(date_str, '%Y 年 %m 月 %d 日')
            date = date_obj.strftime('%Y-%m-%d')

        # 如果是中文格式：11 月 25 日，默认设置为 2024 年
        elif '月' in date_str:
            date = f"2024-{date_str.replace('月', '-').replace('日', '').strip()}"
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            date = date_obj.strftime('%Y-%m-%d')

        # 如果是英文格式：25 Nov 2024
        else:
            date_obj = datetime.strptime(date_str, '%d %b %Y')
            date = date_obj.strftime('%Y-%m-%d')

        # 删除日期中的空格
        date = date.replace(' ', '')  # 去除所有空格

        # 从评论中去除日期部分
        comment_text = re.sub(date_pattern, '', comment_text).strip()

        return date, comment_text
    else:
        # 如果没有日期，返回默认值
        return 'N/A', comment_text


if __name__ == '__main__':
    # 打开 CSV 文件，准备写入
    with open(csv_file, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)

        # 写入标题行
        writer.writerow(['Nick', 'Title', 'Hour', 'Link', 'Date', 'Comment', 'Language'])

        # 遍历所有语言
        for lang in languages:
            # 遍历多个页面
            for i in range(1, max_page + 1):  # 每次请求不同的页面
                # URL 中改进分页逻辑，避免重复加载
                url = f'http://steamcommunity.com/app/{game_id}/homecontent/?userreviewsoffset={10 * (i - 1)}&p={i}&numperpage=10&browsefilter=toprated&appid={game_id}&appHubSubSection=10&l={lang}&filterLanguage=default&searchText=&forceanon=1'

                # 请求页面内容
                html = session.get(url, headers=headers).text
                soup = BeautifulSoup(html, 'html.parser')  # 使用 html.parser 解析

                reviews = soup.find_all('div', {'class': 'apphub_Card'})

                # 遍历每一条评论
                for review in reviews:
                    # 提取评论相关信息
                    nick = review.find('div', {'class': 'apphub_CardContentAuthorName'})
                    title = review.find('div', {'class': 'title'}).text.strip() if review.find('div', {
                        'class': 'title'}) else 'No Title'
                    link = nick.find('a').attrs['href'] if nick else 'No Link'

                    # 如果评论已经抓取过，跳过
                    if link in seen_review_urls:
                        continue
                    seen_review_urls.add(link)

                    # 提取时长信息
                    hour = 'N/A'  # 默认值，防止没有时长时报错
                    hours_div = review.find('div', {'class': 'hours'})
                    if hours_div:
                        hours_text = hours_div.text.strip()
                        match = re.search(r'(\d+\.?\d*)', hours_text)  # 提取数字部分
                        if match:
                            hour = match.group(1)

                    # 提取评论内容并分离日期
                    comment_text = review.find('div', {'class': 'apphub_CardTextContent'}).text.strip() if review.find(
                        'div',
                        {
                            'class': 'apphub_CardTextContent'}) else ''

                    # 使用 parse_date_from_comment 函数处理评论中的日期和内容
                    date, comment_text = parse_date_from_comment(comment_text, lang=lang)

                    # 处理评论的行分割
                    comment_lines = comment_text.split('\n')
                    comment_text = comment_lines[3].strip('\t') if len(comment_lines) > 3 else comment_text.strip()

                    # 将评论数据写入 CSV 文件，date 放在评论之前
                    writer.writerow(
                        [nick.text.strip() if nick else 'Unknown', title, hour, link, date, comment_text, lang])

                print(f"Page {i} processed for language {lang}.")
