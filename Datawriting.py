import csv
from Passwords import Word , Password
from collections import Counter

def write_pwd_file(pwd_list, otp_dict):
    # 将排序结果写入 CSV 文件
    with open(otp_dict, "w", newline='') as output_file:
        csv_writer = csv.writer(output_file)
        # 写入数据
        for password in pwd_list:
            # 获取该密码实例的 words 字典
            words = password.words
            row = [password.password , password.count]

            for word , count in words.items():
                if word != '':
                    row.extend([word])
                    row.extend([count])
            # 将 words 字典的每个键值对写入 CSV 文件
            csv_writer.writerow(row)

def write_pattern_file(pwd_list , otp_dict):
    formated_pattern = []
    for password in pwd_list:
        patterns = password.pattern
        count = password.count
        pattern = ''.join(f"{p[0]}:{p[1]}" for p in patterns.pattern)
        formated_pattern.append(pattern)

    pattern_counter = Counter(formated_pattern )
    sorted_pattern = pattern_counter.most_common()

    with open(otp_dict, "w", newline='') as output_file:
        csv_writer = csv.writer(output_file)
        for (pattern) , count in sorted_pattern:
            csv_writer.writerow([patterns , count])

            
        

