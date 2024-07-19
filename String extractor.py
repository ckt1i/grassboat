import csv
import random

import nltk
passwords = []
cnt = 0
# with open('rockyou.txt', 'r') as file:
#     str = file.readline()
#     while str:
#         try:
#             str = str.rstrip('\n')
#             passwords.append(str)
#             str = file.readline()
#         except:
#             pass
# with open('occurrence.100K.txt', 'r') as file:
#     str = file.readline()
#     while str:
#         str = str.split('|')
#         # try:
#         passwords.append(str[0])
#         str = file.readline()
#         # except:
#         #     pass
# passwords = list(set(passwords))
# print('finished')
# with open('passwords.txt', 'w') as file:
#     for password in passwords:
#         file.write(password + '\n')
with open('dic_with_time2.csv', 'r', encoding='utf-8') as file:
    st = file.readline()
    while st:
        passwords.append(st.rstrip('\n').split(',')[0])
        st = file.readline()
print('Finished')
names = []
with open('yob2023.txt', 'r') as file:
    st = file.readline()
    cnt = 0
    while st:
        cnt += 1
        if cnt > 500:
            break
        st = st.split(',')[0].lower()
        names.append(st)
        st = file.readline()
words = []
with open('1grams_freq.csv', 'r') as file:
    st = file.readline()
    while st:
        st = st.split(',')[0].lower()
        if len(st) >= 3:
            words.append(st)
        st = file.readline()
for i in range(0, 10):
    print(names[i], words[i])
words = set(words) | set(names)
mp = dict()
cnt = 0
# print(len(passwords))
random.shuffle(passwords)
# passwords = passwords[:4000000]

def chk_num(st):
    for i in st:
        if i < '0' or i >'9':
            return False
        return True

for password in passwords:
    cnt += 1
    if cnt % 1000 == 0:
        print(cnt, len(passwords))
    L = len(password)
    tmp_list = []
    for i in range(L):
        for j in range(i, L):
            st = password[i : j + 1].lower()
            if st in words:
                tmp_list.append(st)
    for i in range(L):
        for j in range(i, L):
            if j - i + 1 >= 3:
                tg = True
                st = password[i : j + 1].lower()

                if chk_num(st) and (i != 0 and password[i - 1] >= '0' and password[i - 1] <= '9' or j != L - 1 and password[j + 1] >= '0' and password[j + 1] <= '9'):
                    continue
                for tmp in tmp_list:
                    if st in tmp:
                        tg = False
                        break
                    # if tmp in st:
                    #     tg = False
                    #     break
                if tg:
                    if st in mp.keys():
                        mp[st] += 1
                    else:
                        mp[st] = 1
result = []

for key, value in mp.items():
    result.append((key, value))
result.sort(key=lambda x : x[1], reverse=True)
with open('result.csv', 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerows(result)


