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

# 控制鍵盤
from selenium.webdriver.common.keys import Keys

options = webdriver.ChromeOptions();
options.add_argument("--headless");
options.add_argument('--incognito');
options.add_argument('--disable-popup-blocking');

options.add_experimental_option("prefs", {"download.default_directory": "C:\\Users\\Student\\Downloads\\台北人口\\新北"});

url = 'https://www.ca.ntpc.gov.tw/';

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

        # 蒐集資料
        try:
            # 等待篩選元素出現
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "tbody tr")
                )
            )

            driver.find_element(By.CSS_SELECTOR,
                                'div[class="bt col-lg-3 col-md-3 col-sm-6 col-xs-6"] input[value="開始搜尋"]').click()

            driver.find_element(By.CSS_SELECTOR,
                                'div[class="bt col-lg-3 col-md-3 col-sm-6 col-xs-6"] input[value="匯出csv"]').click()

            tt = time.ctime()

            print('執行時間: ' + str(tt))

            time.sleep(1)


        except TimeoutException as e:

            print("出現504")

            driver.navigate().refresh();

            time.sleep(6)

            continue