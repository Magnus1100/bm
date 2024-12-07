from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import csv

# 设置 Chrome 浏览器的选项
chrome_options = Options()
chrome_options.add_argument("--headless")  # 启用无头模式（不显示浏览器界面）
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")  # 设置浏览器窗口大小，避免响应式页面问题

# 启动浏览器
driver = webdriver.Chrome(options=chrome_options)

# Steam 评论页面的 URL 模板
url_template = 'http://steamcommunity.com/app/2183900/reviews/?userreviewsoffset={offset}&p={page_num}&numperpage=10&browsefilter=toprated&appid=433850&l={language}&filterLanguage=default&searchText=&forceanon=1'

# 所有语言选项
languages = ['en', 'zh-CN', 'ru', 'ja', 'de', 'fr', 'es', 'it', 'pl', 'ko']

# 打开 CSV 文件，准备写入评论
csv_file = '../steam_reviews.csv'
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Nickname', 'Title', 'Play Hours', 'Profile Link', 'Comment', 'Language'])  # 写入表头

    # 遍历所有语言
    for language in languages:
        print(f"正在爬取语言：{language}")
        page_num = 1
        while True:
            # 构建请求的 URL
            url = url_template.format(offset=10 * (page_num - 1), page_num=page_num, language=language)
            driver.get(url)  # 访问页面
            time.sleep(3)  # 等待页面加载，确保评论已经加载

            # 获取评论元素
            reviews = driver.find_elements(By.CLASS_NAME, 'apphub_Card')

            if not reviews:  # 如果当前页面没有评论，说明已爬取完所有评论
                print(f"没有更多评论了 ({language}，页面 {page_num})")
                break

            # 遍历每一条评论
            for review in reviews:
                try:
                    # 获取评论的昵称、标题、时长、评论链接和评论内容
                    nick = review.find_element(By.CLASS_NAME, 'apphub_CardContentAuthorName').text.strip()
                    title = review.find_element(By.CLASS_NAME, 'title').text.strip()
                    hours = review.find_element(By.CLASS_NAME, 'hours').text.split(' ')[0].strip()
                    profile_link = review.find_element(By.CLASS_NAME, 'apphub_CardContentAuthorName').find_element(By.TAG_NAME, 'a').get_attribute('href')
                    comment = review.find_element(By.CLASS_NAME, 'apphub_CardTextContent').text.strip()

                    # 将评论写入 CSV 文件
                    writer.writerow([nick, title, hours, profile_link, comment, language])
                    print(f"语言: {language} | 评论: {nick} | 页面: {page_num}")

                except Exception as e:
                    print(f"抓取评论时出错: {e}")

            # 增加页面编号，抓取下一页
            page_num += 1

# 关闭浏览器
driver.quit()

