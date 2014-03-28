#coding: utf-8
from django.db import models
from django.contrib.auth.models import User as auth_user


class User(models.Model):
    USER_TYPE = (
        ('YW', '运维用户'),
        ('PT', '实名用户'),
    )
    uID = models.IntegerField(primary_key=True)
    uName = models.CharField(unique=True, max_length=30, verbose_name="LDAP用户名")
    uPassword = models.CharField(max_length=60, verbose_name="LDAP密码")
    uType = models.CharField(max_length=2, choices=USER_TYPE, verbose_name="用户类型", default="PT")
    uSuperUser = models.BooleanField(default=False, verbose_name="是否超级管理员")
    uEnable = models.BooleanField(default=True, verbose_name="是否启用")
    uMachineList = models.ManyToManyField('Machine', related_name='MList', blank=True, verbose_name="机器列表")
    uSudoList = models.ManyToManyField('Machine', related_name='SudoList', blank=True, verbose_name="sudo列表")
    uUpdateBy = models.CharField(max_length=30, verbose_name="最后更新")
    uUpdateTime = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.uName


class UserGroup(models.Model):
    ugName = models.CharField(unique=True, max_length=30, verbose_name="用户组名")
    ugLeader = models.ForeignKey('User', verbose_name="组长")
    ugUserList = models.ManyToManyField('User', related_name='UList', verbose_name="用户列表")
    ugModuleList = models.ManyToManyField('Module', verbose_name="业务模块")
    ugEnable = models.BooleanField(default=True, verbose_name="是否启用")
    ugUpdateBy = models.CharField(max_length=30, verbose_name="最后更新")
    ugUpdateTime = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.ugName


class BizSet(models.Model):
    tgID = models.IntegerField(primary_key=True, verbose_name="业务集ID")
    tgName = models.CharField(max_length=30, verbose_name="业务集")
    tgUpdateBy = models.CharField(max_length=30, verbose_name="最后更新")
    tgUpdateTime = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.tgName


class BizGroup(models.Model):
    bgID = models.IntegerField(primary_key=True, verbose_name="业务ID")
    bgName = models.CharField(max_length=30, verbose_name="业务名称")
    bgParent = models.ForeignKey('BizSet', verbose_name="所在业务集")
    bgUpdateBy = models.CharField(max_length=30, verbose_name="最后更新")
    bgUpdateTime = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.bgName


class Module(models.Model):
    mgID = models.IntegerField(primary_key=True, verbose_name="模块ID")
    mgName = models.CharField(max_length=30, verbose_name="模块名称")
    mgParent = models.ForeignKey('BizGroup', verbose_name="所在业务")
    mgEnable = models.BooleanField(default=True, verbose_name="是否启用")
    mgUpdateBy = models.CharField(max_length=30, verbose_name="最后更新")
    mgUpdateTime = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.mgName


class Machine(models.Model):
    mID = models.IntegerField(primary_key=True)
    mIP = models.IPAddressField(unique=True, verbose_name="内网IP地址")
    mExtIP = models.IPAddressField(verbose_name="外网IP地址")
    mHostName = models.CharField(max_length=60, verbose_name="Host Name")
    mAssetID = models.CharField(max_length=60)
    mMainOp = models.CharField(max_length=30, verbose_name="主运维负责人")
    mBakOp = models.CharField(max_length=30, verbose_name="备份运维负责人")
    mMainDev = models.CharField(max_length=30, verbose_name="主开发负责人")
    mBakDev = models.CharField(max_length=30, verbose_name="备份开发负责人")
    mGroupID = models.ForeignKey('Module', verbose_name="业务模块")
    mStatus = models.IntegerField(verbose_name="状态码")
    mUpdateBy = models.CharField(max_length=30, verbose_name="最后更新")
    mUpdateTime = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.mIP


class SudoCommand(models.Model):
    cmdName = models.CharField(max_length=30, verbose_name="名称")
    cmdString = models.CharField(max_length=300, verbose_name="可执行命令")

    def __unicode__(self):
        return self.cmdName


class TempRoot(models.Model):
    rUser = models.ForeignKey('User', verbose_name="LDAP用户名")
    rMachineList = models.ManyToManyField('Machine', verbose_name="机器列表")
    rRunAs = models.CharField(max_length=30)
    rCommand = models.ForeignKey('SudoCommand', verbose_name="命令")
    rReason = models.CharField(max_length=300)
    rTimeBegin = models.DateTimeField(verbose_name="生效时间")
    rTimeEnd = models.DateTimeField(verbose_name="失效时间")
    rEnable = models.BooleanField(default=True, verbose_name="是否启用")
    rIsApproved = models.BooleanField(verbose_name="是否通过审核")
    rUpdateBy = models.CharField(max_length=30, verbose_name="最后更新")
    rUpdateTime = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.rUser


class Sudoer(models.Model):
    rUser = models.ForeignKey('User', verbose_name="LDAP用户名")
    rCN = models.CharField(max_length=30)
    rMachineList = models.ManyToManyField('Machine', verbose_name="机器列表")
    rRunAs = models.CharField(max_length=30)
    rCommand = models.ForeignKey('SudoCommand', verbose_name="命令")
    rUpdateBy = models.CharField(max_length=30, verbose_name="最后更新")
    rUpdateTime = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.rUser


class OpLog(models.Model):
    oName = models.CharField(max_length=30, verbose_name="用户名")
    oTime = models.DateTimeField(auto_now=True, verbose_name="操作时间")
    oIP = models.IPAddressField(verbose_name="登录IP地址")
    oContent = models.CharField(max_length=60, verbose_name="操作记录")

    def __unicode__(self):
        return self.oContent


class LoginUser(models.Model):
    user = models.OneToOneField(auth_user)
    loginID = models.CharField(max_length=50)
    loginName = models.CharField(max_length=50)
    chineseName = models.CharField(max_length=50)
    departmentID = models.CharField(max_length=20)
    departmentName = models.CharField(max_length=100)