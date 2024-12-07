import csv
import os
from collections import defaultdict
from nltk.corpus import stopwords
from nltk.util import ngrams
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from matplotlib import rcParams
import nltk

# 下载nltk资源
nltk.download('stopwords')

# 设置 matplotlib 使用 "PMingLiU" 字体来支持繁体中文
rcParams['font.sans-serif'] = ['KaiTi']
rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# ======== 使用步骤：========= #
# 修改输入文件&输出文件夹，输出即可
# ========================== #

# 文件夹路径
input_folder = 'translated_file/versioned_comments_translated'  # 替换为包含版本文件的文件夹路径
# 保存词云图像到文件
output_image_path = 'translated_file/versioned_comments_translated/词云图.png'  # 设置输出文件路径

# 用于存储每个版本的评论数量和 "Title" 为 0 的评论数量
version_data = defaultdict(lambda: {'total': 0, 'title_0': 0, 'negative_comments': []})

# 读取每个版本文件并处理数据
for filename in os.listdir(input_folder):
    if filename.endswith('.csv'):
        version_name = filename.split('.')[0]  # 假设文件名就是版本名称
        file_path = os.path.join(input_folder, filename)

        try:
            with open(file_path, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)

                for row in reader:
                    # 获取标题（Title）并判断是否为 '0'
                    title = row.get('Title', '').strip()
                    comment = row.get('Comment', '').strip()  # 假设评论内容在"Comment"列

                    # 更新版本数据
                    version_data[version_name]['total'] += 1
                    if title == '0':  # 标题为 0 表示差评
                        version_data[version_name]['title_0'] += 1
                        # 将差评添加到负面评论列表
                        if comment:
                            version_data[version_name]['negative_comments'].append(comment)

        except Exception as e:
            print(f"读取文件 {filename} 时出错: {str(e)}")

# 处理负面评论文本
negative_comments = []
for version_name, data in version_data.items():
    negative_comments.extend(data['negative_comments'])

# 检查负面评论的数量
print(f"负面评论的数量: {len(negative_comments)}")

# 如果有负面评论，进行词云分析
if len(negative_comments) > 0:
    # 获取英语停用词
    stop_words = set(stopwords.words('english'))

    # 生成2-grams
    def generate_ngrams(text, n=2):
        words = text.lower().split()
        words = [word for word in words if word not in stop_words and len(word) > 2]
        return list(ngrams(words, n))

    # 对负面评论进行2-grams处理
    all_ngrams = []
    for comment in negative_comments:
        all_ngrams.extend(generate_ngrams(comment))

    # 将2-grams转为字符串，以便生成词云
    ngram_strings = [' '.join(ngram) for ngram in all_ngrams]
    text_for_wordcloud = ' '.join(ngram_strings)

    # 生成词云
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_for_wordcloud)

    # 显示词云
    plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")  # 去掉坐标轴
    plt.tight_layout()

    # 保存词云图
    plt.savefig(output_image_path, dpi=300)
    print(f"词云图已保存到 {output_image_path}")

    plt.show()

else:
    print("没有负面评论可用于分析。")
