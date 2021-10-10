def adult(url):

    from selenium import webdriver
    from selenium.common.exceptions import TimeoutException
    from selenium.common.exceptions import NoSuchElementException
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    from selenium.webdriver.common.by import By
    from time import sleep
    import re

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")                #不開啟實體瀏覽器背景執行
    options.add_argument("----disable-plugins")        # 禁用插鍵
    options.add_argument("-ignore-certificate-errors")
    options.add_argument("-ignore-ssl-errors")
#    options.add_argument("--start-maximized")         #最大化視窗
    options.add_argument("--incognito")               #開啟無痕模式
    options.add_argument("--disable-popup-blocking ") #禁用彈出攔截
    executable_path = './chromedriver.exe'

    # 使用 Chrome 的 WebDriver (含上方的option)
    driver = webdriver.Chrome( options = options, executable_path = executable_path)

    driver.get(f"{url}")

    cssSelector = 'button.lh-copy.ws-normal.button.green.mt3.w-100.tc'

    listData = []

    try:
        WebDriverWait(driver, 1).until(
            EC.visibility_of_element_located(
                 (By.CSS_SELECTOR, cssSelector)
             )
         )
        # 請求滿十八歲 Web Element 並按下按鈕
        driver.find_element_by_css_selector(cssSelector).click()

        sleep(1)

        # 開始搜尋資料

        a_title = driver.find_element(By.CSS_SELECTOR, 'h2.f4.mt2.mb1').get_attribute('innerText')

        a_donate = driver.find_element(By.CSS_SELECTOR, 'div.f3.b.js-sum-raised.nowrap').get_attribute('innerText')

        # 目標金額會有長期每月donate ，分辨是不是長期donate

        a_target = driver.find_element(By.CSS_SELECTOR, 'div[class="f7"]').get_attribute('innerText')

        if a_target =='/ 每月':
            a_target = None
        else:
            a_target = int(''.join(re.findall(r'\d', a_target)))

        # 判斷贊助人數 有些是即將募資還沒有人數

        try:
            n_sponsor = int(driver.find_element(By.CSS_SELECTOR, 'span.js-backers-count').get_attribute('innerText'))

        except NoSuchElementException:

            n_sponsor = re.findall(r'[\u4e00-\u9fa5]+', driver.find_element(By.CSS_SELECTOR, 'div.mb1.f7.js-preheating span.mr2.b').get_attribute('innerText'))[0]

        # 如果沒有剩餘時間 就加入None
        try:

            t_remaining = driver.find_element_by_class_name( 'span.js-time-left').get_attribute('innerText')

        except NoSuchElementException :

            t_remaining = None

            # 募資開始時間與結束時間 以dict做分類再各自放入listData
        
        dictDuration = {"begin": "", "end": ""}

        a_schedule = driver.find_element(By.CSS_SELECTOR, 'div.mb2.f7').get_attribute('innerText')

        matchDuration = re.search(r'(\d{4}\/\d{2}\/\d{2}\s\d{2}:\d{2})(\s–\s(\d{4}\/\d{2}\/\d{2}\s\d{2}:\d{2}))?', a_schedule)

        dictDuration['begin'] = matchDuration[1]

        if matchDuration[3] != None:
            dictDuration['end'] = matchDuration[3]
        else:
            dictDuration['end'] = None

        QA = driver.find_elements(By.CSS_SELECTOR, 'span.f7.b.ml3.gray')

        QA_b = [ int(j.get_attribute('innerText')) for j in QA]

        if len(QA_b) == 1:
            QA_b.insert(0, 0)
            QA_b.append(0)

        elif len(QA_b) < 3:
            QA_b.insert(0, 0)

        listData = {"案件名稱": a_title,
                         "目前金額": int(''.join(re.findall(r'\d+', a_donate))),
                         "目標金額": a_target,
                         "贊助人數": n_sponsor,
                         "剩餘時間": t_remaining ,
                         "開始時程": dictDuration['begin'],
                         "結束時程": dictDuration['end'],
                         "專案更新": QA_b[0],
                        "留言": QA_b[1],
                        "常見問答": QA_b[2]
                        }

        driver.quit()

    except TimeoutException:
        print("等待逾時!")

    finally:
        driver.quit()

    return listData
