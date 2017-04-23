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


def fetch_all_words_from_yu_yin_yun():
        global all_words
        all_words = {}
        for line in open("contents.txt"):
                request_data = {
                    "api_key": "i1o4P9M192j2l7y1U1I1lrhhyyeAaZrmTqdXhXsj",
                    "text": unicode(line),
                    "pattern": "ws",
                    "format": "json"}

                result = requests.post(url_get_base, data=request_data).content
                content = result.strip()
                js = json.loads(content)
                devided_words = []
                for sent in js[0]:
                        for data in sent:
                                devided_words.append(data['cont'])
                                #devided_words = "%s,%s" % (
                                    #devided_words, data['cont'])
                all_words[line[:-1]] = devided_words


def write_devide_sentence_and_content_to_file():
        file_result = []
        for sentence in all_words.keys():
                file_result.append("%s|%s\n" % (sentence, ','.join(all_words[sentence])))
        write_to_file("contents.csv", file_result)
        print "write to contents.csv done"


def filt_all_word_set():
        global all_words_set
        all_words_set = set()
        for words in all_words.values():
            for word in words:
                all_words_set.add(word)


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
        # 去掉注释可以输出数据的内容
        #for word in all_positive_words:
            #print word
        #for word in all_negative_words:
            #print word



def count_positive_pmi_of_all_words():
        global positive_pmi
        positive_pmi = {}
        for word in all_words_set:
            for positive_word in all_positive_words:
                sentence_count = len(all_words)
                match_count = 0
                word_show_count = 0
                positive_count = 0
                for sentence_word_list in all_words.values():
                    if word in sentence_word_list:
                        word_show_count += 1
                    if positive_word in sentence_word_list:
                        positive_count += 1
                    #去掉注释可以看到匹配过程
                    #print word,positive_word,json.dumps(sentence_word_list, encoding="UTF-8", ensure_ascii=False)
                    if word in sentence_word_list and positive_word in sentence_word_list:
                        #print 'match'
                        match_count += 1
                probability_match = match_count / sentence_count
                probability_word = word_show_count / sentence_count
                probability_positive = positive_count / sentence_count
                #if probability_match > 0:
                    #print "%s 和 %s 同时出现的概率为 %f" %(word, positive_word, probability)
                if word not in positive_pmi:
                    positive_pmi[word] = {}
                #print "word:%f, positive:%f, match:%f"%(probability_word, probability_positive, probability_match)
                if probability_positive * probability_word * probability_match == 0.0:
                    pmi_word_positive = 0
                else:
                    pmi_word_positive = math.log(probability_match /(probability_word * probability_positive), 2)
                    print "%s, %s PMI = %f" % (word, positive_word, pmi_word_positive)
                positive_pmi[word][positive_word] = pmi_word_positive
        global total_positive_pmi
        total_positive_pmi = {}
        for word in positive_pmi.keys():
            total_pmi = 0.0
            for pmi in positive_pmi[word].values():
                total_pmi += pmi
            #print "%s 积极情感词pmi得分 %f" %(word, total_pmi)
            total_positive_pmi[word] = total_pmi



def count_negative_pmi_of_all_words():
        global negative_pmi
        negative_pmi = {}
        for word in all_words_set:
            for negative_word in all_negative_words:
                sentence_count = len(all_words)
                match_count = 0
                word_show_count = 0
                negative_count = 0
                for sentence_word_list in all_words.values():
                    if word in sentence_word_list:
                        word_show_count += 1
                    if negative_word in sentence_word_list:
                        negative_count += 1
                    #去掉注释可以看到匹配过程
                    #print word,negative_word,json.dumps(sentence_word_list, encoding="UTF-8", ensure_ascii=False)
                    if word in sentence_word_list and negative_word in sentence_word_list:
                        #print 'match'
                        match_count += 1
                probability_match = match_count / sentence_count
                probability_word = word_show_count / sentence_count
                probability_negative = negative_count / sentence_count
                #if probability_match > 0:
                    #print "%s 和 %s 同时出现的概率为 %f" %(word, negative_word, probability)
                if word not in negative_pmi:
                    negative_pmi[word] = {}
                #print "word:%f, negative:%f, match:%f"%(probability_word, probability_negative, probability_match)
                if probability_negative * probability_word * probability_match == 0.0:
                    pmi_word_negative = 0
                else:
                    pmi_word_negative = math.log(probability_match /(probability_word * probability_negative), 2)
                    print "%s, %s PMI = %f" % (word, negative_word, pmi_word_negative)
                negative_pmi[word][negative_word] = pmi_word_negative
        global total_negative_pmi
        total_negative_pmi = {}
        for word in negative_pmi.keys():
            total_pmi = 0.0
            for pmi in negative_pmi[word].values():
                total_pmi -= pmi
            #print "%s 消极情感词pmi得分 %f" %(word, total_pmi)
            total_negative_pmi[word] = total_pmi



def write_total_pmi_to_file():
    file_result = []
    for word in all_words_set:
        total_pmi = total_positive_pmi[word] + total_negative_pmi[word]
        file_result.append("%s|%f\n" % (word, total_pmi))
        print "%s 的PMI 总和 %f" % (word, total_pmi)
    write_to_file("total_pmi.csv", file_result)
    print "write to total_pmi.csv done"



def main():
        solve_encode()
        get_comments_from_jd()
        init_devide_sentence_env()
        fetch_all_words_from_yu_yin_yun()
        write_devide_sentence_and_content_to_file()
        filt_all_word_set()
        read_all_positive_and_negative_words()
        count_positive_pmi_of_all_words()
        count_negative_pmi_of_all_words()
        write_total_pmi_to_file()


if __name__ == '__main__':
        main()
