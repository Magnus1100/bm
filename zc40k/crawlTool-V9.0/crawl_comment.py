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

# Steam 评论页面的 URL
url = 'https://steamcommunity.com/app/2183900/reviews/?browsefilter=toprated&numperpage=10&appid=433850&l=en&forceanon=1&filterLanguage=all'

# 打开页面
driver.get(url)

# 等待页面加载
time.sleep(3)

# 用于存储已获取评论的ID，避免重复
seen_review_ids = set()

# 打开 CSV 文件，准备写入评论
csv_file = 'steam_reviews.csv'
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Nickname', 'Title', 'Play Hours', 'Profile Link', 'Comment', 'Language'])  # 写入表头

    # 设置滚动高度
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # 获取当前页面的所有评论元素
        reviews = driver.find_elements(By.CLASS_NAME, 'apphub_Card')

        # 如果有评论，则抓取它们
        for review in reviews:
            try:
                # 获取评论ID（唯一标识，防止重复）
                review_id = review.find_element(By.CLASS_NAME, 'apphub_CardContentAuthorName').find_element(By.TAG_NAME,'a').get_attribute('href')

                # 如果评论已经爬取过，跳过
                if review_id in seen_review_ids:
                    continue

                # 将评论ID加入已爬取集合
                seen_review_ids.add(review_id)

                # 获取评论的相关信息
                nick = review.find_element(By.CLASS_NAME, 'apphub_CardContentAuthorName').text.strip()
                title = review.find_element(By.CLASS_NAME, 'title').text.strip()
                hours = review.find_element(By.CLASS_NAME, 'hours').text.split(' ')[0].strip()
                profile_link = review.find_element(By.CLASS_NAME, 'apphub_CardContentAuthorName').find_element(
                    By.TAG_NAME, 'a').get_attribute('href')
                comment = review.find_element(By.CLASS_NAME, 'apphub_CardTextContent').text.strip()

                # 将评论写入 CSV 文件
                writer.writerow([nick, title, hours, profile_link, comment, 'en'])
                print(f"评论: {nick} | {title} | {comment[:50]}...")  # 打印评论前 50 个字符

            except Exception as e:
                print(f"抓取评论时出错: {e}")

        # 执行滚动操作
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # 等待新评论加载

        # 获取新的滚动高度
        new_height = driver.execute_script("return document.body.scrollHeight")

        # 如果滚动高度没有变化，说明已经到底部，停止抓取
        if new_height == last_height:
            print("已到达页面底部，停止抓取评论。")
            break

        last_height = new_height  # 更新滚动高度

# 关闭浏览器
driver.quit()
