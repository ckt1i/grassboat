import csv
from Passwords import *
import math


class Password:
    def __init__(self, password = "",  words=[] , pattern = [] , count = 0):
        self.password = password 
        self.words = words
        self.pattern = pattern
        self.count = count
    
    def addword(self, word, count=1):
        if word in self.words:
            self.words[word] += count
        else:
            self.words[word] = count

    def findword(self, word):
        # 查找 words 字典中特定单词的计数值
        return self.words.get(word, None)  # 如果找不到返回 None 或者适当的默认值
    
    def extract_word(self):
        pass

    def calculate_pattern(self):
        pass
    
    def levenshtein_distance(self, s1, s2):
        m, s1_len = len(s1), len(s2)
        if m < s1_len:
            return self.levenshtein_distance(s2, s1)

        previous_row = range(s1_len + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def calculate_edit_char(self):
        
        password = self.password
        words = self.words
        patterns = self.pattern
        item_index = 0
        word_index = 0
        editing_num = 0

        for word in words:
            while(patterns[item_index][0] != "w"):
                word_index += patterns[item_index][1]
                item_index += 1
            
            editing_num += self.levenshtein_distance(password[word_index:word_index+len(word)] , word)
            word_index += patterns[item_index][1]
            item_index += 1

        return editing_num


    def calculate_pwd_space(self):
        type_num = 10
        editing_num = self.calculate_edit_char()
        patterns = self.pattern
        word_num = 0
        adding_num = 0
        for pattern in patterns:
            if pattern[0] == "w":
                word_num += pattern[1]
            else:
                adding_num += pattern[1]

        editing_space = math.comb(word_num , editing_num)
        adding_space = pow(type_num , adding_num)
        pwd_space = editing_space * adding_space

        return pwd_space      


class Word:
    def __init__(self , word = None , count = 0 ,sum = {}):
        self.sum = {}
        self.word_counts = {}
        if word is not None:
            self.word_counts[word] = count
            self.sum += count

    def addword(self, word , count = 0):
        if word in self.word_counts:
            self.word_counts[word] += count            
            self.sum[len(word)] += count
        else:
            self.word_counts[word] = count
            wordlen = len(word)
            if wordlen in self.sum :
                self.sum[wordlen] += count
            else:
                self.sum[wordlen] = count


    
    def getcount(self, word):
        # 获取字符串的出现次数
        return self.word_counts.get(word, 0)

    def get_probability(self,word):
        return self.getcount(word) / self.sum[len(word)]

    def updatecount(self, selected_word, new_count):
        # 更新字符串的出现次数
        if selected_word in self.word_counts:
            count = self.word_counts[selected_word]
            self.word_counts[selected_word] = new_count
            wordlen = len(selected_word)
            self.sum[wordlen] = self.sum[wordlen] - count + new_count
        else:
            raise ValueError(f"{selected_word} not found in word_counts.")
    
    def findword(self, selected_word):
        return selected_word in self.word_counts

    def removeword(self, selected_word):
        # 移除指定字符串
        if selected_word in self.word_counts:
            wordlen = len(selected_word)
            self.sum[wordlen] -= self.word_counts[selected_word]
            del self.word_counts[selected_word]
        else:
            raise ValueError(f"{selected_word} not found in word_counts.")
        
    def write(self, dictionary):
        with open(dictionary, "w", newline='') as output_file:
            csv_writer = csv.writer(output_file)
            for word, count in self.word_counts.items():
                csv_writer.writerow([word, count , len(word)])
        

class Patterns:
    def __init__(self , pattern = [] , rate = 0) -> None:
        self.pattern = pattern
        self.rate = rate

def calculate_rate(password , word , pattern):
    rate = pattern.rate
    for word in password.words:
        rate *= words.get_probability(word)
    
    rate = rate / password.calculate_pwd_space()

    return rate

def poisson_probability(m, lambda_):
    return (math.exp(-lambda_) * lambda_**m) / math.factorial(m)

# Here is the test cases for the calculation

if __name__ == "__main__":
    input_pwd = Password("admin@123" , ["admin"] , [["w" , 5] , ["l" , 4 ]])

    pattern = Patterns( [["w" , 5] , ["l" , 4 ]], 0.4480985037406484)

    words = Word(None,0,51328)
    words.addword("admin",1476)
    rate = calculate_rate(input_pwd , words , pattern)
    print(rate)
    total_rate = 1 - pow((1-rate) ,51328)
    print(total_rate)

