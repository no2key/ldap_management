from django.contrib import auth
from django.utils.http import urlquote
from django.http import HttpResponseRedirect


def login_view(request):
    login_url = "http://passport.oa.com/modules/passport/signin.ashx?url=" + \
                urlquote("http://" + request.get_host() + "/accounts/login")
    token = request.GET.get('ticket', '')
    if not token:
        return HttpResponseRedirect(login_url)
    user = auth.authenticate(token = token)
    if user is not None and user.is_active:
        # Correct password, and the user is marked "active"
        auth.login(request, user)
        # Redirect to a success page.
        return HttpResponseRedirect("/account/loggedin/")
    else:
        # Show an error page
        return HttpResponseRedirect("/account/invalid/")


def logout_view(request):
    auth.logout(request)
    logout_url = "http://passport.oa.com/modules/passport/signout.ashx?url=" + \
                 urlquote("http://" + request.get_host() + "/accounts/login")
    return HttpResponseRedirect(logout_url)
