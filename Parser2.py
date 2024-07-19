import copy
import heapq
from enum import Enum
import nltk
import Levenshtein
class SegType(Enum):
    WORD = 1
    STRING = 2
    NUMBER = 3
    ALPHA = 4
    SPECIAL = 5

class PatternType(object):
    def __init__(self, matched_word, type, original_length, matched_length):
        self.matched_word = matched_word
        self.type = type
        self.original_length = original_length
        self.matched_length = matched_length
    def __str__(self):
        return f"({self.matched_word}, {self.type}, {self.original_length}, {self.matched_length})"
class Parser(object):
    def __init__(self, match_type='complete', segment_type='original', heuristic_type='coverage', probability_type='context-free'):
        self.replace_rules = dict()
        self.init_replace_rules()

        self.word_corpus = []
        self.str_corpus = []
        self.init_corpus()

        self.match_type = match_type
        self.segment_type = segment_type
        self.heuristic_type = heuristic_type
        self.probability_type = probability_type

        self._log2_ = [0 for i in range(256 + 1)]
        self._log2_[1] = 0
        for i in range(2, 256 + 1):
            self._log2_[i] = self._log2_[i >> 1] + 1
        pass
    def init_replace_rules(self):
        self.replace_rules = {"4" : "a" , "@":"a" , "8" : "b" , "6" : "b", "3" : "e" , "9" : "g" , "1" : "i" ,"0" : "o" ,"$" : "s" , "5" : "s" , "+" : "t" , "/\'" : "w"}
    def init_corpus(self):
        # nltk.download('words')
        # self.word_corpus = set(nltk.corpus.words.words())
        # tmp_list = []
        # for word in self.word_corpus:
        #     if len(word) == 1 and (word != 'a' or word != 'I'):
        #         continue
        #     tmp_list.append(word)
        # self.word_corpus = tmp_list
        # nltk.download('names')
        # tmp_list = list(set(nltk.corpus.names.words()))
        # for name in tmp_list:
        #     self.word_corpus.append(name.lower())
        self.word_corpus = []
        self.word_freq = dict()
        with open('word_freq.csv', 'r') as file:
            st = file.readline()
            while st:
                tmp = st.strip().split(',')
                word = tmp[0]
                freq = tmp[1]
                self.word_corpus.append(word)
                self.word_freq[word] = float(freq)
                st = file.readline()
        self.word_corpus = set(self.word_corpus)
    def replace_char(self, word : str) -> str:
        for i in range(len(word)):
            if word[i] in self.replace_rules:
                word = word[:i] + self.replace_rules[word[i]] + word[i + 1:]
                # word[i] = self.replace_rules[word[i]]
        return word
    def levenshtein_distance(self, word1, word2):
        return Levenshtein.distance(word1, word2)
    def levenshtein_limit(self, word1, word2, theta):
        L1 = len(word1)
        L2 = len(word2)
        dp = [[0 for i in range(L2 + 1)] for j in range(L1 + 1)]
        for k in range(1, L1 + L2 + 1):
            tmp = 1000000007
            for i in range(max(0, k - L2), min(k, L1) + 1):
                j = k - i
                dp[i][j] = 1000000007
                if i >= 1 and j >= 1:
                    if word1[i - 1] == word2[j - 1]:
                        dp[i][j] = dp[i - 1][j - 1]
                    else:
                        dp[i][j] = dp[i - 1][j - 1] + 1
                if i >= 1:
                    dp[i][j] = min(dp[i][j], dp[i - 1][j] + 1)
                if j >= 1:
                    dp[i][j] = min(dp[i][j], dp[i][j - 1] + 1)
                tmp = min(tmp, dp[i][j])
            if tmp > theta:
                return theta + 1
        return dp[L1][L2]

    def longest_common_subsequence(self, word1, word2):
        dp = [[0 for i in range(len(word2) + 1)] for j in range(len(word1) + 1)]
        for i in range(0, len(word1) + 1):
            for j in range(0, len(word2) + 1):
                if i >= 1:
                    dp[i][j] = max(dp[i][j], dp[i - 1][j])
                if j >= 1:
                    dp[i][j] = max(dp[i][j], dp[i][j - 1])
                if i >= 1 and j >= 1:
                    tmp = 1 if word1[i - 1] == word2[j - 1] else 0
                    dp[i][j] = max(dp[i][j], dp[i - 1][j - 1] + tmp)
        return dp[len(word1)][len(word2)]
    def character_type(self, ch):
        if '0' <= ch <= '9':
            return SegType.NUMBER
        if 'a' <= ch <= 'z' or 'A' <= ch <= 'Z':
            return SegType.ALPHA
        return SegType.SPECIAL
    def fuzzy_match(self, word):
        theta = max(self._log2_[len(word)] - 2, 0)
        min_dist = 1000000007
        matched_word = None
        matched_type = None
        normalized_word = self.replace_char(word).lower()
        # print(len(self.word_corpus))
        cnt = 0
        for other_word in self.word_corpus:
            cnt += 1
            if cnt % 1000 == 0:
                print(cnt)
            # dist = self.levenshtein_limit(normalized_word, other_word, theta)
            dist = self.levenshtein_distance(normalized_word, other_word)
            if dist <= theta and dist < min_dist:
                matched_word = other_word
                min_dist = dist
                matched_type = SegType.WORD
        if self.segment_type == 'extra':
            if word in self.str_corpus:
                matched_word = word
                matched_type = SegType.STRING
        return matched_word, matched_type
    def complete_match(self, word):
        if len(word) == 1:
            normalized_word = word
        else:
            normalized_word = self.replace_char(word).lower()
        if normalized_word in self.word_corpus:
            return normalized_word, SegType.WORD
        if self.segment_type == 'extra' and word in self.str_corpus:
            return word, SegType.STRING
        return None, None
    def calculate_value(self, segment):
        if len(segment) == 1:
            matched_segment, matched_type = self.complete_match(segment)
            if matched_segment is not None:
                return matched_segment, matched_type, 1
            return segment, self.character_type(segment), 0
        matched_segment, matched_type = None, None
        if self.match_type == 'complete':
            matched_segment, matched_type = self.complete_match(segment)
        else:
            matched_segment, matched_type = self.fuzzy_match(segment)
        if matched_segment is None:
            return None, None, 0
        if self.heuristic_type == 'coverage':
            return matched_segment, matched_type, len(matched_segment)
        else:
            return matched_segment, matched_type, self.longest_common_subsequence(segment, matched_segment) ** 2
            # return matched_segment, matched_type, len(matched_segment) ** 2

    def get_word_probability(self, word):
        return self.word_freq[word]
        # return 1
    def get_str_probability(self, word):
        return 1
    def get_n_gram_probability(self, word_list):
        return 1
    def max_probability_division(self, word_list):
        if len(word_list) == 0:
            return 1
        res = 1
        for i in range(1, len(word_list) + 1):
            tmp = self.get_n_gram_probability(word_list[:i])
            if tmp == 0:
                break
            res = max(res, tmp * self.max_probability_division(word_list[i:]))
        return res
    def calculate_probability(self, segments : list[PatternType]):
        # return 1
        sum = 1
        if self.probability_type == 'context-free':
            for seg in segments:
                if seg.type == SegType.WORD:
                    sum *= self.get_word_probability(seg.matched_word)
                elif seg.type == SegType.STRING:
                    sum *= self.get_str_probability(seg.matched_word)
                elif seg.type == SegType.ALPHA:
                    sum *= 1 / 52
                elif seg.type == SegType.NUMBER:
                    sum *= 1 / 10
                elif seg.type == SegType.SPECIAL:
                    sum *= 1 / 20

            return sum

        else:
            return 1
            # word_list = []
            # for seg in segments:
            #     if seg.type == SegType.WORD:
            #         word_list.append(seg.matched_word)
            #     elif seg.type == SegType.STRING:
            #         sum *= self.get_str_probability(seg.matched_word)
            # sum *= self.max_probability_division(word_list)

    def merge_segments(self, seg1 : PatternType, seg2 : PatternType):
        return PatternType(seg1.matched_word + seg2.matched_word, seg1.type, seg1.original_length + seg2.original_length, seg1.matched_length + seg2.matched_length)
    def process_segments(self, segments : list[PatternType]):
        tmp_list = []
        for seg in segments:
            if seg.type == SegType.WORD or seg.type == SegType.STRING:
                tmp_list.append(seg)
            elif len(tmp_list) != 0 and tmp_list[-1].type == seg.type:
                tmp_list[-1] = self.merge_segments(tmp_list[-1], seg)
            else:
                tmp_list.append(seg)
        return tmp_list

    def parse(self, password):

        class node(object):
            def __init__(self, value = 0, segments = None):
                self.value = value
                if segments is None:
                    self.segments = []
                else:
                    self.segments = copy.deepcopy(segments)
                # self.segmentType = segmentType
            def __lt__(self, other):
                return self.value < other.value
            def append(self, value, segment):
                self.segments.append(segment)
                self.value += value

        class PQue(object):
            def __init__(self):
                self.que = []
            def push(self, ele):
                heapq.heappush(self.que, ele)
            def pop(self):
                return heapq.heappop(self.que)
            def size(self):
                return len(self.que)
            def getList(self):
                return self.que

        L = len(password)
        limit = 10
        dp = [PQue() for i in range(L + 1)]
        dp[0].push(node())
        for i in range(1, L + 1):
            for j in range(i - 1, -1, -1):
                matched_segment, matched_type, value = self.calculate_value(password[j : i])
                if matched_segment is None:
                    continue
                trans_list = dp[j].getList()
                for tmp in trans_list:
                    cur = node(tmp.value, tmp.segments)
                    cur.append(value, PatternType(matched_segment, matched_type, i - j, len(matched_segment)))
                    dp[i].push(cur)

            while dp[i].size() > 10:
                dp[i].pop()

        segments_list = dp[L].getList()[::-1]
        segments_list.sort(key=lambda x : x.value, reverse=True)
        segments_list = [node.segments for node in segments_list]
        ans_list = [(segments, self.calculate_probability(segments)) for segments in segments_list]
        for segments, prob in ans_list:
            print(prob, end = ' ')
            tmp_list = self.process_segments(segments)
            for seg in tmp_list:
                print(seg, end = ' ')
            print()
        # for segments in segments_list:
        #     print(segments.value, end=' ')
        #     tmp_list = self.process_segments(segments.segments)
        #     for seg in tmp_list:
        #         print(seg, end=' ')
        #     print()


if __name__ == '__main__':
    # test
    s1 = '1a2b3c'
    s2 = '4a53bc'
    parser = Parser(match_type='complete', heuristic_type='square')
    # parser.fuzzy_match('I1lo')

    password = 'I1love2dog'
    password = 'Anyonebarks67'
    password = input('Enter password: ')
    patterns = parser.parse(password)
    # for pattern in patterns:
    #     print(pattern)

# Anyonebarks67