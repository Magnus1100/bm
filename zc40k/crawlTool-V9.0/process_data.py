import csv
from langdetect import detect
from datetime import datetime
import re

input_review = "processed_reviews.csv"


def read_csv(input_file):
    with open(input_file, mode='r', encoding='utf-8-sig', errors='ignore') as file:
        reader = csv.reader(file)
        header = next(reader)  # 跳过标题行
        raw_data = [row for row in reader]
    return header, raw_data


# 删除空白行
def remove_empty_rows(raw_data):
    cleaned_data = []
    for row in raw_data:
        # 如果该行所有元素都是空字符串或None，则删除
        if any(cell.strip() for cell in row):  # strip() 删除两端空白字符，any() 判断是否有非空的单元格
            cleaned_data.append(row)
    return cleaned_data

# 提取日期并删除评论中的日期
def extract_and_remove_date(comment):
    # 正则匹配日期
    date_match = re.match(r'Posted:\s*(\w+\s*\d+)', comment)
    if date_match:
        date_str = date_match.group(1)
        try:
            # 转换日期格式
            formatted_date = datetime.strptime(date_str, "%B %d").strftime("%Y-%m-%d")
        except ValueError:
            formatted_date = date_str
        # 删除日期部分
        cleaned_comment = comment.replace(date_match.group(0), "").strip()
        return formatted_date, cleaned_comment
    else:
        return "", comment.strip()


# 检测评论语言
def detect_language(comment):
    try:
        return detect(comment)
    except:
        return "unknown"


# 处理评论数据
def process_data(raw_data):
    processed_data = []
    for row in raw_data:
        # 提取日期并删除原评论中的日期
        date, comment = extract_and_remove_date(row[4])  # 假设评论在第5列（索引4）

        # 检测语言
        language = detect_language(comment)

        # 重新格式化数据
        new_row = row[:4]  # 保留原有的前四列数据
        new_row.append(date)  # 添加日期列
        new_row.append(language)  # 添加语言列
        new_row.append(comment)  # 添加清理后的评论内容
        processed_data.append(new_row)

    return processed_data


# 保存处理后的数据
def save_csv(output_file, new_header, new_data):
    with open(output_file, mode='w', encoding='utf-8-sig', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(new_header)  # 写入标题行
        writer.writerows(new_data)  # 写入数据行


# 主函数
if __name__ == '__main__':
    read_csv(input_review)

