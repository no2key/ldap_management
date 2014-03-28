#coding:utf-8
'''
Created on 2013-5-24

@author: shuangluo
'''
import json
from django.http import HttpResponse
from ldap.models import Module, BizGroup, BizSet, Machine
from ldap.utils import modules_for_user


def top_group(request):
    tgSelect = []
    tg = BizSet.objects.all()
    for item in tg:
        tgSelect.append("<option value='%s'>%s</option>" % (item.tgID, item.tgName))
    response = json.dumps(tgSelect)
    return HttpResponse(response)


def biz_group(request, top_id):
    bgSelect = []
    bg = BizGroup.objects.all()
    for item in bg:
        if top_id == str(item.bgParent.tgID):
            bgSelect.append("<option value='%s'>%s</option>" % (item.bgID, item.bgName))
    response = json.dumps(bgSelect)
    return HttpResponse(response)


def machine_group(request, biz_id):
    machineSelect = []
    mg = Module.objects.all()
    groups = modules_for_user(request)
    for item in mg:
        if (biz_id == str(item.mgParent.bgID)) and (item.mgID in groups):
            machineSelect.append("<option value='%s'>%s</option>" % (item.mgID, item.mgName))
    response = json.dumps(machineSelect)
    return HttpResponse(response)


def machine_from_group(request, mg_id):
    machines = []
    m = Machine.objects.all()
    for item in m:
        if mg_id == str(item.mGroupID.mgID):
            machines.append("<option value='%s' selected='selected'>%s</option>" % (item.mIP, item.mIP))
    response = json.dumps(machines)
    return HttpResponse(response)


