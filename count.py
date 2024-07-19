import csv
from collections import Counter
from Passwords import Password

# 读取日志文件并提取用户名和密码
with open("fakessh-2024-07-11-12-55-17-000.log", "r") as log_file:
    log_lines1 = log_file.readlines()

with open("fakessh-2024-07-11-12-55-17-000.log", "r") as log_file:
    log_lines2 = log_file.readlines()

log_lines = log_lines1 + log_lines2

num = 0
credentials = []

for line in log_lines:
    unit = line.split()
    if len(unit) != 6:  # 假设每一行都应该有6个元素
        continue
    passwords = unit[5]
    credentials.append((passwords))
    num += 1

# 统计用户名和密码的出现次数
credential_counter = Counter(credentials)

# 将统计结果按出现次数从高到低排序
sorted_credentials = credential_counter.most_common()

# 将排序结果写入CSV文件
with open("dic_with_time2.csv", "w", newline='') as output_file:
    csv_writer = csv.writer(output_file)
    for (passwords), count in sorted_credentials:
        csv_writer.writerow([passwords , count])
    print(num)


