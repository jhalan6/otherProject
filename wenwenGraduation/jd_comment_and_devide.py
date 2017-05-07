#!/usr/bin/env python
# coding:utf-8
# Author:yunya  Created: 2016/12/6
# copy from http://www.yunya.pw/?post=18
from __future__ import division
import urllib2
import re
import json
import math
import random
import time
import sys
import codecs
import requests
import pandas as pd
import jieba
import jieba.analyse


def solve_encode():
        """
            解决加载文件、输出等时候的编码问题
        """
        reload(sys)
        sys.setdefaultencoding("utf-8")

def get_comments_from_jd():
        """
            在jd上抓取评论，并将评论写到两个文件中。
            contents.txt中每一行放一条评论内容
            file.csv中放了抓取步骤中拿到的全部数据。需要的时候可以读取。
            本方法可以独立运行，即生成两个文本文件为后续功能提供准备工作。
        """
        l_cmt, l_time, l_like, l_score, l_reply, l_level, l_prov, l_nn, \
            l_client = [], [], [], [], [], [], [], [], []
        result_lines = []
        pid = sys.argv[1]
        pages = int(sys.argv[2])

        for page in range(pages):
                print "Page %i ..." % (page + 1)
                url = "https://sclub.jd.com/comment/productPageComments.action?productId=" +\
                    pid + "&score=0&sortType=3&page=" + str(page) + \
                    "&pageSize=10&callback=fetchJSON_comment98vv37464"

                print url
                ws1 = urllib2.urlopen(url).read()
                groups = re.findall(
                    '''\{"id":\d+,.*?,"content":"((?:(?!<\/div>).|\n)*?)",.*?,"referenceTime":"(.*?)",.*?,"replyCount":(\d+),"score":(\d+),"status":\d,"title":"","usefulVoteCount":(\d+),.*?,"userLevelId":"(.*?)","userProvince":"(.*?)",.*?,"nickname":"(.*?)","userClient":(\d+),''',
                    ws1)
                for g in groups:
                        l_cmt.append(g[0])
                        l_time.append(g[1])
                        l_like.append(g[2])
                        l_score.append(g[3])
                        l_reply.append(g[4])
                        l_level.append(g[5])
                        l_prov.append(g[6])
                        l_nn.append(g[7])
                        l_client.append(g[8])
                        result_lines.append(
                            ("%s\n" %
                             g[0]).decode(
                                'gbk',
                                'ignore').encode('utf-8'))
                time.sleep(random.randint(5, 10) / 10.0)

        df = pd.DataFrame({"cmt": l_cmt,
                           "time": l_time,
                           "like": l_like,
                           "score": l_score,
                           "reply": l_reply,
                           "level": l_level,
                           "prov": l_prov,
                           "nn": l_nn,
                           "client": l_client})
        df.to_csv('file.csv', index=False)
        print "grep from jd done.."
        write_to_file("contents.txt", result_lines)
        print "write contents.txt done"


def init_devide_sentence_env():
        """
            初始化语言云的分词时使用，如果不使用语言云的分词，可以不调用
        """
        global api_key
        global format
        global pattern
        global url_get_base
        api_key = 'i1o4P9M192j2l7y1U1I1lrhhyyeAaZrmTqdXhXsj'
        format = 'json'
        pattern = 'dp'
        url_get_base = "http://ltpapi.voicecloud.cn/analysis/"


def write_to_file(file_name, lines):
        """
            一个公用的基础方法，传入文件名及文件内容，以utf8的格式写入到文件中。
        """
        f = codecs.open(file_name, "w", "utf-8")
        for line in lines:
                f.write(line)
        f.close()


def fetch_all_words_from_yu_yin_yun(file_name):
        """
            从语言云对文件中的语句进行分词。
            Args:
                file_name : 需要分词的文件名。文件中每一行为一个句子
            Returns:
                all_words : 一个字典类型的数据。key是需要分词的句子，value是分词
                    结果组成的一个list
                    举例：{
                    "今天是个好日子":["今天", "是个", "好", "日子"],
                    "这个手机真不错":["这个", "手机", "真", "不错"]
                    }
        """
        all_words = {}
        for line in open(file_name):
                request_data = {
                    "api_key": api_key,
                    "text": unicode(line),
                    "pattern": pattern,
                    "format": format}

                result = requests.post(url_get_base, data=request_data).content
                content = result.strip()
                js = json.loads(content)
                devided_words = []
                for sent in js[0]:
                        for data in sent:
                                devided_words.append(data['cont'])
                all_words[line[:-1]] = devided_words
        return all_words


