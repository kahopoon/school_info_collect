# -*- coding: utf-8 -*-
import urllib2
import re
import codecs
from Tkinter import *
import csv
import tkFileDialog

#content from
request_url = "http://applications.chsc.hk/ssp2015/sch_detail1.php?lang_id=2&sch_id="
#sch_id sequence
sequence = 1
#retry maximum
retry_max = 100
#retry count
retry = 0
#checking status
checking = False
#re-run time for checking
rerun = 2
#all data
all_schoolinfo = []

#write every row of all_schoolinfo into csv
def outputFile():
    headers = ['中文名稱','英文名稱', '地址','電話','電郵', '傳真', '網址', '本區', '他區', '校監/ 校管會主席', '校長', '學校類別', '學生性別', '學校佔地面積', '辦學團體', '是否已成立法團校董會', '宗教', '創校年份', '校訓', '家長教師會', '學生會', '舊生會/校友會']
    label_allscanned_content.set("結束檢查，輸出" + str(len(all_schoolinfo)) + "項紀錄至檔案 ......")
    root.update()
    file_type = [('Comma Separated values', '*.csv'), ]
    file_name = tkFileDialog.asksaveasfilename(filetypes=file_type, title="另存...")
    with open(file_name,'wb') as f:
        f_csv = csv.writer(f)
        f.write(codecs.BOM_UTF8)
        f_csv.writerow(headers)
        f_csv.writerows(all_schoolinfo)        
    label_output_content.set("輸出完成。再見！")

#determine to recall getInformation for checking
def checkData():
    global rerun, sequence, retry
    rerun -= 1
    sequence = 1
    retry = 0
    label_allscanned_content.set("收集完畢，重新檢查 ......(剩餘" + str(rerun) + "次)")
    root.update()
    root.after(0, getInformation(sequence))
            
#put raw data row into 'raw_data_row' in list
def getRawData(input):
    global retry 
    try:
        html_open = urllib2.urlopen(request_url + str(input))
    except Exception:
        label_latest_content.set("ID: " + str(input) + " 沒有資料, 嘗試下一個......(" + str(retry_max - retry) + "次後結束)")
        retry += 1
        return None
    else:         
        html_read = html_open.read()
        html_data = unicode(html_read,'UTF-8').encode('UTF-8')
        find_school_name = re.search('<td colspan="4" align="left"><span class="sch_detail_header_text">' + '(.+?)' + '</span>', html_data) 
        if find_school_name:       
            school_name = find_school_name.group(1)
            label_latest_content.set("找到 " + school_name + " ！")
            retry = 0
            return html_data
        else:
            retry += 1
            return None
            
#get school info, encapsulate into tuple row, and append the row to all_schoolinfo
def getInformation(input):
    global all_schoolinfo, sequence, checking  
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
        if not checking:
            all_schoolinfo.append(tuple(schoolinfo_row))
        else:
            for loop in all_schoolinfo:
                if schoolinfo_row[0] == loop[0]:
                    break
                if loop is all_schoolinfo[-1]:
                    all_schoolinfo.append(tuple(schoolinfo_row))           
    sequence += 1
    root.update()
    if retry < retry_max:
        root.after(0, getInformation(sequence))
    else:
        if rerun > 0:
            checking = True
            root.after(0, checkData)
        else:
            checking = False
            root.after(0, outputFile)
    
#call GUI
root = Tk()
#windows box non-resizable and fixes with supplied width height attributes
root.resizable(width=FALSE, height=FALSE)
root.geometry('{}x{}'.format(500, 65))
frame = Frame(root)
#main title
frame.master.title("中學概覽2015")
frame.pack()
#label show on gui
label_latest_content = StringVar()
Label(frame, textvariable=label_latest_content, justify=LEFT).pack()
label_allscanned_content = StringVar()
Label(frame, textvariable=label_allscanned_content, justify=LEFT).pack()
label_output_content = StringVar()
Label(frame, textvariable=label_output_content, justify=LEFT).pack()
#initial function call
root.after(0, getInformation(sequence))
#GUI start
root.mainloop()
