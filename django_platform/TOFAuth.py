#coding: utf-8

from django.contrib.auth.models import User
from ldap.models import LoginUser
import suds

class TOFBackend(object):
    def authenticate(self, token=None):
        Url = "http://passport.oa.com/services/passportservice.asmx?WSDL"
        if not token:
            return None
        soap = suds.client.Client(Url)
        result = soap.service.DecryptTicket(token)
        login_valid = False
        if result.LoginName:
            login_valid = True
        if login_valid:
            try:
                user = User.objects.get(username=result.LoginName)
            except User.DoesNotExist:
                user = User(username=result.LoginName)
                user.set_password('default')
                user.is_staff = False
                user.is_superuser = False
                user.save()
                login_user = LoginUser(
                    user=user,
                    loginID=result.StaffId,
                    loginName=result.LoginName,
                    chineseName=unicode(result.ChineseName),
                    departmentID=result.DeptId,
                    departmentName=unicode(result.DeptName),
                    )
                login_user.save()
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None