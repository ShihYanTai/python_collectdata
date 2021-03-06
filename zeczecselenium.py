def adult(url):

    from selenium import webdriver
    from selenium.common.exceptions import TimeoutException
    from selenium.common.exceptions import NoSuchElementException
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    from selenium.webdriver.common.by import By
    import datetime
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

        drecord = datetime.datetime.now().strftime(f'%Y/%m/%d %H:%M:%S')

        # 開始搜尋資料

        a_title = driver.find_element(By.CSS_SELECTOR, 'h2.f4.mt2.mb1').get_attribute('innerText')

        # 篩選募資區域

        try:

            a_zone = driver.find_element(By.CSS_SELECTOR, 'div.f6.gray span.b').get_attribute('innerText')

        except NoSuchElementException:

            a_zone = None

        # 擷取募資類別

        method = driver.find_elements(By.CSS_SELECTOR, 'a.underline.dark-gray.b.dib')

        a_method = [j_method.get_attribute('innerText') for j_method in method]

        a_donate = int(''.join(re.findall(r'\d+', driver.find_element(By.CSS_SELECTOR, 'div.f3.b.js-sum-raised.nowrap').get_attribute('innerText'))))

        # 目標金額會有長期每月donate ，分辨是不是長期donate

        a_target = driver.find_element(By.CSS_SELECTOR, 'div[class="f7"]').get_attribute('innerText')

        # 由目標金額篩選完後算出達成率

        if a_target =='/ 每月':
            a_target = None
            arrivepercent = None

        else:
            a_target = int(''.join(re.findall(r'\d', a_target)))
            arrivepercent = a_donate / a_target

        # 判斷贊助人數 有些是即將募資還沒有人數

        try:
            n_sponsor = int(driver.find_element(By.CSS_SELECTOR, 'span.js-backers-count').get_attribute('innerText'))

        except NoSuchElementException:

            n_sponsor = re.findall(r'[\u4e00-\u9fa5]+', driver.find_element(By.CSS_SELECTOR, 'div.mb1.f7.js-preheating span.mr2.b').get_attribute('innerText'))[0]

        # 如果沒有剩餘時間 就加入None
        try:

            t_remaining = driver.find_element(By.CSS_SELECTOR, 'span.js-time-left').get_attribute('innerText')

            # 剩餘時間轉成分鐘

            if '天' in re.findall(r'[\u4e00-\u9fa5]+', t_remaining):
                t_remaining = int(''.join(re.findall(r'\d+', t_remaining))) * 24 * 60

            elif '小時' in re.findall(r'[\u4e00-\u9fa5]+', t_remaining):
                t_remaining = int(''.join(re.findall(r'\d+', t_remaining))) * 60
            else:
                t_remaining = int(''.join(re.findall(r'\d+', t_remaining.text)))

        except NoSuchElementException :

            t_remaining = None

            # 募資開始時間與結束時間 以dict做分類再各自放入listData
        
        dictDuration = {"begin": "", "end": ""}

        a_schedule = driver.find_element(By.CSS_SELECTOR, 'div.mb2.f7').get_attribute('innerText')

        matchDuration = re.search(r'(\d{4}\/\d{2}\/\d{2}\s\d{2}:\d{2})(\s–\s(\d{4}\/\d{2}\/\d{2}\s\d{2}:\d{2}))?', a_schedule)

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

        QA = driver.find_elements(By.CSS_SELECTOR, 'span.f7.b.ml3.gray')

        QA_b = [ int(j.get_attribute('innerText')) for j in QA]

        if len(QA_b) == 1:
            QA_b.insert(0, 0)
            QA_b.append(0)

        elif len(QA_b) < 3:
            QA_b.insert(0, 0)

        listData = {"downloadrecord": drecord,
                    "案件名稱": a_title,
                    "募資區域": a_zone,
                    "募資方式": a_method[0],
                    "專案類別": a_method[1],
                    "目前金額": a_donate,
                    "目標金額": a_target,
                    "贊助人數": n_sponsor,
                    "剩餘時間": t_remaining,
                    "開始時程": dictDuration['begin'],
                    "結束時程": dictDuration['end'],
                    "專案更新": QA_b[0],
                    "留言": QA_b[1],
                    "常見問答": QA_b[2],
                    "達成率": arrivepercent,
                    "是否完成募資": whether}

        driver.quit()

    except TimeoutException:
        print("等待逾時!")

    finally:
        driver.quit()

    return listData
