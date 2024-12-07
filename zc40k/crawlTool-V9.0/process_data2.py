import csv
import re
from datetime import datetime

# CSV 文件路径
input_file_path = "processed_reviews.csv"  # 替换为输入文件路径
output_file_path = "processed_file.csv"  # 处理后的输出文件路径

try:
    with open(input_file_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        if 'Comment' in fieldnames:
            # 确保 'date' 列存在，如果不存在则添加
            if 'date' not in fieldnames:
                fieldnames.append('date')

            processed_rows = []
            date_pattern = re.compile(r"Posted: (\d{1,2} \w+|\w+ \d{1,2})")

            for row in reader:
                comment = row['Comment']
                match = date_pattern.search(comment)
                if match:
                    date_text = match.group(1)
                    try:
                        # 解析日期并格式化为标准格式 YYYY-MM-DD
                        if re.match(r"\d{1,2} \w+", date_text):
                            formatted_date = datetime.strptime(date_text, "%d %B").strftime("2024-%m-%d")
                        else:
                            formatted_date = datetime.strptime(date_text, "%B %d").strftime("2024-%m-%d")
                    except ValueError as ve:
                        print(f"日期解析失败: {date_text}, 错误: {ve}")
                        formatted_date = None

                    # 移除日期内容并更新评论和日期列
                    cleaned_comment = date_pattern.sub("", comment).strip()
                    row['Comment'] = cleaned_comment
                    row['Date'] = formatted_date
                else:
                    row['Date'] = None  # 没有匹配到日期时

                processed_rows.append(row)

            # 将处理后的数据写入新文件
            with open(output_file_path, mode='w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(processed_rows)

            print(f"数据已处理并保存到: {output_file_path}")
        else:
            print(f"列 'comment' 未找到。可用列名为: {fieldnames}")
except Exception as e:
    print(f"文件读取或写入出错: {str(e)}")