def fetch_all_words_from_jieba(file_name):
        """
            利用jieba分词对文件中的语句进行分词。
            Args:
                file_name : 需要分词的文件名。文件中每一行为一个句子
                    举例 : content.txt
                    文件内容为:
                        今天是个好日子
                        这个手机真不错
            Returns:
                all_words : 一个字典类型的数据。key是需要分词的句子，value是分词
                    结果组成的一个list
                    举例：{
                    "今天是个好日子":["今天", "是个", "好", "日子"],
                    "这个手机真不错":["这个", "手机", "真", "不错"]
                    }

        """
        all_words = {}
        for line in open(file_name):
            seg_list = list(jieba.cut(line, cut_all=True))
            all_words[line[:-1]] = seg_list
        return all_words


def write_devide_sentence_and_content_to_file(all_words):
        """
            将分词结果写入到文件中，以备使用
            Args:
                all_words: 一个字典类型的数据。key是需要分词的句子，value是分词
                    结果组成的一个list
                    举例：{
                    "今天是个好日子":["今天", "是个", "好", "日子"],
                    "这个手机真不错":["这个", "手机", "真", "不错"]
                    }
            Returns:
                写入一个文件，文件名为contents.csv
                格式为：
                    分词原句|分词1,分词2,...
                举例：
                    今天是个好日子|今天,是个,好,日子
                    这个手机真不错|这个,手机,真,不错
        """

        file_result = []
        for sentence in all_words.keys():
                file_result.append("%s|%s\n" % (sentence, ','.join(all_words[sentence])))
        write_to_file("contents.csv", file_result)
        print "write to contents.csv done"


def filt_all_word_set(all_words):
        """
            把全部的分词内容，过滤成每个词仅出现一次的集合
            Args:
                all_words: 一个字典类型的数据。key是需要分词的句子，value是分词
                    结果组成的一个list
                    举例：{
                    "今天是个好日子":["今天", "是个", "好", "日子"],
                    "这个手机真不错":["这个", "手机", "真", "不错"],
                    "我今天买手机":["我","今天","买","手机"]
                    }
            Returns:
                all_words_set:在all_words中出现的所有词、每个词仅出现一遍
                    举例:
                        ("今天", "是个", "好", "日子", "这个", "手机",
                            "真", "不错", "我","买")

        """
        global all_words_set
        all_words_set = set()
        for words in all_words.values():
            all_words_set = all_words_set | set(words)
        return all_words_set


def read_words_dictionary(dictionary_file, all_words_set):
        """
            从词典文件中读取出全部词，并过滤出在所有评论中出现过的词
            Args:
                dictionary_file : 字典文件名
                    文件内内容为每行一个词
                all_words_set : 一个集合，集合中包括了all_words_set中用到的词
            Returns:
                dictionary_words : 所有词典中的词构成的一个集合
                used_dicitionary_words : 所有词中用到的词典
        """
        dictionary_words = set()
        for line in open(dictionary_file):
            dictionary_words.add(line.decode('utf8')[:-1])
            #print chardet.detect(str(line).encode('utf8'))['encoding']
        used_dictionary_words = dictionary_words & all_words_set
        print "%s中使用到的词%d个" % (dictionary_file, len(used_dictionary_words))
        #for word in dictionary_words:
            #print word
        return dictionary_words, used_dictionary_words



