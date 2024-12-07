import csv
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from collections import defaultdict

# 文件夹路径
input_folder = 'translated_file/versioned_comments_translated'  # 替换为实际路径
output_file_path = 'translated_file/versioned_comments_translated/最负面评论按版本分组.csv'  # 输出文件路径

# 初始化情感分析器
analyzer = SentimentIntensityAnalyzer()

# 用于存储每个版本的负面评论
version_negative_comments = defaultdict(list)

# 读取每个版本文件并筛选最负面评论
for filename in os.listdir(input_folder):
    if filename.endswith('.csv'):
        version_name = filename.split('.')[0]  # 假设文件名即为版本名称
        file_path = os.path.join(input_folder, filename)

        try:
            with open(file_path, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)

                for row in reader:
                    comment = row.get('Comment', '').strip()  # 获取评论内容
                    title = row.get('Title', '').strip()  # 获取时长信息
                    date = row.get('Date', '').strip()  # 获取评论日期

                    if comment:  # 如果评论不为空
                        # 使用 VADER 进行情感分析
                        sentiment_score = analyzer.polarity_scores(comment)
                        negative_score = sentiment_score['compound']

                        # 仅筛选最负面的评论
                        if negative_score <= -0.5:  # 负面程度筛选的阈值
                            version_negative_comments[version_name].append({
                                'Date': date,
                                'Title': title,
                                'Comment': comment,
                                'Negative Score': negative_score
                            })

        except Exception as e:
            print(f"读取文件 {filename} 时出错: {str(e)}")

# 打开并写入输出文件
header = ['Version', 'Date', 'Title', 'Comment', 'Negative Score']  # 列名
with open(output_file_path, mode='w', encoding='utf-8-sig', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=header)
    writer.writeheader()

    # 遍历每个版本并将负面评论输出到同一个文件
    for version_name, comments in version_negative_comments.items():
        # 按照负面得分排序，并获取最负面的20条评论
        comments.sort(key=lambda x: x['Negative Score'], reverse=True)  # 按照负面得分降序排序
        top_comments = comments[:20]  # 获取最负面的20条评论

        # 为每条评论添加版本信息并写入文件
        for comment in top_comments:
            comment['Version'] = version_name  # 添加版本信息
            writer.writerow(comment)

print(f"最负面评论按版本已输出到: {output_file_path}")
