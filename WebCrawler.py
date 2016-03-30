# coding=utf-8
import urllib2, time, gzip
import StringIO, unicodedata, json
import MySQLdb, datetime, uuid
import sys
import logging

LOG_FILENAME = "log.txt"
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)
logging.debug(
    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ":Start *************************************************")

reload(sys)
sys.setdefaultencoding("utf-8")


def reqt(url):
    req = urllib2.Request(url + "&t=" + str(int(round(time.time() * 1000))))
    req.add_header("Accept-Encoding", "gzip, deflate, sdch")
    req.add_header("Accept-Language", "zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4,ko;q=0.2,zh-TW;q=0.2")
    req.add_header("Cache-Control", "no-cache")
    req.add_header("User-Agent",
                   "")
    req.add_header("Accept", "*/*")
    req.add_header("Connection", "keep-alive")
    req.add_header("Host", "host.com")
    req.add_header("Referer", "http://host.com")
    res = urllib2.urlopen(req).read()
    res = gzip.GzipFile(fileobj=StringIO.StringIO(res)).read()
    return res


def parseJSON(res, var=None):
    return json.loads(res.replace(var, '').replace('(', '').replace(')', ''))


def catList():
    res = parseJSON(
        reqt("http://host.com/somecats.htm"),
        var="subscribeNav")
    cats = []
    for cat in res['cats']:
        cats.append(cat)
        logging.debug(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "-CAT-:" + str(cat['catName']))
    return cats


def channelList(keys=['chlid', 'chlname', 'icon']):
    res = parseJSON(reqt("http://host.com/somechannel.htm"), var="allManageMedia")
    channels = []
    for cat in res['cats']:
        for channel in cat['channels']:
            chnlDict = {k: v for k, v in channel.iteritems() if any(k in s for s in keys)}
            chnlDict['catId'] = cat['catId']
            chnlDict['catName'] = str(cat['catName'])
            logging.debug(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "-CHANNEL-:" + chnlDict['catName'])
            channels.append(chnlDict)
    return channels


def newsList(chlid, keys=['id', 'title', 'thumbnails']):
    unparsed = parseJSON(
        reqt("http://host.com/somenews.htm?chlid=" + chlid)
        , var="createHtml")
    newsList = []
    for news in unparsed['newslist']:
        newsList.append({k: v for k, v in news.iteritems() if any(k in s for s in keys)})

    return newsList


def newsHtml(aid):
    unparsed = parseJSON(
        reqt("http://host.com/somecontent?id=" + aid),
        var='showArticle')
    parsed = ''

    if isinstance(unparsed['data'], list):
        try:
            for content in unparsed['data'][0]['content']:
                if content['type'] == 'cnt_article':
                    parsed += '<p>' + content['desc'] + '</p>'
                elif content['type'] == 'img_url':
                    parsed += '<p><img src="' + content['img_url'] + '" /></p>'
        except Exception, e:
            pass
    return parsed


def main():
    db = MySQLdb.connect(host="",
                         user="",
                         passwd="",
                         db="")

    db.set_character_set("utf8")

    sql = ""
    newslink = 'http://host.com/news.htm?id='
    chllink = 'http://host.com/child.htm?chlid='

    cur = db.cursor()

    cats = catList()
    for cat in cats:
        r = cur.execute(xsql)
        db.commit()

    try:
        channels = channelList()
        for channel in channels:
            sectionId = uuid.uuid1()
            chlname = 'XXX' + str(channel['chlname'])
            r = cur.execute(xsql)

            db.commit()

            if r == 0:
                cur.execute(xsql)
                result = cur.fetchall()
                if len(result) > 0:
                    sectionId = result[0][0];
                else:
                    continue

            newses = newsList(channel['chlid'])
            for news in newses:
                link = newslink + news['id']
                newscontent = newsHtml(news['id'])
                if len(newscontent) == 0:
                    continue

                cur.execute(sql, paras)
                db.commit()

                logging.debug(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "-LINK-:" + link)
    except Exception, e:
        # pass
        print(e)


if __name__ == '__main__':
    main()
