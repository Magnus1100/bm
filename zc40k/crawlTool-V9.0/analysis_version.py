import os
import csv
from datetime import datetime
from collections import Counter

import matplotlib.pyplot as plt
from matplotlib import rcParams

# ======== 使用步骤：========= #
# 修改输入文件&输出文件夹，输出即可
# ========================== #

# 设置 matplotlib 使用 SimHei 字体来支持中文
rcParams['font.sans-serif'] = ['KaiTi']
rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 输入和输出文件路径
input_file_path = "translated_file/re_encoding.csv"  # 上一步生成的 CSV 文件
output_folder = "versioned_comments_translated"  # 输出文件夹

# 创建输出文件夹
os.makedirs(output_folder, exist_ok=True)


# 定义版本划分规则
def determine_version(date_str):
    try:
        # 将日期字符串转换为 datetime 对象
        date = datetime.strptime(date_str, "%Y/%m/%d")  # 支持 'YYYY/MM/DD' 格式
    except ValueError:
        return "Unknown"  # 如果日期格式不正确，返回 Unknown

    # 版本划分
    version_1_end = datetime(2024, 9, 11)
    version_2_start = datetime(2024, 9, 12)
    version_2_end = datetime(2024, 9, 26)
    version_3_start = datetime(2024, 9, 27)
    version_3_end = datetime(2024, 10, 17)
    version_4_start = datetime(2024, 10, 18)
    version_4_end = datetime(2024, 11, 12)
    version_4_5_start = datetime(2024, 11, 13)
    version_4_5_end = datetime(2024, 12, 3)

    # 比较日期并返回版本
    if date <= version_1_end:
        return "Version 1"
    elif version_2_start <= date <= version_2_end:
        return "Version 2"
    elif version_3_start <= date <= version_3_end:
        return "Version 3"
    elif version_4_start <= date <= version_4_end:
        return "Version 4"
    elif version_4_5_start <= date <= version_4_5_end:
        return "Version 4.5"
    else:
        return None  # 去掉 Other 和 Unknown


try:
    with open(input_file_path, mode='r', encoding='utf-8-sig') as file:  # 使用 'utf-8-sig' 编码以自动处理 BOM
        reader = csv.DictReader(file)
        header = [field.strip() for field in reader.fieldnames]  # 去除列名中的 BOM 字符

        if 'Date' in header:
            # 创建一个字典，按版本存储评论
            versioned_comments = {"Version 1": [], "Version 2": [], "Version 3": [], "Version 4": [], "Version 4.5": []}

            # 处理每一行数据
            for row in reader:
                date = row.get('Date')  # 获取日期字段
                version = determine_version(date)  # 确定版本
                if version:  # 如果版本不为 None，则添加到相应的版本列表
                    versioned_comments[version].append(row)

            # 保存分类后的评论到不同版本的文件中
            for version, comments in versioned_comments.items():
                if comments:  # 仅保存非空版本
                    output_file_path = os.path.join(output_folder, f"{version.replace(' ', '_')}.csv")
                    with open(output_file_path, mode='w', encoding='utf-8', newline='') as outfile:
                        writer = csv.DictWriter(outfile, fieldnames=header)
                        writer.writeheader()
                        writer.writerows(comments)
            print(f"分类评论已保存到文件夹: {output_folder}")

            # 统计评论数量并绘制堆积条形图
            version_counts = {version: len(comments) for version, comments in versioned_comments.items()}
            labels = list(version_counts.keys())
            sizes = list(version_counts.values())
            total = sum(sizes)

            plt.figure(figsize=(12, 2))  # 调整条形比例
            bottom = 0

            # 调整条形高度为更小的值
            for i, size in enumerate(sizes):
                bar_color = plt.cm.Paired(i / len(labels))
                plt.barh(0, size / total, left=bottom, height=0.1, label=labels[i], color=bar_color)

                # 计算占比百分比
                percentage = f"{(size / total) * 100:.1f}%"

                # 在条形图上添加数量和占比标签
                plt.text(bottom + (size / (2 * total)), 0, f"{size}\n({percentage})",
                         ha='center', va='center', fontsize=10, color='black')
                bottom += size / total

            # 设置图表属性
            plt.xlim(0, 1)
            plt.xticks([i / 10 for i in range(11)])  # X轴刻度设置为 0.1 的间距
            plt.xlabel('占比 (Total = 100%)')
            plt.title('版本评论数量分布')
            plt.yticks([])  # 隐藏 Y 轴刻度

            # 图例位置调整
            plt.legend(
                loc="upper center",  # 图例位置调整到图形下方中央
                bbox_to_anchor=(0.5, -0.2),  # 设置图例锚点位置，适当下移
                ncol=len(labels),  # 每行显示的图例数量，与版本数量一致
                fontsize=10,  # 图例字体大小
                frameon=True  # 添加图例边框以增强可见性
            )

            # 保存图形
            plt_path = os.path.join(output_folder, "版本评论占比3.png")
            plt.savefig(plt_path, bbox_inches='tight')
            print(f"统计图已保存到: {plt_path}")

            # 显示图形
            plt.show()


        else:
            print(f"列 'Date' 未找到。可用列名为: {header}")

except Exception as e:
    print(f"文件读取出错: {str(e)}")
