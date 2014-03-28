#coding:utf-8
'''
Created on 2013-5-29

@author: shuangluo
'''
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils.decorators import method_decorator
from django.forms import ModelForm
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User as auth_user
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from ldap.models import TempRoot, UserGroup, User, Sudoer, SudoCommand
from ldap.utils import is_operator, ssha_encode

#----------------------------------Group Operations-------------------------------------------------


class UserGroupForm(ModelForm):
    class Meta:
        model = UserGroup
        fields = ['ugName', 'ugLeader', 'ugUserList', 'ugModuleList', 'ugEnable']


class UserGroupList(ListView):
    model = UserGroup
    context_object_name = 'ugs'
    template_name = 'operator/opgrouplist.html'
    paginate_by = 10

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if is_operator(request):
            return super(UserGroupList, self).dispatch(request, *args, **kwargs)
        else:
            return render_to_response('invalid.html')

    def get_queryset(self, *args, **kwargs):
        queryset = UserGroup.objects.order_by('-ugUpdateTime')
        return queryset


class UserGroupAdd(CreateView):
    model = UserGroup
    template_name = 'operator/opgroupadd.html'
    form_class = UserGroupForm
    success_url = '/ldap/op_group_list'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if is_operator(request):
            return super(UserGroupAdd, self).dispatch(request, *args, **kwargs)
        else:
            return render_to_response('invalid.html')

    def form_valid(self, form):
        form.instance.ugUpdateBy = self.request.user.username
        leader = auth_user.objects.get(username=form.instance.ugLeader.uName)
        if not leader.is_staff:
            leader.is_staff = True
            leader.save()
        return super(UserGroupAdd, self).form_valid(form)


class UserGroupEdit(UpdateView):
    model = UserGroup
    template_name = 'operator/opgroupedit.html'
    form_class = UserGroupForm
    success_url = '/ldap/op_group_list'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if is_operator(request):
            return super(UserGroupEdit, self).dispatch(request, *args, **kwargs)
        else:
            return render_to_response('invalid.html')

    def form_valid(self, form):
        form.instance.ugUpdateBy = self.request.user.username
        return super(UserGroupEdit, self).form_valid(form)


class UserGroupDelete(DeleteView):
    model = UserGroup
    success_url = '/ldap/op_group_list'
    template_name = 'operator/confirm_delete.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if is_operator(request):
            return super(UserGroupDelete, self).dispatch(request, *args, **kwargs)
        else:
            return render_to_response('invalid.html')

#----------------------------------User Operations-------------------------------------------------


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['uName', 'uType', 'uSuperUser', 'uEnable', 'uMachineList']


def op_user_info(request):
    user = None
    if request.method == "POST":
        s_user = request.POST.get('s_user', "")
        if s_user:
            try:
                user = User.objects.get(uName=s_user)
            except:
                messages.error(request, "没有查询到这个成员，请检查拼写或添加新用户。")
        else:
            messages.error(request, "请输入要查询的用户名。")
    return render_to_response('operator/opuserinfo.html',
                              {'user_info': user, 'user': request.user},
                              context_instance=RequestContext(request))


class UserList(ListView):
    model = User
    context_object_name = 'us'
    template_name = 'operator/opuserlist.html'
    paginate_by = 10

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if is_operator(request):
            if request.method == "POST":
                return op_user_info(request)
            return super(UserList, self).dispatch(request, *args, **kwargs)
        else:
            return render_to_response('invalid.html')

    def get_queryset(self, *args, **kwargs):
        queryset = User.objects.order_by('-uUpdateTime')
        return queryset


class UserAdd(CreateView):
    model = User
    template_name = 'operator/opuseradd.html'
    form_class = UserForm
    success_url = '/ldap/op_user_list'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if is_operator(request):
            return super(UserAdd, self).dispatch(request, *args, **kwargs)
        else:
            return render_to_response('invalid.html')

    def form_valid(self, form):
        max_id = User.objects.order_by('-uID')[0].uID
        form.instance.uID = max_id + 1
        form.instance.uUpdateBy = self.request.user.username
        return super(UserAdd, self).form_valid(form)


