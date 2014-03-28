#coding:utf-8
'''
Created on 2013-5-27

@author: shuangluo
'''
from ldap.models import User
from django_platform.settings import systemId, apiUrl
import urllib
import base64
import hashlib
import random


def modules_for_user(request):
    mg_ids = []
    username = request.user.username
    try:
        user = User.objects.get(uName=username)
    except:
        user = None
    user_groups = user.usergroup_set.all()
    for ug in user_groups:
        for mg in ug.ugModuleList.all():
            mg_ids.append(mg.mgID)
    return mg_ids


def leader_has_groups(request):
    ugs = []
    username = request.user.username
    try:
        leader = User.objects.get(uName=username)
    except:
        return ugs
    user_groups = leader.usergroup_set.all()
    for ug in user_groups:
        if ug.ugLeader.uName == username:
            ugs.append(ug)
    return ugs


def is_leader(request):
    return request.user.is_staff


def is_operator(request):
    return request.user.is_superuser


def ssha_encode(text):
    salt = ""
    for _i in range(10):
        j = random.randint(0, 15)
        salt += "01234567890abcdef"[j:j + 1]
    print "org_slat: " + salt
    hash_ = "{SSHA}" + base64.encodestring(hashlib.sha1(text + salt).digest() + salt)
    return hash_


def ssha_check(text, hash_):
    hash_ = base64.decodestring(hash_[6:])
    print "hash+salt: " + hash_
    salt_ = hash_[20:]
    print salt_
    hash_ = hash_[0:20]
    print hash_
    n_hash = hashlib.sha1(text + salt_).digest()
    return hash_ == n_hash


def get_itil_info(ip="", server_id=0, dept_id=10, server_gid=0, top_id=56187):
    if ip != "":
        cond = '"serverIP":"%s"' % ip
    elif server_id > 0:
        cond = '"serverId":"%s"' % server_id
    else:
        cond = '"serverDeptId":"%s"' % dept_id
        if server_gid > 0:
            cond += ', "serverGroupId":"%s"' % server_gid
        if top_id > 0:
            cond += ', "serverBusi1Id":"%s"' % top_id
            
    startIndex = 0
    pageSize = 100
    totalRows = 1
    importNum = 0
    
    while startIndex < totalRows:
        reqContent = '{"params":{"content":{"schemeId":"Server","type":"Json","version":"1.0","dataFormat":"dict",'\
                     '"requestInfo":{"systemId":"%s","sceneId":"83","requestModule":"","operator":""},'\
                     '"resultColumn":{ "serverAssetId":"", "serverName":"", "serverOperator":"",'\
                     '"serverBakOperator":"", "serverStatusId":"", "serverStatusName":"", "serverLanIP":"",'\
                     '"serverWanIP":"", "idcParentName":"", "idcParentId":"", "allBusiness_cache":""},'\
                     '"pagingInfo":{"startIndex":"%s","pageSize":"%s","returnTotalRows":"1"},'\
                     '"orderBy":"serverId asc",'\
                     '"conditionLogical":"",'\
                     '"searchCondition":{ %s}}}}' % (systemId, startIndex, pageSize, cond)
        f = urllib.urlopen(apiUrl, reqContent)
        result = f.read()


def save_itil_data():
    pass


def save_top_group():
    pass


def save_biz_group():
    pass


def save_machine_group():
    pass


def save_machine():
    pass
