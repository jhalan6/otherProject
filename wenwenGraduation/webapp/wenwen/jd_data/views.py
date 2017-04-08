#coding:utf-8
from django.shortcuts import render

from django.http import HttpResponse
def index(request):
    return HttpResponse(u"文文你好～么么哒")


def comments(request):
    import urllib2, re, random, time, json, requests
    import pandas as pd
    pid = request.GET['pid']
    pages = int(request.GET['pages'])

    l_cmt, l_time, l_like, l_score, l_reply, l_level, l_prov, l_nn, l_client = \
        [], [], [], [], [], [], [], [], []

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

    return HttpResponse(u"done")
