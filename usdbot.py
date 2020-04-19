#!/usr/bin/python3
#--------------------------------------------------------------------------#
#-----Bot wich watch on the site of central bank of russia ----------------#
#-----course of US dollar and if when it changes send message to telegram--# 
#--------------------------------------------------------------------------#
#--------------------------------------------------------------------------#
#---------------------------svedboxlab-------------------------------------#
#--------------------------------------------------------------------------#
#--------------------------------------------------------------------------#
#--------Modules-------#
import os
import pathlib
import urllib.request
import string
import requests
import socks
import datetime
import sqlite3
#--------Variables-------------------------------------#
logpath=(os.getcwd() +'/.usdcourse/usdcourse.log')
workdirpath=(os.getcwd() +'/.usdcourse')
dbpath=(os.getcwd() +'/.usdcourse/usdcourse.db')
fileusdcourselog=pathlib.Path(logpath)
dirusdcourse = pathlib.Path(workdirpath)
dbfile = pathlib.Path(dbpath)
cbrurl = ('http://www.cbr.ru/scripts/XML_daily.asp?date_req=')
token='' #<----insert TELEGRAM TOKEN
chatid=''#<----insert TELEGRAM CHAT ID
boturl='https://api.telegram.org/bot' 
proxies={"https":"socks5://192.168.0.150:9050"} #--if you live in non free country, you must install tor
urlt = (boturl + token +'/sendMessage')
date=str(datetime.datetime.today().strftime("%d.%m.%Y"))
#----Create the work dir-----------------#
if (os.path.exists(dirusdcourse)):
    pass
else:
    d = os.mkdir(workdirpath)
#----Create the log file---------#
if (os.path.exists(fileusdcourselog)):
    pass
else:
    file = open(logpath, 'w+')
    file.write('0')
    file.close()
#-------Change exist the database------------#
if (os.path.exists(dbfile)):
    pass
else:
    conn = sqlite3.connect(dbfile)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE courses
                      ('id' INTEGER PRIMARY KEY AUTOINCREMENT, 'date' TEXT, 'course' REAL, 'message' TEXT )
                   """)
    cursor.execute("""CREATE TABLE lastusd
                      ('id' INTEGER PRIMARY KEY,'lastcourse' REAL)
                   """)
    cursor.execute("INSERT INTO lastusd (id, lastcourse) VALUES (1, 0)" )
    conn.commit()
    cursor.close()
    conn.close()
#---------------------------------------------------#
cbrpage = str(urllib.request.urlopen(cbrurl).read())
usdindex = cbrpage.find('USD')
usdcoursetmp = (cbrpage[usdindex+91:usdindex+96]).replace(',','.')
usdcourse = float(usdcoursetmp) #-Course of CBR digital--#

#-------Check change course of CBR-------#
#-------------SQL-------------------------#
conn = sqlite3.connect(dbfile)
cur = conn.cursor()
[usdold], = cur.execute("SELECT lastcourse FROM lastusd WHERE id = 1 ")
conn.commit()
cur.close()
conn.close()
#-----------------------------------------#

if (usdcourse == usdold):
    pass
else:
    usdchange = round((usdcourse - usdold),2)
    if (usdchange > 0):
        usdchangestr=str(usdchange)
        usdchangeout = ('+'+ usdchangestr)
        data = {"chat_id":chatid, "text":("Курс ЦБ  " + str(usdcourse) + " (" + usdchangeout + ")")}
        message = str(requests.post(urlt, data ,proxies=proxies)) #--if you live in free country you must comment
       #message = str(requests.post(urlt, data)) #--if you live in free country, you must uncomment
        file = open(logpath, 'a')
        file.write('\n' "| " + message + " | "+ date + " | Курс USD - " + usdcoursetmp + " |")
        file.close()
        #-------------SQL----------------#
        conn = sqlite3.connect(dbfile)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO courses (date, course, message) VALUES (?, ?, ?)" , (date, usdcourse, message))
        cursor.execute("UPDATE lastusd SET lastcourse = ? WHERE id = 1 "  , (usdcourse,))
        conn.commit()
        cursor.close()
        conn.close()
        #--------------------------------#
    else:
        usdchangeout = str(usdchange)
        data = {"chat_id":chatid, "text":("Курс ЦБ  " + str(usdcourse) + " (" + usdchangeout + ")")}
        message = str(requests.post(urlt, data ,proxies=proxies)) #--if you live in free country you must comment
       #message = str(requests.post(urlt, data)) #--if you live in free country, you must uncomment
        file = open(logpath, 'a')
        file.write('\n' "| " + message + " | "+ date + " | Курс USD - " + usdcoursetmp + " |")
        file.close()
        #-------------SQL----------------#
        conn = sqlite3.connect(dbfile)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO courses (date, course, message) VALUES (?, ?, ?)" , (date, usdcourse, message))
        cursor.execute("UPDATE lastusd SET lastcourse = ? WHERE id = 1 "  , (usdcourse,))
        conn.commit()
        cursor.close()
        conn.close()
#----------------------------END-----------------------------#
