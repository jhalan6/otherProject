#!/usr/bin/env python
# coding:utf-8
# Author:yunya  Created: 2016/12/6
# copy from http://www.yunya.pw/?post=18
import urllib2
import re
import json
import random
import time
import sys
import codecs
import requests
import pandas as pd


def get_comments_from_jd():
    l_cmt, l_time, l_like, l_score, l_reply, l_level, l_prov, l_nn, l_client = \
        [], [], [], [], [], [], [], [], []
    result_lines = []
    pid = sys.argv[1]
    pages = int(sys.argv[2])

    for page in range(pages):  #12.13 edit
        print "Page %i ..." % (page + 1)
        url = "https://sclub.jd.com/comment/productPageComments.action?productId=" +\
            pid + "&score=0&sortType=3&page=" + str(page) + \
            "&pageSize=10&callback=fetchJSON_comment98vv37464"

        print url
        ws1 = urllib2.urlopen(url).read()
        groups = re.findall('''\{"id":\d+,.*?,"content":"((?:(?!<\/div>).|\n)*?)",.*?,"referenceTime":"(.*?)",.*?,"replyCount":(\d+),"score":(\d+),"status":\d,"title":"","usefulVoteCount":(\d+),.*?,"userLevelId":"(.*?)","userProvince":"(.*?)",.*?,"nickname":"(.*?)","userClient":(\d+),''', ws1)
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
            result_lines.append(("%s\n" % g[0]).decode('gbk', 'ignore').encode('utf-8'))
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
    df.to_csv('file.csv', index = False)
    print "grep from jd done.."
    write_to_file("contents.txt", result_lines)
    print "write contents.txt done"


def solve_encode():
    reload(sys)
    sys.setdefaultencoding("utf-8")


def devide_sentence_env():
    global api_key
    global format
    global pattern
    global url_get_base
    api_key = 'i1o4P9M192j2l7y1U1I1lrhhyyeAaZrmTqdXhXsj'
    format = 'json'
    pattern = 'dp'
    url_get_base = "http://ltpapi.voicecloud.cn/analysis/?"


def write_to_file(file_name, lines):
    f = codecs.open(file_name, "w", "utf-8")
    for line in lines:
        f.write(line)
    f.close()


def write_devide_sentence_and_content_to_file():
    file_result = []
    for line in open("contents.txt"):
        url = "%sapi_key=%s&text=%s&format=%s&pattern=%s" % \
            (url_get_base, api_key, line, format, pattern)
        result = requests.get(url).content
        content = result.strip()
        js = json.loads(content)
        devided_words = ""
        for data in js[0][0]:
            devided_words = "%s,%s" % (devided_words, data['cont'])
        file_result.append("%s|%s\n" % (line, devided_words))
    write_to_file("contents.csv", file_result)
    print "write to contents.csv done"


def main():
    solve_encode()
    get_comments_from_jd()
    devide_sentence_env()
    write_devide_sentence_and_content_to_file()


if __name__ == '__main__':
    main()
