# -*- coding:utf8 -*-
import json
import sys
import requests
import codecs


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


def write_to_file(lines):
    f = codecs.open("contents.csv", "w", "utf-8")
    for line in lines:
        f.write(line)
    f.close()


def main():
    query = sys.argv[1]
    file_result = []
    for line in open(query):
        url = "%sapi_key=%s&text=%s&format=%s&pattern=%s" % \
            (url_get_base, api_key, line, format, pattern)
        result = requests.get(url).content
        content = result.strip()
        js = json.loads(content)
        devided_words = ""
        for data in js[0][0]:
            devided_words = "%s,%s" % (devided_words, data['cont'])
        file_result.append("%s|%s\n" % (line, devided_words))
    write_to_file(file_result)


if __name__ == '__main__':
    solve_encode()
    devide_sentence_env()
    main()