def count_pmi_of_all_words_v2(all_words_set, known_dictionary, devided_passages):
        """
            计算两组词中的PMI值(第二版，加速过的)
            PMI根据两组词在一组文本中出现的频率特征进行计算
            Args:
                all_words_set : 所有出现过的词的集合
                known_dictionary : 需要计算的词典词的集合
                devided_passages : 分词过后的句子列表
                    举例:
                        [
                            ["今天", "是个", "好", "日子"],
                            ["这个", "手机", "真", "不错"],
                            ["我","今天","买","手机"]
                        ]
            Returns:
                total_pmi : all_words_set中的每一个词对应的PMI值
                    举例:
                        {
                            "今天": 27.6,
                            "买":3.8,
                            “手机":7.7
                        }

        """
        sentence_count = len(devided_passages)
        word_passage = {}
        word_show_probility_list = {}
        for word in all_words_set:
            for devided_passage in devided_passages:
                if word in devided_passage:
                    if word not in word_passage:
                        word_passage[word] = []
                    word_passage[word].append(devided_passage)
            word_show_probility_list[word] = len(word_passage[word]) / sentence_count



        dict_word_probility_list = {}
        for dict_word in known_dictionary:
            show_count = 0
            for devided_passage in devided_passages:
                if dict_word in devided_passage:
                    show_count += 1
            dict_word_probility_list[dict_word] = show_count / sentence_count


        all_pmi = {}
        for word in all_words_set:
            for dict_word in known_dictionary:
                match_count = 0
                for sentence_word_list in word_passage[word]:
                    if dict_word in sentence_word_list:
                        #print 'match'
                        match_count += 1
                probability_match = match_count / sentence_count
                probability_word = word_show_probility_list.get(word, 0)
                probability_dict_word = dict_word_probility_list.get(dict_word, 0)
                #if probability_match > 0:
                    #print "%s 和 %s 同时出现的概率为 %f" %(word, positive_word, probability)
                if word not in all_pmi:
                    all_pmi[word] = {}
                #print "word:%f, dict_word:%f, match:%f"%(probability_word, probability_dict_word, probability_match)
                if probability_dict_word * probability_word * probability_match == 0.0:
                    pmi = 0
                else:
                    pmi = math.log(probability_match / (probability_word * probability_dict_word), 2)
                    #print "%s, %s PMI = %f" % (word, dict_word, pmi)
                all_pmi[word][dict_word] = pmi
        total_pmi = {}
        for word in all_pmi.keys():
            total_pmi_for_this_word = 0.0
            for pmi in all_pmi[word].values():
                total_pmi_for_this_word += pmi
            #print "%s 词典pmi得分 %f" %(word, total_pmi_for_this_word)
            total_pmi[word] = total_pmi_for_this_word
        return total_pmi


def count_pmi_of_all_words(all_words_set, known_dictionary, devided_passages):
        """
            计算两组词中的PMI值(第一版)
            PMI根据两组词在一组文本中出现的频率特征进行计算
            Args:
                all_words_set : 所有出现过的词的集合
                known_dictionary : 需要计算的词典词的集合
                devided_passages : 分词过后的句子列表
                    举例:
                        [
                            ["今天", "是个", "好", "日子"],
                            ["这个", "手机", "真", "不错"],
                            ["我","今天","买","手机"]
                        ]
            Returns:
                total_pmi : all_words_set中的每一个词对应的PMI值
                    举例:
                        {
                            "今天": 27.6,
                            "买":3.8,
                            “手机":7.7
                        }

        """

        sentence_count = len(devided_passages)
        all_pmi = {}
        for word in all_words_set:
            for dict_word in known_dictionary:
                match_count = 0
                word_show_count = 0
                dict_word_show_count = 0
                for sentence_word_list in devided_passages:
                    if word in sentence_word_list:
                        word_show_count += 1
                    if dict_word in sentence_word_list:
                        dict_word_show_count += 1
                    #去掉注释可以看到匹配过程
                    #print word,positive_word,json.dumps(sentence_word_list, encoding="UTF-8", ensure_ascii=False)
                    if word in sentence_word_list and dict_word in sentence_word_list:
                        #print 'match'
                        match_count += 1
                probability_match = match_count / sentence_count
                probability_word = word_show_count / sentence_count
                probability_dict_word = dict_word_show_count / sentence_count
                #if probability_match > 0:
                    #print "%s 和 %s 同时出现的概率为 %f" %(word, positive_word, probability)
                if word not in all_pmi:
                    all_pmi[word] = {}
                #print "word:%f, dict_word:%f, match:%f"%(probability_word, probability_dict_word, probability_match)
                if probability_dict_word * probability_word * probability_match == 0.0:
                    pmi = 0
                else:
                    pmi = math.log(probability_match /(probability_word * probability_dict_word), 2)
                    #print "%s, %s PMI = %f" % (word, dict_word, pmi)
                all_pmi[word][dict_word] = pmi
        total_pmi = {}
        for word in all_pmi.keys():
            total_pmi_for_this_word = 0.0
            for pmi in all_pmi[word].values():
                total_pmi_for_this_word += pmi
            #print "%s 词典pmi得分 %f" %(word, total_pmi_for_this_word)
            total_pmi[word] = total_pmi_for_this_word
        return total_pmi


def count_total_pmi(total_positive_pmi, total_negative_pmi):
        """
            根据两种PMI值，计算总的PMI值
            Args:
                total_positive_pmi : 词与积极情感词的对应关系
                total_negative_pmi : 词与消极情感词的对应关系
            Returns:
                all_word_total_pmi : 词的PMI值
        """
        all_word_total_pmi = {}
        for word in all_words_set:
            total_pmi = total_positive_pmi[word] - total_negative_pmi[word]
            all_word_total_pmi[word] = total_pmi
            print "%s 的PMI 总和 %f" % (word, total_pmi)
        return all_word_total_pmi


