# -*- coding: utf-8 -*-
import sys
import urllib2
import re
import codecs
import csv
import time

#content from
request_url = "http://applications.chsc.hk/psp2015/sch_detail1.php?lang_id=2&sch_id="
#sch_id sequence
sequence = 1
#maximum no data tolerate on continous sequence
go_on_max = 50
#count on no data continous sequence
go_on = 0
#exception item try max
item_exception_max = 50
#all data
all_schoolinfo = []

#put raw data row into 'raw_data_row' in list
def getRawData(input):
    global go_on
    item_try_remain = item_exception_max
    while item_try_remain > 0:
        try:
            html_open = urllib2.urlopen(request_url + str(input))
        except Exception:
            #print "收集錯誤，重新嘗試......(" + str(item_exception_max - item_try_remain) + " 次後結束)"
            item_try_remain -= 1
            continue
        else:      
            html_read = html_open.read()
            html_data = unicode(html_read,'UTF-8').encode('UTF-8')  
            find_school_name = re.search('<td colspan="4" align="left"><span class="sch_detail_header">' + '(.+?)' + '</span>', html_data) 
            if find_school_name:
                #print "找到 " + find_school_name.group(1).strip() + " !"
                go_on = 0
                return html_data
            else:
                #print "ID: " + str(input) + " 資料空白， " + str(go_on_max - go_on) + " 項後結束"
                go_on += 1
                return None

#write every row of all_schoolinfo into csv
def outputFile():
    headers = ['中文名稱','英文名稱','校網編號','地址','電話','電郵', '傳真', '網址', '校監／學校管理委員會主席', '是否已成立法團校董會', '校長', '學校類別', '學生性別', '辦學團體', '宗教', '創校年份', '校訓', '學校佔地面積', '一條龍中學', '直屬中學', '聯繫中學', '教學語言', '校車服務', '家長教師會', '舊生會/校友會', '法團校董會名稱']
    file_name = time.strftime("%Y%m%d") + "_primary_school_info.csv"
    with open(file_name,'wb') as f:
        f_csv = csv.writer(f)
        f.write(codecs.BOM_UTF8)
        f_csv.writerow(headers)
        f_csv.writerows(all_schoolinfo)        
    print "已輸出 " + str(len(all_schoolinfo)) + " 項紀錄至檔案 " + time.strftime("%Y%m%d") + ".csv (" + time.strftime("%H:%M:%S") + ")" 
           
#get school info, encapsulate into tuple row, and append the row to all_schoolinfo
def getInformation(input):
    global all_schoolinfo, sequence
    raw_data = getRawData(str(input))
    if raw_data != None:
        schoolinfo_row = []    
        find_school_name = re.findall('<span class="sch_detail_header">' + '(.+?)' + '</span>', raw_data)
        school_chi_name = find_school_name[0].strip()
        school_eng_name = find_school_name[1].strip()
        find_school_poa = re.findall('<span class="sch_detail_poa">' + '(.+?)' + '</span>', raw_data)
        school_poa = find_school_poa[1].strip()
        find_school_info = re.findall('<span class="sch_detail_info">' + '(.+?)' + '</span>', raw_data)
        for loop in range(len(find_school_info)):
            find_school_info[loop] = find_school_info[loop].strip()
        school_addr = find_school_info[1]
        school_tel = find_school_info[3]
        school_email = find_school_info[5]
        school_fax = find_school_info[7]
        school_url = find_school_info[9]   
        find_school_chancellor = re.search('<td width="293" align="left">' + '(.+?)' + '</td>', raw_data)
        school_chancellor = find_school_chancellor.group(1)  
        find_school_extra = re.findall('<td align="left">' + '(.+?)' + '</td>', raw_data)
        for loop in range(len(find_school_extra)):
            find_school_extra[loop] = find_school_extra[loop].replace("<p align='left'>-</p>", "-")
            find_school_extra[loop] = find_school_extra[loop].replace("<br>", "-")
            find_school_extra[loop] = find_school_extra[loop].strip()
        school_imc = find_school_extra[11]
        school_principal = find_school_extra[14]
        school_mode = find_school_extra[17]
        school_studentGender = find_school_extra[20]
        school_sponsor = find_school_extra[23]
        school_religious = find_school_extra[26]
        school_opened = find_school_extra[29]
        school_slogan = find_school_extra[32]
        school_areaSize = find_school_extra[35]
        school_directthrough = find_school_extra[38]
        school_direct_S_school = find_school_extra[41]
        school_connect_S_school = find_school_extra[44]
        school_tLanguage = find_school_extra[47]
        school_bus = find_school_extra[50]
        school_pta = find_school_extra[53]
        school_alumni = find_school_extra[56]
        school_imcName = find_school_extra[59]  
        schoolinfo_row.extend((school_chi_name, school_eng_name, school_poa, school_addr, school_tel, school_email, school_fax, school_url,
        school_chancellor, school_imc, school_principal, school_mode, school_studentGender, school_sponsor, school_religious,
        school_opened, school_slogan, school_areaSize, school_directthrough, school_direct_S_school, school_connect_S_school,
        school_tLanguage, school_bus, school_pta, school_alumni, school_imcName))  
        all_schoolinfo.append(tuple(schoolinfo_row)) 
    sequence += 1
    if go_on < go_on_max:
        getInformation(sequence)
        
def start():
    print "開始收集資料，請稍候... (" + time.strftime("%H:%M:%S") + ")"
    sys.stdout.flush()
    getInformation(sequence)
    outputFile()
    
start()
