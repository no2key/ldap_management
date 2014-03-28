#coding: utf-8
'''
Created on 2013-5-23

@author: shuangluo
'''
from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ldap.models import User, Machine

class UserAddForm(forms.Form):
    uName = forms.CharField(max_length = 100)
    topGroup = forms.ChoiceField(required = False)
    bizGroup = forms.ChoiceField(required = False)
    machineGroup = forms.MultipleChoiceField(required = False)
    chosenIP = forms.MultipleChoiceField()

@login_required
def add_view(request):
    username = request.user.username
    if request.method == 'POST':
        f = UserAddForm(request.POST)
        m_machines = request.POST.getlist('chosenIP')
        try:
            m_user = User.objects.get(uName=username)
        except:
            messages.error(request,"LDAP用户不存在，请联系运维添加。")
        else:
            if not m_machines:
                messages.error(request, "必须选择一组IP地址")
            else:
                for machine in m_machines:
                    m_machine = Machine.objects.get(mIP=machine)
                    m_user.uMachineList.add(m_machine)
                m_user.save()
                messages.success(request, "添加成功")
                return HttpResponseRedirect('/ldap/common_list')
    else:
        f = UserAddForm(initial={'uName':request.user.username})
    return render_to_response('common/addcommon.html', 
                              {'form':f, 'user': request.user, },
                              context_instance=RequestContext(request))
    
@login_required
def list_view(request):
    commons = [] 
    username = request.user.username
    try:
        user = User.objects.get(uName=username)
    except:
        messages.error(request,"LDAP用户不存在，请联系运维添加。")
    else:
        machines = user.uMachineList.all()
        for machine in machines:
            mg = machine.mGroupID
            bg = mg.mgParent
            tg = bg.bgParent
            commons.append((machine,tg,bg,mg))
    return render_to_response('common/listcommon.html', 
                              {'machines':commons, 'user':request.user},
                              context_instance=RequestContext(request))
    
    