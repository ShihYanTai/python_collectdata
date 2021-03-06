from zeczecselenium import adult
import json, datetime, time
from urllib import parse
import requests
from bs4 import BeautifulSoup
import re


# zeczec網頁資料

url = 'https://www.zeczec.com/'

headers = {
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31',

}

def getMainLinks(count):

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


    fp = open(f"zeczecList{count}.json", "w", encoding ="utf-8")
    fp.write( json.dumps(listData, ensure_ascii=False) )
    fp.close()

def getSubLinks(count):

    listContent = []

    fp = open(f"zeczecList{count}.json", "r", encoding="utf-8")
    strJson = fp.read()
    listResult = json.loads(strJson)

    # 蒐集各案件的資料 取得先前所有的連結 進入案件取資料

    for i in range( len(listResult)):
        print(listResult[i]['link'])
        response = requests.get(listResult[i]['link'], headers = headers)

        soup = BeautifulSoup(response.text, "lxml")

        drecord = datetime.datetime.now().strftime(f'%Y/%m/%d %H:%M:%S')

        # 如果有進入 詢問是否滿十八歲進入selenium 登入後跳出重新登入

        if soup.select_one('p[class="red b"]') is not None:

            listContent.append( adult(listResult[i]['link'] ) )

            continue

        a_title = soup.select_one('h2[class="f4 mt2 mb1"]')

        # 篩選募資區域

        if soup.select_one('div[class="f6 gray"] span[class="b"]') != None:
            a_zone = soup.select_one('div[class="f6 gray"] span[class="b"]').text
        else:
            a_zone = soup.select_one('div[class="f6 gray"] span[class="b"]')

        # 篩選募資類別

        a_method = [method.text for method in soup.select('a[class="underline dark-gray b dib"]')]

        a_donate = int(''.join(re.findall(r'\d+', soup.select_one('div[class="f3 b js-sum-raised nowrap"]').text)))

        a_target = soup.select_one('div[class="f7"]')

        # 如果目標金額是一直有而沒有金額 先判斷資料是否不同

        if ''.join(re.findall(r'\d+', a_target.text)) == []:
            b_target = re.findall(r'[\u4e00-\u9fa5]+', a_target.text)[0]
        else:
            b_target = ''.join(re.findall(r'\d', a_target.text))

        # 由目標金額篩選完後算出達成率

        if b_target == '':

            b_target = None

            arrivepercent = None

        else:
            b_target = int(b_target)

            arrivepercent = a_donate / b_target


        # 如果是預購就帶入即將開始

        if soup.select_one('span[class="js-backers-count"]') != None:
            n_sponsor = int(soup.select_one('span[class="js-backers-count"]').text)
        else:
            n_sponsor = re.findall(r'[\u4e00-\u9fa5]+', soup.select_one('div[class="mb1 f7 js-preheating"] span[class="mr2 b"]').text)[0]

        t_remaining = soup.select_one('span[class="js-time-left"]')

        # 如果沒有剩餘時間 就加入None

        if t_remaining == None:
            t_remaining = None

        # 剩餘時間轉成分鐘

        else:
            if '天' in re.findall(r'[\u4e00-\u9fa5]+', t_remaining.text)[0]:
                t_remaining = int(''.join(re.findall(r'\d+', t_remaining.text)[0])) * 24 * 60
            elif '小時' in re.findall(r'[\u4e00-\u9fa5]+', t_remaining.text)[0]:
                t_remaining = int(''.join(re.findall(r'\d+', t_remaining.text)[0])) * 60
            else:
                t_remaining = int(''.join(re.findall(r'\d+', t_remaining.text)[0]))

        # 先dict 開始日與截止日期

        dictDuration = {"begin": "", "end": ""}
        a_schedule = soup.select_one('div[class="mb2 f7"]')

        # 正則表達式篩選兩個goup

        matchDuration = re.search('(\d{4}\/\d{2}\/\d{2}\s\d{2}:\d{2})(\s–\s(\d{4}\/\d{2}\/\d{2}\s\d{2}:\d{2}))?', a_schedule.get_text())

        # list 分別加入 dict

        dictDuration['begin'] = matchDuration[1]
        if matchDuration[3] != None:
            dictDuration['end'] = matchDuration[3]

            # 由爬蟲當下時間與結束時間做比較後，篩選是否完成募資

            if dictDuration['end'] > drecord:
                if arrivepercent > 1:
                    whether = 1
                else:
                    whether = 0
            else:
                if arrivepercent > 1:
                    whether = 1
                else:
                    whether = 0

        else:
            dictDuration['end'] = None
            whether = None

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

        listContent.append({"downloadrecord": drecord,
                            "案件名稱": a_title.text,
                            "募資區域": a_zone,
                            "募資方式": a_method[0],
                            "專案類別": a_method[1],
                            "目前金額": a_donate,
                            "目標金額": b_target,
                            "贊助人數": n_sponsor,
                            "剩餘時間": t_remaining,
                            "開始時程": dictDuration['begin'],
                            "結束時程": dictDuration['end'],
                            QAname[0]: QAnumber[0],
                            QAname[1]: QAnumber[1],
                            QAname[2]: QAnumber[2],
                            "達成率": arrivepercent,
                            "是否完成募資": whether
                            })

        fp = open(f"zeczecdata{count}.json", "w", encoding="utf-8")
        fp.write(json.dumps(listContent, ensure_ascii=False))
        fp.close()
        time.sleep(2)

if __name__ == "__main__":

    while True:
        
        count = 0
        
        getMainLinks(count)
        getSubLinks(count)
        
        count += 1
        
        continue
