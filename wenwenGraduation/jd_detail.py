#!/usr/bin/env python
#coding:utf-8
#Author:yunya  Created: 2016/12/6
#copy from http://www.yunya.pw/?post=18
import urllib2, re, random, time, sys
import pandas as pd


def main():
    l_cmt, l_time, l_like, l_score, l_reply, l_level, l_prov, l_nn, l_client = \
        [], [], [], [], [], [], [], [], []
    pid = sys.argv[1]
    pages = int(sys.argv[2])

    for page in range(pages):  #12.13 edit
        print "Page %i ..." % (page + 1)
        url = "https://sclub.jd.com/comment/productPageComments.action?productId=" +\
            pid + "&score=0&sortType=3&page=" + str(page) + \
            "&pageSize=10&callback=fetchJSON_comment98vv37464"

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
        time.sleep(random.randint(5, 10) / 10.0)

    df = pd.DataFrame({"cmt":l_cmt,
                       "time":l_time,
                       "like":l_like,
                       "score":l_score,
                       "reply":l_reply,
                       "level":l_level,
                       "prov":l_prov,
                       "nn":l_nn,
                       "client":l_client})
    df.to_csv('file.csv', index = False)
    print "done.."

if __name__ == "__main__":
    main()
