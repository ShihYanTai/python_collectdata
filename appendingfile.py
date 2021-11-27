import pandas as pd
import os

Folder_Path = r'C:\Users\Student\Downloads\氣象'  # 要拼接的資料夾及其完整路徑，注意不要包含中文
SaveFile_Path = r'C:\Users\Student\Downloads\氣象'  # 拼接後要儲存的檔案路徑
SaveFile_Name = r'newtaipeiclimate.csv'  # 合併後要儲存的檔名

# 修改當前工作目錄
os.chdir(Folder_Path)

# 將該資料夾下的所有檔名存入一個列表
file_list = os.listdir()

# 讀取第一個CSV檔案幷包含表頭
df = pd.read_csv(Folder_Path + '\\' + file_list[0])  # 編碼預設UTF-8，若亂碼自行更改

# 將讀取的第一個CSV檔案寫入合併後的檔案儲存
df.to_csv(SaveFile_Path + '\\' + SaveFile_Name, encoding="utf_8_sig", index=False)

# 迴圈遍歷列表中各個CSV檔名，並追加到合併後的檔案
for i in range(1, len(file_list)):
    df = pd.read_csv(Folder_Path + '\\' + file_list[i])

    df.to_csv(SaveFile_Path + '\\' + SaveFile_Name, encoding="utf_8_sig", index=False, header=False, mode='a+')