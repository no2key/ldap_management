#coding: utf-8
'''
Created on 2013-5-27

@author: shuangluo
'''
import datetime
from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ldap.models import User, Machine, TempRoot, SudoCommand
from ldap.utils import modules_for_user


class SudoAddForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(SudoAddForm, self).__init__(*args, **kwargs)
        self.fields['uCommand'] = forms.ChoiceField(
            choices=[(o.cmdString, o.cmdName) for o in SudoCommand.objects.all()],
            label="可执行命令"
        )
    uName = forms.CharField(max_length=100, label="用户名")
    uReason = forms.CharField(max_length=300, label="申请事由")
    uIP = forms.CharField(max_length=100, widget=forms.Textarea, label="IP列表")
    uCommand = forms.ChoiceField(label="可执行命令")
    uStartTime = forms.DateTimeField(label="起始时间")
    uEndTime = forms.DateTimeField(label="失效时间")

@login_required
def add_view(request):
    errors = False
    m_username = request.user.username
    if request.method == 'POST':
        machines = []
        f = SudoAddForm(request.POST)
        if f.is_valid():
            cd = f.cleaned_data
            m_user = User.objects.get(uName=m_username)
            m_reason = cd['uReason']
            tmp_IPs = cd['uIP'].replace("\r\n", "\n")
            tmp_IPs = tmp_IPs.replace("\r", "\n")
            m_IPs = tmp_IPs.split("\n")
            m_command = cd['uCommand']
            m_starttime = cd['uStartTime']
            m_endtime = cd['uEndTime']
            m_duration = m_endtime - m_starttime
            m_groups = modules_for_user(request)
            m_command = SudoCommand.objects.get(cmdString=m_command)
            if m_duration <= datetime.timedelta(0):
                messages.error(request, "失效时间必须晚于起始时间。")
                errors = True
            else:
                for IP in m_IPs:
                    try:
                        machine = Machine.objects.get(mIP=IP)
                        if machine.mGroupID.mgID in m_groups:
                            try:
                                m_user.uMachineList.get(mIP=IP)
                                machines.append(machine)
                            except:
                                messages.error(request, "请先申请%s的<a href='/ldap/common_add'>登录权限</a>。" % (IP))
                                errors = True
                        else:
                            messages.error(request, "你所在的组没有该机器的临时sudo权限。")
                            errors = True
                    except:
                        messages.error(request, "IP地址 %s无效或不存在。" % (IP))
                        errors = True
            if errors:
                return render_to_response('sudo/addsudo.html', 
                                          {'form':f, 'user': request.user},
                                          context_instance=RequestContext(request))
            
            tmp_root = TempRoot(rUser=m_user,
                                rReason=m_reason,
                                rRunAs="root",
                                rCommand=m_command,
                                rTimeBegin=m_starttime,
                                rTimeEnd=m_endtime,
                                rEnable=True,
                                rIsApproved=False,
                                rUpdateBy=m_username
                               )
            tmp_root.save()
            for machine in machines:
                tmp_root.rMachineList.add(machine)
            tmp_root.save()
            messages.success(request, "添加成功，正在等待组长审核。")
            return HttpResponseRedirect('/ldap/sudo_list/')
    else:
        f = SudoAddForm(initial={'uName':request.user.username})
    return render_to_response('sudo/addsudo.html', 
                              {'form': f, 'user': request.user},
                              context_instance=RequestContext(request))

@login_required
def list_view(request):
    sudos = []
    username = request.user.username
    try:
        user = User.objects.get(uName=username)
    except:
        messages.error(request, "LDAP用户不存在，请联系运维添加。")
    else:
        tmp_roots = TempRoot.objects.all().filter(rUser=user)
        for tmp_root in tmp_roots:
            rmachines = tmp_root.rMachineList.all()
            strTmp = ""
            strStatus = ""
            for rmachine in rmachines:
                strTmp += rmachine.mIP
                strTmp += ";"
            rcommand = tmp_root.rCommand
            rbegin = tmp_root.rTimeBegin
            rend = tmp_root.rTimeEnd
            rstatus = tmp_root.rIsApproved
            renable = tmp_root.rEnable
            if (not rstatus) & (not renable):
                strStatus = "审核不通过"
            if rstatus & renable:
                strStatus = "已通过，生效中"
            if rstatus & (not renable):
                strStatus = "已通过，已失效"
            if (not rstatus) & renable:
                strStatus = "待审核"
            sudos.append((strTmp, rcommand, rbegin, rend, strStatus))
    return render_to_response('sudo/listsudo.html', 
                              {'sudos': sudos, 'user': request.user},
                              context_instance=RequestContext(request))

