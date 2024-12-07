import csv
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 设置 matplotlib 使用 SimHei 字体来支持中文
rcParams['font.sans-serif'] = ['KaiTi']
rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 初始化情感分析器
analyzer = SentimentIntensityAnalyzer()

# 文件夹路径
input_folder = 'translated_file/versioned_comments_translated'  # 替换为包含版本文件的文件夹路径

# 用于存储每个版本的评论数量和情感分析结果
version_sentiment_data = {}

# 读取每个版本文件并进行情感分析
for filename in os.listdir(input_folder):
    if filename.endswith('.csv'):
        version_name = filename.split('.')[0]  # 假设文件名就是版本名称
        file_path = os.path.join(input_folder, filename)

        # 初始化情感分析数据
        version_sentiment_data[version_name] = {'positive': 0, 'negative': 0, 'neutral': 0, 'total': 0}

        try:
            with open(file_path, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)

                for row in reader:
                    comment = row.get('Comment', '').strip()  # 假设评论内容在"Comment"列
                    if comment:  # 如果评论不为空
                        version_sentiment_data[version_name]['total'] += 1

                        # 使用 VADER 进行情感分析
                        sentiment_score = analyzer.polarity_scores(comment)

                        # 根据情感得分分类
                        if sentiment_score['compound'] >= 0.05:
                            version_sentiment_data[version_name]['positive'] += 1
                        elif sentiment_score['compound'] <= -0.05:
                            version_sentiment_data[version_name]['negative'] += 1
                        else:
                            version_sentiment_data[version_name]['neutral'] += 1

        except Exception as e:
            print(f"读取文件 {filename} 时出错: {str(e)}")

# 输出每个版本的情感分析结果
for version_name, data in version_sentiment_data.items():
    total_comments = data['total']
    positive_percentage = (data['positive'] / total_comments) * 100 if total_comments else 0
    negative_percentage = (data['negative'] / total_comments) * 100 if total_comments else 0
    neutral_percentage = (data['neutral'] / total_comments) * 100 if total_comments else 0

    print(f"版本 {version_name} 情感分析结果:")
    print(f"  正面评论占比: {positive_percentage:.2f}%")
    print(f"  负面评论占比: {negative_percentage:.2f}%")
    print(f"  中性评论占比: {neutral_percentage:.2f}%")
    print("-" * 40)

# 绘制情感占比堆积条形图
version_names = list(version_sentiment_data.keys())
positive_percentages = [data['positive'] / data['total'] * 100 for data in version_sentiment_data.values()]
negative_percentages = [data['negative'] / data['total'] * 100 for data in version_sentiment_data.values()]
neutral_percentages = [data['neutral'] / data['total'] * 100 for data in version_sentiment_data.values()]

x = range(len(version_names))

fig, ax = plt.subplots(figsize=(12, 6))

# 堆积条形图
ax.barh(x, positive_percentages, label='正面', color='#f5c9a1')
ax.barh(x, negative_percentages, left=positive_percentages, label='负面', color='#FFB6C1')
ax.barh(x, neutral_percentages, left=[p + n for p, n in zip(positive_percentages, negative_percentages)],
        label='中性', color='#aec6cf')

# 在每个堆积条上添加占比数字
# 在每个堆积条上添加数量和占比数字
for i, version_name in enumerate(version_names):
    total = version_sentiment_data[version_name]['total']
    positive = version_sentiment_data[version_name]['positive']
    negative = version_sentiment_data[version_name]['negative']
    neutral = version_sentiment_data[version_name]['neutral']

    # 计算百分比
    positive_percentage = (positive / total) * 100 if total else 0
    negative_percentage = (negative / total) * 100 if total else 0
    neutral_percentage = (neutral / total) * 100 if total else 0

    # 添加每一部分的数量和占比文本
    ax.text(positive_percentage / 2, i, f"{positive} ({positive_percentage:.1f}%)",
            ha='center', va='center', fontsize=10, color='black')
    ax.text(positive_percentage + negative_percentage / 2, i, f"{negative} ({negative_percentage:.1f}%)",
            ha='center', va='center', fontsize=10, color='black')
    ax.text(positive_percentage + negative_percentage + neutral_percentage / 2, i,
            f"{neutral} ({neutral_percentage:.1f}%)", ha='center', va='center', fontsize=10, color='black')


# 设置图表属性
ax.set_yticks(x)
ax.set_yticklabels(version_names)
ax.set_xlabel('情感占比 (%)')
ax.set_title('不同版本情感分析堆积条形图')
ax.legend()

plt.tight_layout()

# 保存图形
plt_path = os.path.join(input_folder, "版本情感分布堆积条形图.png")
plt.savefig(plt_path)
print(f"统计图已保存到: {plt_path}")

# 显示图形
plt.show()
