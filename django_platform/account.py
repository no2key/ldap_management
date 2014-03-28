#coding:utf-8
'''
Created on 2013-5-28

@author: shuangluo
'''
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from ldap.models import User

@login_required
def info_view(request):
    errors = []
    loggin_name = request.user.username
    try:
        ldap_user = User.objects.get(uName=loggin_name)
    except:
        ldap_user = None
        errors.append("系统中不存在您的信息，请联系组长添加信息。")
        return render_to_response('loggedin.html', {'errors':errors, 
                                                    'user':request.user})
    user_groups = ldap_user.usergroup_set.all()
    ugs = [(ug.ugName, ug.ugLeader.uName) for ug in user_groups]
    mgs = {}
    for user_group in user_groups:
        machine_groups = user_group.ugModuleList.all()
        for mg in machine_groups:
            mgs[mg.mgID] = "%s=>%s=>%s" % (mg.mgParent.bgParent.tgName,mg.mgParent.bgName,mg.mgName)
    return render_to_response('loggedin.html', {'ugs':ugs, 
                                                'mgs':mgs,
                                                'errors':errors,
                                                'user':request.user})

def invalid(request):
    return render_to_response('invalid.html')
