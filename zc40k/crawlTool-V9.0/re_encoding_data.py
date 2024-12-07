import csv

# 输入文件路径和输出文件路径
input_file_path = 'translated_comments_2.csv'  # 输入文件路径
output_file_path = 'translated_file/re_encoding.csv'  # 输出文件路径

# 原始文件的编码格式和目标编码格式
source_encoding = 'utf-8-sig'  # 根据你的文件实际编码格式调整
target_encoding = 'utf-8-sig'

# 打开原始文件并写入新编码的文件
try:
    with open(input_file_path, mode='r', encoding=source_encoding) as input_file:
        reader = csv.reader(input_file)

        with open(output_file_path, mode='w', encoding=target_encoding, newline='') as output_file:
            writer = csv.writer(output_file)

            for row in reader:
                writer.writerow(row)

    print(f"文件重新编码完成，已保存到: {output_file_path}")
except Exception as e:
    print(f"处理文件时出错: {str(e)}")
