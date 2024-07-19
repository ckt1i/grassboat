'''
Here is our search about attackers based on the password data collected by the basic words.
We use some basic data processing words to collect the word in password. And we sort them to get
some information about the malicious passwords.
'''
from Passwords import Word , Password
import Datawriting
import nltk
import re
from nltk.corpus import reuters



def pick_words(input_string , dictionary):
    found_words = []
    start = 0
    end = len(input_string)
    while start < end:
        for i in range(end, start, -1):
            substring = input_string[start:i]
            # ignore strings that is too short
            if substring in dictionary and len(substring) >= 3:
                found_words.append(input_string[start:i])
                start = i
                break
        else:
            start += 1
    
    return found_words

def replace_characters(input_string):
    substitution_dict = {"4" : "a" , "@":"a" , "8" : "b" , "6" : "b", "3" : "e" , "9" : "g" , "1" : "i" ,"0" : "o" ,"$" : "s" , "5" : "s" , "+" : "t" , "/\'" : "w"}
    result = []
    for char in input_string:
        if char in substitution_dict:
            result.append(substitution_dict[char])
        else:
            result.append(char)
    return ''.join(result)

def find_words_ex(password , word_list , special_words , weak_passwords):

    found_words = []

    for weak_password in weak_passwords:
        if weak_password in password and weak_password not in found_words:
            if found_words == []:
                found_words.append(weak_password.lower())
            for another_word in found_words :
                if weak_password in another_word or weak_password.lower() == another_word:
                    break
                found_words.append(weak_password.lower())
        continue
    
    for special_word in special_words:
        if special_word in password and special_word not in found_words:
            if found_words == []:
                found_words.append(special_word.lower())
            for another_word in found_words :
                if special_word in another_word or special_word.lower() == another_word:
                    break
                found_words.append(special_word.lower())
        else:
            continue

    found_words2 = pick_words(password , word_list)

    for words2 in found_words2:
        if found_words == []:
            found_words = found_words2
            break
        flag = 1
        for words in found_words:
            if words2 in words or words2.lower() == words:
                flag = 0
            else:
                continue
        if flag == 1 :
            found_words.append(words2)

    return found_words

# here we use two ways to check whether the word can be recognized as a word-based words
def find_words(password , word_list , special_words , weak_passwords , words):

    inp_pwd = password.password

    # Here we defined two situations, one is no change of words and just add the word and the other is make some basic changes.
    found_words_ori = find_words_ex(inp_pwd , word_list , special_words , weak_passwords)
    #Pre processing strings
    pre_proc_string = replace_characters(inp_pwd)

    # 预处理字符串，去掉非字母字符，并转为小写
    processed_string = re.sub(r'[^a-zA-Z]', '', pre_proc_string).lower()
    
    found_words_proc = find_words_ex(processed_string , word_list , special_words , weak_passwords)
    
    found_words_set = set(found_words_proc).union(found_words_ori)

    found_words = list(found_words_set)

    if len(found_words) < 1:
        return 0
    
    if len(found_words) < 2:
        found_words.append("")

    # return longest subwords we find
    max3_words = sorted(found_words, key=len, reverse=True)[:3]
#    if len("".join(max3_words)) + 5 <=  len(inp_pwd):
#       return 0 

    for word in max3_words:
        password.addword(word , -1)
        words.addword(word, password.count)
        if words.findword(word):
            count = words.getcount(word)
            count += password.count
            words.updatecount(word, count)
        else:
            words.addword(word, password.count)

    return 1
    

def count_unique_characters(input_string):
    unique_chars = set(input_string) 
    num_unique_chars = len(unique_chars) 
    return num_unique_chars

#Check whether a password is a weak password
def is_weak_password(pwd , weak_passwords):
    password = pwd.password
    # check the password length and uniqueness
    if(len(password) <= 8 or (password.isdigit() and len(password) <= 12) or count_unique_characters(password) <= 6):
        return 1
    else:
        # check whether a password is based on the typically weak password
        weak_words = pick_words(password , weak_passwords)
        if not weak_words:  
            return 0  
        else:
            longest_word = max(weak_words, key=len)
            if len(longest_word) + 3 > len(password):
                return 1
            else:
                return 0


def read_pwd_lib(filename):
    passwords = []
    # 读取日志文件并提取用户名和密码
    with open(filename, "r") as log_file:
        log_lines = log_file.readlines()

    for line in log_lines:
        unit = line.split(",")
        try:
            password = Password(password=unit[0].strip(), count=int(unit[1].strip()))
        except:
            continue
        passwords.append(password)

    return passwords

def read_dict(file_path):
    passwords = []
    
    with open(file_path, 'r') as file:
        for line in file:
            password = line.strip()  # 移除行末的换行符和多余的空格
            if password:  # 如果行不为空
                passwords.append(password)
    return passwords
    
def sort_passwords(passwords , word_list , special_words , weak_passwords):
    pwd_weak = []
    pwd_weak_cnt = 0
    pwd_wb = []
    pwd_wb_cnt = 0
    pwd_strong = []
    pwd_strong_cnt = 0
    pwd_words = Word(None , 0)

    for password in passwords:
        if is_weak_password(password , weak_passwords):
            pwd_weak.append(password)
            pwd_weak_cnt += password.count
        else:
            if(find_words(password , word_list , special_words , weak_passwords , pwd_words)):
                pwd_wb.append(password)
                pwd_wb_cnt += password.count
            else:
                pwd_strong.append(password)
                pwd_strong_cnt += password.count

    total_cnt = pwd_weak_cnt + pwd_wb_cnt + pwd_strong_cnt
    print("weak passwords have:" + str(pwd_weak_cnt) + " accounts for: " + str(pwd_weak_cnt / total_cnt))
    print("word based passwords have:" + str(pwd_wb_cnt) + " accounts for: " + str(pwd_wb_cnt / total_cnt))
    print("strong passwords have:" + str(pwd_strong_cnt) + " accounts for: " + str(pwd_strong_cnt / total_cnt))

    return pwd_words , pwd_weak , pwd_wb , pwd_strong
 


def main():

    pwd_record = "datas/dic_with_time2.csv"
    weak_pwd_dict_name = "datas/weak_origin.csv"
    special_dict_name = "datas/special_words.csv"

    weak_dict = "datas/weak_dictionary2.csv"
    wb_dict = "datas/wordbased_dictionary2.csv"
    strong_dict = "datas/strong_dictionary2.csv"
    words_dict = "datas/word_dictionary2.csv"
    pattern_dict = "datas/patterns2.csv"

    # Downloat nltk dictionary
    nltk.download('words')


    word_list = set(reuters.words())

    passwords = read_pwd_lib(pwd_record)
    weak_passwords = read_dict(weak_pwd_dict_name)
    special_words = read_dict(special_dict_name)
    
    pwd_words , pwd_weak , pwd_wb , pwd_strong = sort_passwords(passwords , word_list , special_words , weak_passwords)   
    
    Datawriting.write_pwd_file(pwd_weak, weak_dict)
    Datawriting.write_pwd_file(pwd_wb, wb_dict)
    Datawriting.write_pwd_file(pwd_strong, strong_dict)
    Datawriting.write_pattern_file(pwd_wb , pattern_dict)
    pwd_words.write(words_dict)


if __name__ == "__main__":
    main()