class UserEdit(UpdateView):
    model = User
    template_name = 'operator/opuseredit.html'
    form_class = UserForm
    success_url = '/ldap/op_user_list'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if is_operator(request):
            return super(UserEdit, self).dispatch(request, *args, **kwargs)
        else:
            return render_to_response('invalid.html')

    def form_valid(self, form):
        form.instance.uUpdateBy = self.request.user.username
        pass1 = self.request.POST['Password1']
        pass2 = self.request.POST['Password2']
        if pass1 != "":
            if pass1 == pass2:
                form.instance.uPassword = ssha_encode(pass1)
        return super(UserEdit, self).form_valid(form)


class UserDelete(DeleteView):
    model = User
    success_url = '/ldap/op_user_list'
    template_name = 'operator/confirm_delete.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if is_operator(request):
            return super(UserDelete, self).dispatch(request, *args, **kwargs)
        else:
            return render_to_response('invalid.html')


@login_required
def op_user_clone(request):
    errors = False
    if is_operator(request):
        if request.method == 'POST':
            be_cloned = request.POST['uClone']
            if not request.POST['uList']:
                messages.error(request, "请输入要添加的用户名，每行一个。")
                errors = True
            clone_list = request.POST['uList'].replace("\r\n", "\n")
            clone_list = clone_list.replace("\r", "\n")
            clone_list = clone_list.split("\n")
            if be_cloned:
                try:
                    u = User.objects.get(uName=be_cloned)
                    ugs = u.usergroup_set.all()
                except:
                    messages.error(request, "被克隆用户不存在。")
                    errors = True
                else:
                    for clone in clone_list:
                        if not clone:
                            continue
                        if User.objects.filter(uName=clone):
                            messages.error(request, "用户  %s 已经存在，无法克隆。" % clone)
                            errors = True
                        else:
                            max_id = User.objects.order_by('-uID')[0].uID
                            user = User(uID=max_id + 1,
                                        uName=clone,
                                        uType=u.uType,
                                        uPassword=ssha_encode(clone),
                                        uUpdateBy=request.user.username)
                            user.save()
                            for m in u.uMachineList.all():
                                user.uMachineList.add(m)
                            user.save()
                            for ug in ugs:
                                ug.ugUserList.add(user)
                                ug.save()
                            if errors:
                                messages.success(request, "用户  %s 克隆成功。" % clone)
            else:
                messages.error(request, "请输入要克隆的用户名。")
                errors = True
            if not errors:
                messages.success(request, "克隆成功。")
                return HttpResponseRedirect('/ldap/op_user_list/')
        return render_to_response('operator/opuserclone.html',
                                  {'user': request.user},
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('invalid.html')

#----------------------------------Sudoer Operations-------------------------------------------------


class SudoerForm(ModelForm):
    class Meta:
        model = Sudoer
        fields = ['rUser', 'rCN', 'rMachineList', 'rCommand']


class SudoerList(ListView):
    model = Sudoer
    context_object_name = 'sudoers'
    template_name = 'operator/opsudoerlist.html'
    paginate_by = 10

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if is_operator(request):
            return super(SudoerList, self).dispatch(request, *args, **kwargs)
        else:
            return render_to_response('invalid.html')

    def get_queryset(self, *args, **kwargs):
        queryset = Sudoer.objects.order_by('-rUpdateTime')
        return queryset


class SudoerAdd(CreateView):
    model = Sudoer
    template_name = 'operator/opsudoeradd.html'
    form_class = SudoerForm
    success_url = '/ldap/op_sudoer_list'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if is_operator(request):
            return super(SudoerAdd, self).dispatch(request, *args, **kwargs)
        else:
            return render_to_response('invalid.html')

    def form_valid(self, form):
        form.instance.rUpdateBy = self.request.user.username
        return super(SudoerAdd, self).form_valid(form)


class SudoerEdit(UpdateView):
    model = Sudoer
    template_name = 'operator/opsudoeredit.html'
    form_class = SudoerForm
    success_url = '/ldap/op_sudoer_list'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if is_operator(request):
            return super(SudoerEdit, self).dispatch(request, *args, **kwargs)
        else:
            return render_to_response('invalid.html')

    def form_valid(self, form):
        form.instance.rUpdateBy = self.request.user.username
        return super(SudoerEdit, self).form_valid(form)


class SudoerDelete(DeleteView):
    model = Sudoer
    success_url = '/ldap/op_sudoer_list'
    template_name = 'operator/confirm_delete.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if is_operator(request):
            return super(SudoerDelete, self).dispatch(request, *args, **kwargs)
        else:
            return render_to_response('invalid.html')

#----------------------------------Command Operations-------------------------------------------------


class CmdList(ListView):
    model = SudoCommand
    context_object_name = 'cmds'
    template_name = 'operator/opcmdlist.html'
    paginate_by = 10

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if is_operator(request):
            return super(CmdList, self).dispatch(request, *args, **kwargs)
        else:
            return render_to_response('invalid.html')


class CmdAdd(CreateView):
    model = SudoCommand
    template_name = 'operator/opcmdadd.html'
    success_url = '/ldap/op_cmd_list'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if is_operator(request):
            return super(CmdAdd, self).dispatch(request, *args, **kwargs)
        else:
            return render_to_response('invalid.html')


class CmdEdit(UpdateView):
    model = SudoCommand
    template_name = 'operator/opcmdedit.html'
    success_url = '/ldap/op_cmd_list'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if is_operator(request):
            return super(CmdEdit, self).dispatch(request, *args, **kwargs)
        else:
            return render_to_response('invalid.html')


class CmdDelete(DeleteView):
    model = SudoCommand
    success_url = '/ldap/op_cmd_list'
    template_name = 'operator/confirm_delete.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if is_operator(request):
            return super(CmdDelete, self).dispatch(request, *args, **kwargs)
        else:
            return render_to_response('invalid.html')

#----------------------------------Approve/disable Operations-------------------------------------------------


@login_required
def op_approve(request):
    to_approve = []
    username = request.user.username
    if is_operator(request):
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
                            TempRoot.objects.filter(id=int(choice)).update(rEnable=False, rUpdateBy=username)
                    except:
                        pass

        tmp_roots = TempRoot.objects.filter(rEnable=True, rIsApproved=False)
        for tmp_root in tmp_roots:
            rIPs = ""
            machines = tmp_root.rMachineList.all()
            for m in machines:
                rIPs += m.mIP
                rIPs += "; "
            to_approve.append((tmp_root.rUser.uName,
                               tmp_root.rReason,
                               rIPs,
                               tmp_root.rCommand,
                               tmp_root.rTimeBegin,
                               tmp_root.rTimeEnd,
                               tmp_root.id))
        return render_to_response('operator/opapprove.html',
                                  {'to_approve': to_approve, 'user': request.user},
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('invalid.html')


@login_required
def op_sudo_disable(request):
    to_disable = []
    username = request.user.username
    if is_operator(request):
        if request.method == "POST":
            choices = request.POST
            if not choices:
                messages.error(request, "请先选择要禁用的项目。")
            for choice in choices:
                status = choices[choice]
                if choice.isdigit():
                    try:
                        if status == "yes":
                            TempRoot.objects.filter(id=int(choice)).update(rEnable=False, rUpdateBy=username)
                    except:
                        pass
        tmp_roots = TempRoot.objects.filter(rEnable=True, rIsApproved=True)
        for tmp_root in tmp_roots:
            rIPs = ""
            machines = tmp_root.rMachineList.all()
            for m in machines:
                rIPs += m.mIP
                rIPs += "; "
            to_disable.append((tmp_root.rUser.uName,
                               tmp_root.rReason,
                               rIPs,
                               tmp_root.rCommand,
                               tmp_root.rTimeBegin,
                               tmp_root.rTimeEnd,
                               tmp_root.id))
        return render_to_response('operator/opsudodisable.html',
                                  {'to_disable': to_disable, 'user': request.user},
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('invalid.html')