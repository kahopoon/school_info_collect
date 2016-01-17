#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
import re
import codecs
import csv
import time
import logging

#content from
request_url = "http://applications.chsc.hk/ssp2015/sch_detail1.php?lang_id=2&sch_id="
#sch_id initial sequence
sequence = 1
#maximum no data tolerate on continous sequence
go_on_max = 10
#count on no data continous sequence
go_on = 0
#exception item max try
item_exception_max = 5
#exception try hold time in seconds
item_exception_holdtime = 0.3
#last known good collected data id
last_good = 0
#all data
all_schoolinfo = []
#item exception remain list
item_exception_list = []
#log filename
log_filename = "school_info.log"
#output filename
output_filename = time.strftime("%Y%m%d") + "_secondary_school_info.csv"

#initialize log function, output as (timestamp, scho info type, log type, log message)
logger = logging.getLogger('S_SCHOOL_INFO')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(log_filename)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)
    
#put raw data row into 'raw_data_row' in list
def getRawData(input):
    global go_on, last_good, item_exception_list
    item_try_remain = item_exception_max
    while item_try_remain >= 0:
        try:
            html_open = urllib2.urlopen(request_url + str(input))
        except Exception:
            item_try_remain -= 1
            if item_try_remain < 0:
                item_exception_list.append(input)
            time.sleep(item_exception_holdtime)  
            continue
        else:      
            html_read = html_open.read()
            html_data = unicode(html_read,'UTF-8').encode('UTF-8')  
            find_school_name = re.search('<td colspan="4" align="left"><span class="sch_detail_header_text">' + '(.+?)' + '</span>', html_data) 
            if find_school_name:
                last_good = input
                go_on = 0
                return html_data
            else:
                go_on += 1
                return None

#write every row of all_schoolinfo into csv
def outputFile():
    headers = ['中文名稱','英文名稱', '地址','電話','電郵', '傳真', '網址', '本區', '他區', '校監/ 校管會主席', '校長', '學校類別', '學生性別', '學校佔地面積', '辦學團體', '是否已成立法團校董會', '宗教', '創校年份', '校訓', '家長教師會', '學生會', '舊生會/校友會']
    with open(output_filename,'wb') as f:
        f_csv = csv.writer(f)
        f.write(codecs.BOM_UTF8)
        f_csv.writerow(headers)
        f_csv.writerows(all_schoolinfo)        
    logger.info("已輸出 " + str(len(all_schoolinfo)) + " 項紀錄至檔案 " + time.strftime("%Y%m%d") + ".csv")
           
#get school info, encapsulate into tuple row, and append the row to all_schoolinfo
def getInformation(input):
    global all_schoolinfo, sequence
    raw_data = getRawData(str(input))
    if raw_data != None:
        schoolinfo_row = []    
        find_school_name = re.findall('<span class="sch_detail_header_text">' + '(.+?)' + '</span>', raw_data)
        school_chi_name = find_school_name[0]
        school_eng_name = find_school_name[1]      
        find_school_info = re.findall('<span class="sch_detail_info">' + '(.+?)' + '</span>', raw_data)
        school_addr = find_school_info[1]
        school_tel = find_school_info[3]
        school_email = find_school_info[5]
        school_fax = find_school_info[7]
        school_url = find_school_info[9]   
        find_school_district = re.search('<td width="61%" align="left">' + '(.+?)' + '</td>', raw_data)
        school_district1 = find_school_district.group(1)  
        find_school_extra_raw = re.findall('<td align="left"' + '(.+?)' + '</td>', raw_data)
        find_school_extra = []
        for loop in range(len(find_school_extra_raw)):
            if "<span" not in find_school_extra_raw[loop]:
                if "<a" not in find_school_extra_raw[loop]:
                    if find_school_extra_raw[loop] == ">":
                        find_school_extra_raw[loop] = find_school_extra_raw[loop].replace(">", "-")
                    find_school_extra_raw[loop] = find_school_extra_raw[loop].replace(">", "")
                    find_school_extra_raw[loop] = find_school_extra_raw[loop].strip()
                    find_school_extra.append(find_school_extra_raw[loop])         
        school_district2 = find_school_extra[1]
        school_chancellor = find_school_extra[3]
        school_principal = find_school_extra[5]
        school_mode = find_school_extra[7]
        school_studentGender = find_school_extra[9]
        school_areaSize = find_school_extra[11]
        school_sponsor = find_school_extra[13]
        school_imc = find_school_extra[15] 
        school_religious = find_school_extra[17]
        school_opened = find_school_extra[19]
        school_slogan = find_school_extra[21]
        school_pta = find_school_extra[23]
        school_su = find_school_extra[25]
        school_alumni = find_school_extra[27]
        schoolinfo_row.extend((school_chi_name, school_eng_name, school_addr, school_tel, school_email, school_fax, school_url,
        school_district1, school_district2, school_chancellor, school_principal, school_mode, school_studentGender, school_areaSize,
        school_sponsor, school_imc, school_religious, school_opened, school_slogan, school_pta, school_su, school_alumni))
        all_schoolinfo.append(tuple(schoolinfo_row))
    sequence += 1

#tells data correctness before output
def dataReport():
    error_found = [s for s in item_exception_list if s < last_good]
    if not error_found:
        logger.info("沒有資料錯誤，準備輸出...")
    else:
        logger.error(error_found)
        logger.error("以上 " + str(len(error_found)) + " 項錯誤資料未能修正，準備輸出")
          
def start():
    logger.info("開始收集資料，請稍候...")
    while go_on < go_on_max:
        getInformation(sequence)
    dataReport()
    outputFile()
    
start()
