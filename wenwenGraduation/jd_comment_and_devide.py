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
from pprint import pprint


def solve_encode():
        reload(sys)
        sys.setdefaultencoding("utf-8")

def get_comments_from_jd():
        l_cmt, l_time, l_like, l_score, l_reply, l_level, l_prov, l_nn, l_client = [
                ], [], [], [], [], [], [], [], []
        result_lines = []
        pid = sys.argv[1]
        pages = int(sys.argv[2])

        for page in range(pages):  # 12.13 edit
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
        global api_key
        global format
        global pattern
        global url_get_base
        api_key = 'i1o4P9M192j2l7y1U1I1lrhhyyeAaZrmTqdXhXsj'
        format = 'json'
        pattern = 'dp'
        url_get_base = "http://ltpapi.voicecloud.cn/analysis/"


def write_to_file(file_name, lines):
        f = codecs.open(file_name, "w", "utf-8")
        for line in lines:
                f.write(line)
        f.close()


def fetch_all_words_from_yu_yin_yun(file_name):
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
        all_words = {}
        for line in open(file_name):
            seg_list = list(jieba.cut(line, cut_all=True))
            all_words[line[:-1]] = seg_list
        return all_words

def write_devide_sentence_and_content_to_file(all_words):
        file_result = []
        for sentence in all_words.keys():
                file_result.append("%s|%s\n" % (sentence, ','.join(all_words[sentence])))
        write_to_file("contents.csv", file_result)
        print "write to contents.csv done"


def filt_all_word_set(all_words):
        global all_words_set
        all_words_set = set()
        for words in all_words.values():
            all_words_set = all_words_set | set(words)


def read_all_positive_and_negative_words():
        global all_positive_words
        global all_negative_words
        all_positive_words = set()
        all_negative_words = set()
        for line in open("positive_words.txt"):
            all_positive_words.add(line.decode('utf8')[:-1])
            #print chardet.detect(str(line).encode('utf8'))['encoding']
        for line in open("negative_words.txt"):
            all_negative_words.add(line.decode('utf8')[:-1])
        global used_positive_words
        global used_negative_words
        used_positive_words = all_positive_words & all_words_set
        used_negative_words = all_negative_words & all_words_set
        print "使用到的积极词%d个" % len(used_positive_words)
        print "使用到的消极词%d个" % len(used_negative_words)
        # 去掉注释可以输出数据的内容
        #for word in all_positive_words:
            #print word
        #for word in all_negative_words:
            #print word

def count_pmi_of_all_words_v2(all_words_set, known_dictionary, devided_passages):
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
        global all_word_total_pmi
        all_word_total_pmi = {}
        for word in all_words_set:
            total_pmi = total_positive_pmi[word] - total_negative_pmi[word]
            all_word_total_pmi[word] = total_pmi
            print "%s 的PMI 总和 %f" % (word, total_pmi)


def write_total_pmi_to_file():
    file_result = []
    for word in all_word_total_pmi.keys():
        file_result.append("%s|%f\n" % (word, all_word_total_pmi[word]))
        print "%s 的PMI 总和 %f" % (word, all_word_total_pmi[word])
    write_to_file("total_pmi.csv", file_result)
    print "write to total_pmi.csv done"



def get_tag_by_jieba_keyword(sents):
    for sent in sents:
        tags = jieba.analyse.extract_tags(sent, 5)
        pmi_list = []
        for tag in tags:
            pmi_list.append(all_word_total_pmi.get(tag, 0))
        print '%s|%s|%s' % (sent, ','.join(tags), ','.join([str(item) for item in pmi_list]))

def main():
        solve_encode()
        get_comments_from_jd()
        #init_devide_sentence_env()
        #all_words = fetch_all_words_from_yu_yin_yun("contents.txt")
        all_words = fetch_all_words_from_jieba("contents.txt")
        write_devide_sentence_and_content_to_file(all_words)
        filt_all_word_set(all_words)
        read_all_positive_and_negative_words()
        positive_pmi = count_pmi_of_all_words_v2(all_words_set, used_positive_words, all_words.values())
        negative_pmi = count_pmi_of_all_words_v2(all_words_set, used_negative_words, all_words.values())
        #positive_pmi = count_pmi_of_all_words(all_words_set, all_positive_words, all_words.values())
        #negative_pmi = count_pmi_of_all_words(all_words_set, all_negative_words, all_words.values())
        count_total_pmi(positive_pmi, negative_pmi)
        write_total_pmi_to_file()
        get_tag_by_jieba_keyword(all_words.keys())


if __name__ == '__main__':
        main()
