from zeczecselenium import adult
import json, os, datetime, time
from datetime import timedelta
from urllib import parse
import requests
from bs4 import BeautifulSoup
import re

# 設定每天要要執行時間

nowtime = { inde : ii for inde, ii in enumerate(time.localtime())}

instantlytime = datetime.datetime(nowtime[0] , nowtime[1] , nowtime[2], nowtime[3], nowtime[4])

dayTime = datetime.datetime(nowtime[0], nowtime[1], nowtime[2], 0, 0, 0)

nighttime = datetime.datetime(nowtime[0], nowtime[1], nowtime[2], 12, 0, 0)

one = timedelta(days= 1)

# zeczec網頁資料

url = 'https://www.zeczec.com/'

headers = {
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31',

}

def getMainLinks(time):

    listData = []

    # 先設定第一頁搜尋各個連結
    pages = 1
    res = requests.get(url=url + f'categories?page={pages}', headers=headers)
    soup = BeautifulSoup(res.text, "lxml")
    a_elms = soup.select('a[class="button button-s dn dib-ns"]')

    # 得到最終頁數
    number = len(a_elms)
    pages = int(a_elms[number - 1].text)

    # 在每頁重複得到連結
    for page in range(1, pages + 1):
        res = requests.get(url=url + f'categories?page={page}', headers=headers)

        soup = BeautifulSoup(res.text, "lxml")
        a_elms = soup.select('div[class="mb4 w-100 w-25-l w-50-m"] a[class="db"]')

        for a in a_elms:
            listData.append({"title": a.text,
                             "link": 'https://www.zeczec.com' + parse.unquote(a.get('href'))
        })

    #寫入連結資料附上時間

    time = str(time).replace(":", '')
    time = time.replace(" ", '')
    time = time.replace("-", '')

    fp = open(f"zeczecList{time}.json", "w", encoding ="utf-8")
    fp.write( json.dumps(listData, ensure_ascii=False) )
    fp.close()

def getSubLinks(time):

    listContent = []

    fp = open("zeczecList.json", "r", encoding="utf-8")
    strJson = fp.read()
    listResult = json.loads(strJson)

    # 蒐集各案件的資料 取得先前所有的連結 進入案件取資料

    for i in range( len(listResult)):

        response = requests.get(listResult[i]['link'], headers = headers)

        soup = BeautifulSoup(response.text, "lxml")

        # 如果有進入 詢問是否滿十八歲進入selenium 登入後跳出重新登入

        if soup.select_one('p[class="red b"]') is not None:

            listContent.append( adult(listResult[i]['link'] ) )

            continue

        a_title = soup.select_one('h2[class="f4 mt2 mb1"]')

        a_donate = soup.select_one('div[class="f3 b js-sum-raised nowrap"]')

        a_target = soup.select_one('div[class="f7"]')

        # 如果目標金額是一直有而沒有金額 先判斷資料是否不同

        if ''.join(re.findall(r'\d+', a_target.text)) == []:
            b_target = re.findall(r'[\u4e00-\u9fa5]+', a_target.text)[0]
        else:
            b_target = ''.join(re.findall(r'\d', a_target.text))

        if b_target == '':
            b_target = None
        else:
            b_target = int(b_target)

        # 如果是預購就帶入即將開始

        if soup.select_one('span[class="js-backers-count"]') != None:
            n_sponsor = int(soup.select_one('span[class="js-backers-count"]').text)
        else:
            n_sponsor = re.findall(r'[\u4e00-\u9fa5]+', soup.select_one('div[class="mb1 f7 js-preheating"] span[class="mr2 b"]').text)[0]

        t_remaining = soup.select_one('span[class="js-time-left"]')

        # 如果沒有剩餘時間 就加入None

        if t_remaining == None:
            t_remaining = None
        else:
            t_remaining = t_remaining.text

        # 先dict 開始日與截止日期

        dictDuration = {"begin": "", "end": ""}
        a_schedule = soup.select_one('div[class="mb2 f7"]')

        # 正則表達式篩選兩個goup

        matchDuration = re.search('(\d{4}\/\d{2}\/\d{2}\s\d{2}:\d{2})(\s–\s(\d{4}\/\d{2}\/\d{2}\s\d{2}:\d{2}))?', a_schedule.get_text())

        # list 分別加入 dict

        dictDuration['begin'] = matchDuration[1]
        if matchDuration[3] != None:
            dictDuration['end'] = matchDuration[3]
        else:
            dictDuration['end'] = None

        # QA 有三個專案更新 常見問答 留言 及各自數量有些案子有缺後需補上各自缺少的 ，需先全部轉成int再加入dict

        divQAname = soup.select('a[class="b--transparent bb-l dib hover-b--dark-gray mr4 mt1 near-black pv3"] div[class="dib pv1"]')

        QAname = [j.text for j in divQAname]

        if len(divQAname) == 1:
            QAname.insert(0, '專案更新')
            QAname.append('常見問答')
        elif len(divQAname) < 3:
            QAname.insert(0, '專案更新')
        else:
            pass

        span = soup.select('span[class="f7 b ml3 gray"]')

        QAnumber = [int(i.text) for i in span]

        if len(QAnumber) == 1:
            QAnumber.insert(0, 0)
            QAnumber.append(0)
        elif len(QAnumber) < 3:
            QAnumber.insert(0, 0)
        else:
            pass

        listContent.append({"案件名稱": a_title.text,
                         "目前金額": int(''.join(re.findall(r'\d+', a_donate.text))),
                         "目標金額": b_target,
                         "贊助人數": n_sponsor,
                         "剩餘時間": t_remaining,
                         "開始時程": dictDuration['begin'],
                         "結束時程": dictDuration['end'],
                         QAname[0]: QAnumber[0],
                         QAname[1]: QAnumber[1],
                         QAname[2]: QAnumber[2]
                         })

        # 寫入資料附上時間

        time = str(time).replace(":", '')
        time = time.replace(" ", '')
        time = time.replace("-", '')

        fp = open(f"zeczecdata{time}.json", "w", encoding="utf-8")
        fp.write(json.dumps(listContent, ensure_ascii=False))
        fp.close()

if __name__ == "__main__":
    while True:
        # 在中午12點前執行程式
        if datetime.datetime.now() < nighttime:

            while datetime.datetime.now() < nighttime:
                time.sleep(1)

            getMainLinks(instantlytime)
            getSubLinks(instantlytime)

            tomorrow = dayTime + one
            while datetime.datetime.now() < tomorrow:
                time.sleep(1)

            getMainLinks(instantlytime)
            getSubLinks(instantlytime)

        # 在中午12點後執行程式
        else:

            tomorrow = dayTime + one
            while datetime.datetime.now() < tomorrow:
                time.sleep(1)

                while datetime.datetime.now() < dayTime:
                    time.sleep(1)

                getMainLinks(instantlytime)
                getSubLinks(instantlytime)

                while datetime.datetime.now() < nighttime:
                    time.sleep(1)

                getMainLinks(instantlytime)
                getSubLinks(instantlytime)
                continue
        continue
