import time

from selenium import webdriver

from selenium.webdriver.common.by import By

import pandas as pd

from urllib.error import HTTPError, URLError

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument('--incognito')
options.add_argument('--disable-popup-blocking')

url = 'https://e-service.cwb.gov.tw/HistoryDataQuery/DayDataController.do?command=viewMain&station=466880&stname=%25E6%259D%25BF%25E6%25A9%258B&datepicker=2021-11-23'

driver = webdriver.Chrome(options=options)  # Optional argument, if not specified will search path.

driver.get(url)

# 取得觀測站text
a_elms = driver.find_elements(By.CSS_SELECTOR, 'select[name="selectStno"] option')

a = [i.get_attribute('value')[0:6] for i in a_elms]

path = r'C:\Users\Student\Downloads\氣象\\'

dc = '2010-01-01'

de = '2010-08-17'

d = [str(i).replace(' 00:00:00', '') for i in pd.date_range(start=dc, end=de)]


def climate(d):
    for ind, day in enumerate(d):
        for i in a:
            url = f'https://e-service.cwb.gov.tw/HistoryDataQuery/DayDataController.do?command=viewMain&station={i}&stname=%25E6%259D%25BF%25E6%25A9%258B&datepicker={day}'

            df = pd.read_html(url, encoding='utf-8', header=0)[1].drop([0, 1])

            df["day"] = day

            df["station"] = i

            day.replace('-', '')

            dc = day

            df.to_csv(path + day + i + str(ind) + '.csv')

            t = time.ctime()

            print(t)
    return dc


if __name__ == '__main__':

    while (dc is not de):
        try:
            climate(d)

        except (URLError, HTTPError, TimeoutError, NameError, ValueError):
            time.sleep(5)
            climate(d)
            continue
        else:
            break
driver.quit()
