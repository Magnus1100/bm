import csv
import os
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 设置 matplotlib 使用 "PMingLiU" 字体来支持繁体中文
rcParams['font.sans-serif'] = ['KaiTi']
rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 文件夹路径
input_folder = 'translated_file/versioned_comments_translated'  # 替换为包含版本文件的文件夹路径
# 保存图像到文件
output_image_path = 'translated_file/versioned_comments_translated/版本差评分析.png'  # 设置输出文件路径

# 用于存储每个版本的评论数量和 "Title" 为 0 的评论数量
version_data = defaultdict(lambda: {'total': 0, 'title_0': 0})

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

                    # 更新版本数据
                    version_data[version_name]['total'] += 1
                    if title == '0':
                        version_data[version_name]['title_0'] += 1

        except Exception as e:
            print(f"读取文件 {filename} 时出错: {str(e)}")

# 计算每个版本中 'Title' 为 0 的评论占比
version_names = []
title_0_percentages = []
non_title_0_percentages = []

for version_name, data in version_data.items():
    total_comments = data['total']
    title_0_comments = data['title_0']

    if total_comments > 0:
        title_0_percentage = (title_0_comments / total_comments) * 100
        non_title_0_percentage = 100 - title_0_percentage
    else:
        title_0_percentage = 0
        non_title_0_percentage = 100

    version_names.append(version_name)
    title_0_percentages.append(title_0_percentage)
    non_title_0_percentages.append(non_title_0_percentage)

# 绘制多个条状图（差评与非差评占比，横向）
fig, ax = plt.subplots(figsize=(10, 6))

# 绘制差评部分，使用清新的蓝色
bars_title_0 = ax.barh(version_names, title_0_percentages, color='#aec6cf', label='差评')  # 浅蓝色

# 绘制非差评部分，使用清新的橙色
bars_non_title_0 = ax.barh(version_names, non_title_0_percentages, left=title_0_percentages, color='#f5c9a1', label='非差评')  # 浅橙色

# 添加标签和标题
ax.set_xlabel('评论占比(%)')
ax.set_ylabel('版本')
ax.set_title('不同版本差评与非差评占比')

# 在色块上添加数量和占比
for i, (bar_title_0, bar_non_title_0, version_name) in enumerate(zip(bars_title_0, bars_non_title_0, version_names)):
    total_comments = version_data[version_name]['total']
    title_0_count = version_data[version_name]['title_0']
    non_title_0_count = total_comments - title_0_count

    # 差评部分
    if bar_title_0.get_width() > 0:  # 仅当宽度大于0时添加标签
        ax.text(
            bar_title_0.get_width() / 2,  # X 坐标在差评色块中间
            bar_title_0.get_y() + bar_title_0.get_height() / 2,  # Y 坐标在差评色块中间
            f"{title_0_count} ({title_0_percentages[i]:.1f}%)",  # 文本内容
            ha='center', va='center', fontsize=9
        )

    # 非差评部分
    if bar_non_title_0.get_width() > 0:  # 仅当宽度大于0时添加标签
        ax.text(
            bar_non_title_0.get_x() + bar_non_title_0.get_width() / 2,  # X 坐标在非差评色块中间
            bar_non_title_0.get_y() + bar_non_title_0.get_height() / 2,  # Y 坐标在非差评色块中间
            f"{non_title_0_count} ({non_title_0_percentages[i]:.1f}%)",  # 文本内容
            ha='center', va='center', fontsize=9
        )

# 添加图例
ax.legend()

# 调整布局并保存图像
plt.tight_layout()
plt.savefig(output_image_path, dpi=300)  # 保存为 PNG 文件，并设置高分辨率
print(f"图像已保存到 {output_image_path}")

plt.show()
