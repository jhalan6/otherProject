# -*- coding:utf8 -*-
import urllib2, json, sys, requests
if __name__ == '__main__':
    url_get_base = "http://ltpapi.voicecloud.cn/analysis/?"
    api_key = 'i1o4P9M192j2l7y1U1I1lrhhyyeAaZrmTqdXhXsj'
    text = '今天是个好日子'
    format = 'json'
    pattern = 'dp'
    result = urllib2.urlopen( "%sapi_key=%s&text=%s&format=%s&pattern=%s" % \
                             (url_get_base, api_key, text, format, pattern))
    content = result.read().strip()
    #print content
    js = json.loads(content)
    #for data in js[0][0]:
        #print 'id:%s\trelate:%s\tpos:%s\tparent:%s\tcont:%s' % (data['id'], data['relate'], data['pos'], data['parent'], data['cont'])
    #for data in js[0][0]:
        #print '%s|%s|%s|%s|%s' % (data['id'], data['relate'], data['pos'], data['parent'], data['cont'])



    query = sys.argv[1]
    for line in open(query):
        url_get_base = "http://ltpapi.voicecloud.cn/analysis/?"
        api_key = 'i1o4P9M192j2l7y1U1I1lrhhyyeAaZrmTqdXhXsj'
        format = 'json'
        pattern = 'dp'
        url = "%sapi_key=%s&text=%s&format=%s&pattern=%s" % \
            (url_get_base, api_key, line, format, pattern)
        result = requests.get(url).content
        #result = urllib2.urlopen(url)
        content = result.strip()
        #print content
        js = json.loads(content)
        for data in js[0][0]:
            print ('%s|%s|%s|%s|%s' % (data['id'], data['relate'], data['pos'], data['parent'], data['cont'])).encode('utf8')
        print '||||'
