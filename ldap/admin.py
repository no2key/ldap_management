#coding:utf-8
from django.contrib import admin
from ldap.models import User, UserGroup, Machine, Module, BizGroup, BizSet, TempRoot, Sudoer, SudoCommand, OpLog


class UserAdmin(admin.ModelAdmin):
    list_display = ('uName', 'uType', 'uEnable', 'uUpdateBy', 'uUpdateTime')
    list_filter = ('uUpdateTime',)
    filter_horizontal = ('uMachineList', 'uSudoList', )


class UserGroupAdmin(admin.ModelAdmin):
    list_display = ('ugName', 'ugLeader', 'ugEnable', 'ugUpdateBy', 'ugUpdateTime')
    filter_horizontal = ('ugUserList', 'ugModuleList', )


class MachineAdmin(admin.ModelAdmin):
    list_display = ('mIP', 'mExtIP', 'mHostName', 'mGroupID', 'mMainOp', 'mBakOp')


class MachineGroupAdmin(admin.ModelAdmin):
    list_display = ('mgName', 'mgID', 'mgParent', 'mgEnable')


class BizGroupAdmin(admin.ModelAdmin):
    list_display = ('bgName', 'bgID', 'bgParent')


admin.site.register(User, UserAdmin)
admin.site.register(UserGroup, UserGroupAdmin)
admin.site.register(Machine, MachineAdmin)
admin.site.register(Module, MachineGroupAdmin)
admin.site.register(BizGroup, BizGroupAdmin)
admin.site.register(BizSet)
admin.site.register(TempRoot)
admin.site.register(Sudoer)
admin.site.register(OpLog)
admin.site.register(SudoCommand)
