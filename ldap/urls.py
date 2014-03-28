#coding:utf-8
'''
Created on 2013-5-30
LDAP模块url路由信息
@author: shuangluo
'''
from django.conf.urls import patterns, url

from ldap import common
urlpatterns = patterns('',
    url(r'common_add/', common.add_view, name='common_add'),
    url(r'common_list/', common.list_view, name='common_list'),
)

from ldap import sudo
urlpatterns += patterns('',
    url(r'sudo_add/', sudo.add_view, name='sudo_add'),
    url(r'sudo_list/', sudo.list_view, name='sudo_list'),
)

from ldap import leader
urlpatterns += patterns('',
    url(r'group_info/', leader.info, name='leader_info'),
    url(r'^approve/', leader.approve, name='leader_approve'),
)

from ldap import operator
urlpatterns += patterns('',
    url(r'op_approve/', operator.op_approve, name='op_approve'),
    url(r'op_sudo_disable/', operator.op_sudo_disable, name='op_sudo_disable'),

    url(r'op_group_add/', operator.UserGroupAdd.as_view(), name='op_group_add'),
    url(r'op_group_edit/(?P<pk>\d+)', operator.UserGroupEdit.as_view(), name='op_group_edit'),
    url(r'op_group_list/', operator.UserGroupList.as_view(), name='op_group_list'),
    url(r'op_group_delete/(?P<pk>\d+)', operator.UserGroupDelete.as_view(), name='op_group_delete'),

    url(r'op_user_add/', operator.UserAdd.as_view(), name='op_user_add'),
    url(r'op_user_edit/(?P<pk>\d+)', operator.UserEdit.as_view(), name='op_user_edit'),
    url(r'op_user_list/', operator.UserList.as_view(), name='op_user_list'),
    url(r'op_user_delete/(?P<pk>\d+)', operator.UserDelete.as_view(), name='op_user_delete'),
    url(r'op_user_clone/', operator.op_user_clone, name='op_user_clone'),

    url(r'op_sudoer_add/', operator.SudoerAdd.as_view(), name='op_sudoer_add'),
    url(r'op_sudoer_edit/(?P<pk>\d+)', operator.SudoerEdit.as_view(), name='op_sudoer_edit'),
    url(r'op_sudoer_list/', operator.SudoerList.as_view(), name='op_sudoer_list'),
    url(r'op_sudoer_delete/(?P<pk>\d+)', operator.SudoerDelete.as_view(), name='op_sudoer_delete'),

    url(r'op_cmd_add/', operator.CmdAdd.as_view(), name='op_cmd_add'),
    url(r'op_cmd_edit/(?P<pk>\d+)', operator.CmdEdit.as_view(), name='op_cmd_edit'),
    url(r'op_cmd_list/', operator.CmdList.as_view(), name='op_cmd_list'),
    url(r'op_cmd_delete/(?P<pk>\d+)', operator.CmdDelete.as_view(), name='op_cmd_delete'),
)

from ldap import ajax
urlpatterns += patterns('',
    url(r'ajax/topgroup/', ajax.top_group),
    url(r'ajax/bizgroup/(\d+)', ajax.biz_group),
    url(r'ajax/machinegroup/(\d+)', ajax.machine_group),
    url(r'ajax/machine/(\d+)', ajax.machine_from_group),
)
