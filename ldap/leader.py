#coding:utf-8
'''
Created on 2013-5-28

@author: shuangluo
'''
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import messages
from ldap.models import TempRoot
from ldap.utils import is_leader, leader_has_groups


@login_required
def info(request):
    managed_ugs = []
    user_info = []
    if is_leader(request):
        ugs = leader_has_groups(request)
        users = []
        for ug in ugs:
            user_list = ""
            mg_list = ""
            users= ug.ugUserList.all()
            mgs = ug.ugModuleList.all()
            for user in users:
                user_list += user.uName
                user_list += "<br />"
            for mg in mgs:
                mg_list += "%s=>%s=>%s" % (mg.mgParent.bgParent.tgName,
                                          mg.mgParent.bgName,
                                          mg.mgName)
                mg_list += "<br />"
            managed_ugs.append((ug.ugName, user_list, mg_list))
 
        s_user = request.POST.get('s_user',"")
        user_names = [user.uName for user in users]
        if s_user:
            if s_user in user_names:
                u_machines = user.uMachineList.all()
                um_list = ""
                for u_machine in u_machines:
                    um_list += u_machine.mIP
                    um_list += "<br />"
                u_roots = user.temproot_set.filter(rEnable = True,
                                                  rIsApproved = True)
                ur_list = ""
                for u_root in u_roots:
                    ur_machines = u_root.rMachineList.all()
                    urm_list = ""
                    for ur_machine in ur_machines:
                        urm_list += ur_machine.mIP
                        urm_list += ";"
                    ur_list += urm_list + "=>" + u_root.rCommand
                    ur_list += "<br />"
                if um_list or ur_list:
                    user_info = (s_user, um_list, ur_list)
            else:
                messages.error(request, "小组内没有查询到这个成员，请检查拼写，或联系运维添加。")
        return render_to_response('leader/groupinfo.html',
                                  {'managed_ugs': managed_ugs, 'user_info': user_info, 'user': request.user},
                                  context_instance=RequestContext(request))    
    else:
        return render_to_response('invalid.html')


@login_required
def approve(request):
    user_list = set()
    to_approve =[]
    username = request.user.username
    if is_leader(request):
        if request.method == "POST":
            choices = request.POST
            if not choices:
                messages.error(request, "请先选择要批准的项目。")
            for choice in choices:
                status = choices[choice]
                if choice.isdigit():
                    try:
                        if status == "yes":
                            TempRoot.objects.filter(id=int(choice)).update(rIsApproved=True, rUpdateBy=username)
                        elif status == "no":
                            TempRoot.objects.filter(id=int(choice)).update(rEnable = False, rUpdateBy=username)
                    except:
                        pass
        ugs = leader_has_groups(request)
        for ug in ugs:
            users= ug.ugUserList.all()
            for user in users:
                user_list.add(user)
        for user in user_list:
            tmp_roots = user.temproot_set.filter(rEnable = True, rIsApproved = False)
            for tmp_root in tmp_roots:
                rIPs = ""
                machines = tmp_root.rMachineList.all()
                for m in machines:
                    rIPs += m.mIP
                    rIPs += "; "
                to_approve.append((user.uName,
                                   tmp_root.rReason,
                                   rIPs, 
                                   tmp_root.rCommand, 
                                   tmp_root.rTimeBegin, 
                                   tmp_root.rTimeEnd,
                                   tmp_root.id))
        return render_to_response('leader/approve.html', 
                                  {'to_approve': to_approve, 'user': request.user},
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('invalid.html')

    