import json, os, pprint, time
from urllib import parse
import requests
from bs4 import BeautifulSoup

listData = []

url = 'https://www.bookwormzz.com/zh/'

headers = {
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31'
}

def getMainLinks():
    response = requests.get(url, headers = headers)
    soup = BeautifulSoup(response.text, "lxml")
    a_elms = soup.select('a[data-ajax="false"]')
    for a in a_elms:
        listData.append({
            "title": a.text,
            "link": url + parse.unquote(a.get('href')) + '#book_toc'
        })

def getSubLinks():
    for i in range( len(listData)):
        if "sub" not in listData[i]:
            listData[i]['sub'] = []
        response = requests.get(listData[i]['link'], headers = headers)
        soup = BeautifulSoup(response.text, "lxml")
        a_elms = soup.select('div[data-theme="b"][data-content-theme="c"] a[rel="external"]')
        if len(a_elms) > 0:
            for a in a_elms:
                listData[i]['sub'].append({
                    "sub_title": a.text,
                    "sub_link": url + parse.unquote( a.get('href') )
                })
        else:
            continue

def saveJson():
    fp = open("jinyong.json", "w", encoding ="utf-8")
    fp.write( json.dumps(listData, ensure_ascii=False) )
    fp.close()

def writeTxt():
    listContent = []

    fp = open("jinyong.json", "r", encoding="utf-8")
    srtJson = fp.read()
    fp.close()

    folderPath = 'jinyong_txt'
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)

    listResult = json.loads(srtJson)

    for i in range(len(listResult)):
        for j in range(len(listResult[i]['sub'])):
            response = requests.get(listResult[i]['sub'][j]['sub_link'], headers = headers)
            soup = BeautifulSoup(response.text, "lxml")
            div = soup.select_one('div#html >div')
            strContent = div.text
            strContent = strContent.replace(" ","")
            strContent = strContent.replace("\r", "")
            strContent = strContent.replace("\n", "")
            strContent = strContent.replace("　", "")

            fileName = f"{listResult[i]['title']} {listResult[i]['sub'][j]['sub_title']}.txt"
            fp = open(f"{folderPath}/{fileName}", "w", encoding="utf-8")
            fp.write(strContent)
            fp.close()

            listContent.append(strContent)

    fp = open("train.json", "w", encoding="utf-8")
    fp.write(json.dumps(listContent, ensure_ascii=False) )
    fp.close()

if __name__ == '__main__':

    time1 = time.time()
    getMainLinks()
    getSubLinks()
    saveJson()
    writeTxt()
    print(f"[total] It takes {time.time() - time1} seconds.")