import csv
from googletrans import Translator
from tqdm import tqdm  # 导入 tqdm 库用于显示进度条

# 输入和输出文件路径
input_file_path = 'processed_file_V2.0.csv'  # 输入文件路径
output_file_path = 'translated_comments_2.csv'  # 输出文件路径

# 初始化翻译器
translator = Translator()

# 用于记录翻译错误的评论及其错误原因
translation_errors = []
total_comments = 0
translated_comments = 0

# 打开输入文件并读取评论
with open(input_file_path, mode='r', encoding='utf-8-sig') as input_file:
    reader = csv.DictReader(input_file)

    # 打开输出文件
    with open(output_file_path, mode='w', encoding='utf-8', newline='') as output_file:
        fieldnames = reader.fieldnames  # 保留输入文件的列名
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)

        writer.writeheader()  # 写入列头

        # 使用 tqdm 显示进度条
        for row in tqdm(reader, desc="翻译进度", unit="条评论"):
            original_comment = row.get('Comment', '').strip()

            if original_comment:  # 如果评论不为空
                total_comments += 1

                try:
                    # 翻译评论
                    translated_comment = translator.translate(original_comment, src='auto', dest='en').text
                    if translated_comment:  # 如果翻译结果不为空
                        row['Comment'] = translated_comment  # 将评论替换为翻译后的评论
                        writer.writerow(row)
                        translated_comments += 1
                    else:
                        raise ValueError("翻译结果为空")
                except Exception as e:
                    # 记录翻译失败的评论和错误信息
                    error_message = str(e)
                    translation_errors.append((original_comment, error_message))

# 输出翻译过程的统计信息
print(f"总评论数: {total_comments}, 翻译成功的评论数: {translated_comments}")
print(f"翻译完成，文件保存在: {output_file_path}")

# 输出翻译错误的评论及原因
if translation_errors:
    print("\n翻译失败的评论及错误原因:")
    for original_comment, error_message in translation_errors:
        print(f"评论: {original_comment}\n错误原因: {error_message}\n")
else:
    print("所有评论翻译成功，没有失败的评论。")