def write_total_pmi_to_file(all_word_total_pmi):
        """
            把所有词的PMI值写到文件中。留着后续使用
        """
        file_result = []
        for word in all_word_total_pmi.keys():
            file_result.append("%s|%f\n" % (word, all_word_total_pmi[word]))
            print "%s 的PMI 总和 %f" % (word, all_word_total_pmi[word])
        write_to_file("total_pmi.csv", file_result)
        print "write to total_pmi.csv done"



def get_tag_by_jieba_keyword(all_words, all_words_total_pmi, tag_file):
        """
            根据语句及所有词的PMI值进行分析，利用jieba提取关键字的方法
            过滤出5个关键词,并将5个关键词对应的PMI数据导出成matlab可读的数据文件

            如果提供了tag文件，同时根据文件内的tag信息生成对应的tag文件
            Args:
                all_words: 一个字典类型的数据。key是需要分词的句子，value是分词
                    结果组成的一个list
                    举例：{
                    "今天是个好日子":["今天", "是个", "好", "日子"],
                    "这个手机真不错":["这个", "手机", "真", "不错"],
                    "我今天买手机":["我","今天","买","手机"]
                    }
                all_wors_total_pmi : 所有词的PMI值
                tag_file : 针对每一个语句打过tag的文件名
                            注意，文件内的语句就是第一步抓取的结果
                    举例:
                        文件名: tag_list.txt
                        文件内容 :
                            这手机是假的|0
                            这手机真不错|1
            Returns:
                输出sentences_pmi_mat.txt文件，文件格式:
                    3.33 4.33 8.99 1.83 8.42
                    3.33 4.33 8.99 1.83 8.42
                    3.33 4.33 8.99 1.83 8.42
                可以直接在matlab中利用load('sentences_pmi_mat.txt')导入

                输出sentences_tag_mat.txt文件，文件格式:
                    1
                    0
                    1
                    1
        """
        matlab_file_content = []
        matlab_tag_content = []
        tag_dict = {}
        if tag_file:
            for line in open(tag_file):
                sent = line[:-1].split('|')[0]
                tag = line[:-1].split('|')[1]
                tag_dict[sent] = tag

        for sent in all_words.keys():
            tags = jieba.analyse.extract_tags(sent, 5)
            pmi_list = []
            for tag in tags:
                pmi_list.append(all_words_total_pmi.get(tag, 0))
            while len(pmi_list) < 5 :
                pmi_list.append(0)
            print '%s|%s|%s' % (sent, ','.join(tags), ','.join([str(item) for item in pmi_list]))
            matlab_file_content.append("%s\n" % (','.join([str(item) for item in pmi_list])))
            if tag_file:
                matlab_tag_content.append('%s\n' % (tag_dict[sent]))

        write_to_file("sentences_pmi_mat.txt", matlab_file_content)
        if tag_file:
            write_to_file("sentences_tag_mat.txt", matlab_tag_content)




def main():
        solve_encode()
        get_comments_from_jd()
        #init_devide_sentence_env()
        #all_words = fetch_all_words_from_yu_yin_yun("contents.txt")
        all_words = fetch_all_words_from_jieba("contents.txt")
        write_devide_sentence_and_content_to_file(all_words)
        all_words_set = filt_all_word_set(all_words)
        all_positive_words, used_positive_words = read_words_dictionary("positive_words.txt", all_words_set)
        all_negative_words, used_negative_words = read_words_dictionary("negative_words.txt", all_words_set)
        positive_pmi = count_pmi_of_all_words_v2(all_words_set, used_positive_words, all_words.values())
        negative_pmi = count_pmi_of_all_words_v2(all_words_set, used_negative_words, all_words.values())
        #positive_pmi = count_pmi_of_all_words(all_words_set, all_positive_words, all_words.values())
        #negative_pmi = count_pmi_of_all_words(all_words_set, all_negative_words, all_words.values())
        all_words_total_pmi = count_total_pmi(positive_pmi, negative_pmi)
        write_total_pmi_to_file(all_words_total_pmi)

        # 打好tag，存好文件，可以使用上面的这个，会生成matlab中tag的文件
        #get_tag_by_jieba_keyword(all_words, all_words_total_pmi, "tag_list.txt")
        get_tag_by_jieba_keyword(all_words, all_words_total_pmi, None)


if __name__ == '__main__':
        main()
