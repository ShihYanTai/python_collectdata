import time

from selenium import webdriver

# 面對動態網頁，等待某個元素出現的工具，通常與 exptected_conditions 搭配
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.common.by import By

# 搭配 WebDriverWait 使用，對元素狀態的一種期待條件，若條件發生，則等待結束，往下一行執行
from selenium.webdriver.support import expected_conditions as EC

# 處理下拉式選單的工具
from selenium.webdriver.support.ui import Select

# 處理逾時例外的工具
from selenium.common.exceptions import TimeoutException

import csv

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument('--incognito')
options.add_argument('--disable-popup-blocking')

url = 'https://www.ca.ntpc.gov.tw/'

driver = webdriver.Chrome(options=options)  # Optional argument, if not specified will search path.

driver.get(url)

time.sleep(5)  # Let the user actually see something!

a_elms = driver.find_elements(By.CSS_SELECTOR, 'a[title="幸福人生"]')[1]

url = a_elms.get_attribute('href')

driver.quit()

time.sleep(5)

driver = webdriver.Chrome(options=options)

driver.get(url)

a_elms = driver.find_elements(By.CSS_SELECTOR, 'span[id="short2"] a[title="新北市人口統計"]')[0]

url = a_elms.get_attribute('href')

driver.quit()

time.sleep(5)

driver = webdriver.Chrome(options=options)

driver.get(url)

a_elms = driver.find_elements(By.CSS_SELECTOR, 'div[class="level1"] a[title="新北市各里人口數排行榜"]')[0]

url = a_elms.get_attribute('href')

driver.quit()

time.sleep(5)

driver = webdriver.Chrome(options=options)

driver.get(url)

# 選擇下拉是選單搜尋

# 蒐集年分

yyyy = driver.find_elements(By.CSS_SELECTOR, 'select[id="yyyy"] option')

yyyy = [y.get_attribute('value') for y in yyyy]

yyyy.remove('')

# 選擇全部及調整比數

listtxt = []

# 執行選擇年分

for y in yyyy:

    selectYY = Select(driver.find_element(By.CSS_SELECTOR, 'select#yyyy'))

    selectYY.select_by_visible_text(y)

    for m in range(1, 13):

        mt = str(m)

        selectmm = Select(driver.find_element(By.CSS_SELECTOR, 'select#mm'))

        selectmm.select_by_visible_text(mt)

        #         展開全部
        selectmm = Select(driver.find_element(By.CSS_SELECTOR, 'select#pagesize'))

        selectmm.select_by_visible_text('全部')

        #         點擊調整紐
        driver.find_element(By.CSS_SELECTOR, 'input[value="調整筆數"]').click()
        time.sleep(5)
        #         蒐集資料
        try:
            # 等待篩選元素出現
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "tbody tr")
                )
            )

            tbody_tr = driver.find_elements(By.CSS_SELECTOR, 'tbody tr')

            #             '''
            #             totalHeight => 瀏覽器內部的高度
            #             offset => 當前捲動的量(高度)
            #             count => 計無效滾動次數
            #             limit => 最大無效滾動次數
            #             wait_second => 每次滾動後的強制等待時間
            #             '''
            totalHeight = 0
            offset = 0
            count = 0
            limit = 3
            wait_second = 3

            # 在捲動到沒有元素動態產生前，持續捲動
            while count <= limit:
                # 每次移動高度
                offset = driver.execute_script(
                    'return window.document.documentElement.scrollHeight;'
                )

                #                 '''
                #                 或是每次只滾動一點距離，
                #                 以免有些網站會在移動長距離後，
                #                 將先前移動當中的元素隱藏
                #                 offset += 600
                #                 '''

                # 捲動的 js code
                js_code = f'''
                    window.scrollTo({{
                        top: {offset}, 
                        behavior: 'smooth' 
                    }});
                '''

                # 執行 js code
                driver.execute_script(js_code);

                # 強制等待，此時若有新元素生成，瀏覽器內部高度會自動增加
                time.sleep(wait_second)

                # 透過執行 js 語法來取得捲動後的當前總高度
                totalHeight = driver.execute_script(
                    'return window.document.documentElement.scrollHeight;'
                );

                # 經過計算，如果滾動距離(offset)大於等於視窗內部總高度(innerHeight)，代表已經到底了
                if offset >= totalHeight:
                    count += 1
                # 為了實驗功能，捲動超過一定的距離，就結束程式
                if offset >= 600:
                    break

            for tr in range(len(tbody_tr) - 1):
                r = driver.find_elements(By.CSS_SELECTOR, 'td[data-th="排名"]')[tr].get_attribute('innerText');

                lz = driver.find_elements(By.CSS_SELECTOR, 'td[data-th="隸屬區"]')[tr].get_attribute('innerText');

                le = driver.find_elements(By.CSS_SELECTOR, 'td[data-th="里"]')[tr].get_attribute('innerText');

                ln = driver.find_elements(By.CSS_SELECTOR, 'td[data-th="鄰數"]')[tr].get_attribute('innerText');

                ho = driver.find_elements(By.CSS_SELECTOR, 'td[data-th="戶數"]')[tr].get_attribute('innerText');

                m = driver.find_elements(By.CSS_SELECTOR, 'td[data-th="男"]')[tr].get_attribute('innerText');

                f = driver.find_elements(By.CSS_SELECTOR, 'td[data-th="女"]')[tr].get_attribute('innerText');

                a = driver.find_elements(By.CSS_SELECTOR, 'td[data-th="合計"]')[tr].get_attribute('innerText');

                listtxt.append({'排名': r,
                                '隸屬': lz,
                                '里': le,
                                '鄰數': ln,
                                '戶數': ho,
                                '男': m,
                                '女': f,
                                '合計': a,
                                '年': y,
                                '月': mt});

                tt = time.ctime()

                print('所有數量(扣除最後):' + str(len(tbody_tr) - 1) + ' 第' + str(
                    tr) + '行 里: ' + le + ' 月:' + mt + ' 年:' + y + ' 執行時間:' + str(tt))

        except TimeoutException as e:

            print("出現504")

            driver.navigate().refresh();

            time.sleep(3)

            continue

# 開啟輸出的 CSV 檔案
with open('output.csv', 'w', newline='', encoding="utf-8") as csvfile:
    # 定義欄位

    fieldnames = ['排名', '隸屬', '里', '鄰數', '戶數', '男', '女', '合計', '年', '月']
    # 將 dictionary 寫入 CSV 檔
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # 寫入第一列的欄位名稱
    writer.writeheader()

    # 寫入資料
    writer.writerows(listtxt)
