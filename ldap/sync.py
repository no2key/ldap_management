#coding:utf-8
'''
Created on 2013-5-31

@author: shuangluo
'''

from django_platform.settings import LDAP_CONFIG
import ldap

def ldap_connect():
    server = LDAP_CONFIG['SERVER'] + ":" + str(LDAP_CONFIG['PORT'])
    conn = ldap.initialize(server)
    if not conn:
        return False
    conn.protocol_version = ldap.VERSION3
    conn.simple_bind_s(LDAP_CONFIG['USER'], LDAP_CONFIG['PASSWORD'])
    return conn


def get_all_users(search_filter="uid=*"):
    conn = ldap_connect()
    if not conn:
        return False
    search_scope = ldap.SCOPE_SUBTREE
    search_filter = search_filter
    search_attr = ['uid', 'uidnumber']
    dn = LDAP_CONFIG['USER_BASE']
    ldap_result_id = conn.search(dn, search_scope, search_filter, search_attr)
    result_set = []
    while 1:
        result_type, result_data = conn.result(ldap_result_id, 0)
        if not result_data:
            break
        else:
            if result_type == ldap.RES_SEARCH_ENTRY:
                result_set.append(result_data)
    print result_set


def get_all_sudoers(search_filter="cn=*"):
    conn = ldap_connect()
    if not conn:
        return False
    search_scope = ldap.SCOPE_SUBTREE
    search_filter = search_filter
    dn = LDAP_CONFIG['SUDOER_BASE']
    ldap_result_id = conn.search(dn, search_scope, search_filter)
    result_set = []
    while 1:
        result_type, result_data = conn.result(ldap_result_id, 0)
        if not result_data:
            break
        else:
            if result_type == ldap.RES_SEARCH_ENTRY:
                result_set.append(result_data)
    print result_set


def del_user(username):
    conn = ldap_connect()
    if not conn:
        return False
    if not username:
        return False
    to_delete = "uid=" + username + "," + LDAP_CONFIG['USER_BASE']
    try:
        conn.delete_s(to_delete)
    except:
        pass


def del_sudoer(cn):
    conn = ldap_connect()
    if not conn:
        return False
    if not cn:
        return False
    to_delete = "cn=" + cn + "," + LDAP_CONFIG['SUDOER_BASE']
    try:
        conn.delete_s(to_delete)
    except:
        pass