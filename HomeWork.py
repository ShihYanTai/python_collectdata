from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json, os, pprint, time
from urllib import parse
import re

options = webdriver.ChromeOptions()
options.add_argument('--sart-maximized')
options.add_argument('--incognito')
options.add_argument('--disaable-popup-blocking')
options.add_argument('enable-web-bluetooth-scanning')

driver = webdriver.Chrome(executable_path=r'C:\Users\yantaishih\PycharmProjects\jinyong\chromedriver.exe',options = options)
listData = []

url = 'https://www.gutenberg.org/browse/languages/zh'

def visit():
    driver.get(url)

def getMainLinks():
    a_elms = driver.find_elements(By.CSS_SELECTOR, 'li[class="pgdbetext"] a')
    for a in a_elms:
        title = a.get_attribute('innerText')

        title = title.replace(" ", "")
        title = title.replace("\r", "")
        title = title.replace("\n", "")
        title = title.replace("<", "")
        title = title.replace(">", "")
        title = title.replace("/", "")
        title = title.replace("\\", "")
        title = title.replace("*", "")
        title = title.replace("|", "")
        title = title.replace("\"", "")

        listData.append({
            "title": title,
            "link": parse.unquote(a.get_attribute('href'))
        })


def getSubLinks():
    for i in range( len(listData) ):
        if "sub" not in listData[i]:
            listData[i]['sub'] = []

        driver.get(listData[i]["link"])

        try:
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located(
                   ( By.CSS_SELECTOR, 'a[type="text/html"]')
                )
            )

            a_elms = driver.find_elements(By.CSS_SELECTOR, 'a[type="text/html"]')
            for a in a_elms:
                listData[i]["sub"].append({
                    "sub_title":listData[i]["title"],
                    "sub_link":parse.unquote( a.get_attribute("href") )
                })
        except TimeoutException as e:
            continue

def close():
    driver.quit()

def saveJson():
    fp = open("HomeWork.json", "w", encoding ="utf-8")
    fp.write( json.dumps(listData, ensure_ascii=False) )
    fp.close()

def writeTxt():
    listContent = []
    fp = open("HomeWork.json", "r",encoding="utf-8")
    strJson = fp.read()

    folderPath = 'HomeWork_txt'
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)

    listResult = json.loads(strJson)

    for i in range(len(listResult)):
        for j in range(len(listResult[i]['sub'])):
            driver.get( listResult[i]['sub'][j]['sub_link'])
            div = driver.find_element(By.CSS_SELECTOR, 'body')
            strContent = div.get_attribute('innerText')
            strContent = ''.join(re.findall('[\u4e00-\u9fa5]+', strContent))

            fileName = f"{listResult[i]['title']}.txt"
            fp = open(f"{folderPath}/{fileName}", "w", encoding="utf-8")
            fp.write(strContent)
            fp.close()

            listContent.append(strContent)



        fp = open("HomeWork.json", "w", encoding="utf-8")
        fp.write(json.dumps(listContent, ensure_ascii=False))
        fp.close()

if __name__ == '__main__':
    visit()
    getMainLinks()
    getSubLinks()
    saveJson()
    writeTxt()
    close()
