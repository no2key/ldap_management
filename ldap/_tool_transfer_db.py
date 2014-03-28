#coding:utf-8

'''
数据库格式转换 ldapNow -> django
'''

import MySQLdb as mdb
from datetime import datetime
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class MySQL(object):
    def __init__(self, host='127.0.0.1', username='', password='', database=''):
        self.conn = mdb.connect(host, username, password, database, charset='utf8')

    def closeLink(self):
        self.conn.close()


db_now = MySQL(username='root', database='ldapnow')
db_django = MySQL(username='root', database='sh')

conn_now = db_now.conn
cur_now = conn_now.cursor()

conn_django = db_django.conn
cur_django = conn_django.cursor()

sql_now = 'SELECT moduleId1, moduleId2, moduleId3, moduleName FROM ticsonservermodule'

cur_now.execute(sql_now)
result_now = cur_now.fetchall()

for row in result_now:
    tid = row[0]
    bid = row[1]
    mid = row[2]
    name = row[3]
    if tid != 0 and bid == 0 and mid == 0:
        sql_t = "REPLACE INTO ldap_bizset(tgID, tgName, tgUpdateBy, tgUpdateTime) " \
                "VALUES ('%s', '%s', 'sync', '%s')" % (tid, name, now)
        cur_django.execute(sql_t)
conn_django.commit()
cur_django.close()

cur_django = conn_django.cursor()
for row in result_now:
    tid = row[0]
    bid = row[1]
    mid = row[2]
    name = row[3]
    if bid != 0 and mid == 0:
        sql_b = "REPLACE INTO ldap_bizgroup(bgID, bgName, bgParent_id, bgUpdateBy, bgUpdateTime) " \
                "VALUES ('%s', '%s', '%s', 'sync', '%s')" % (bid, name, tid, now)
        cur_django.execute(sql_b)
conn_django.commit()
cur_django.close()

cur_django = conn_django.cursor()
for row in result_now:
    tid = row[0]
    bid = row[1]
    mid = row[2]
    name = row[3]
    if mid != 0:
        sql_m = "REPLACE INTO ldap_module(mgID, mgName, mgParent_id, mgEnable, mgUpdateBy, mgUpdateTime) " \
                "VALUES ('%s', '%s', '%s', '1', 'sync', '%s')" % (mid, name, bid, now)
        cur_django.execute(sql_m)
conn_django.commit()
cur_django.close()

sql_now = 'SELECT sId, sIp, sExtIp, sHostname, sAssetId, sManager, sSecManager, sModuleId3, sStatus FROM ticsonserver'

cur_now.execute(sql_now)
result_now = cur_now.fetchall()

cur_django = conn_django.cursor()
for row in result_now:
    sid = row[0]
    sIp = row[1]
    sExtIp = row[2]
    sHostname = row[3]
    sAssetId = row[4]
    sManager = row[5]
    sSecManager = row[6]
    sModuleId3 = row[7]
    sStatus = row[8]

    sql = "REPLACE INTO ldap_machine(mID, mIP, mExtIP, mHostName, mAssetID, " \
          "mMainOp, mBakOp, mMainDev, mBakDev, mGroupID_id, mStatus, mUpdateBy, mUpdateTime) " \
          "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '0', '0', '%s', '%s', 'sync', '%s')" \
          % (sid, sIp, sExtIp, sHostname, sAssetId, sManager, sSecManager, sModuleId3, sStatus, now)
    # print sql
    cur_django.execute(sql)
conn_django.commit()
cur_django.close()

conn_django.close()
cur_now.close()
conn_now.close()
