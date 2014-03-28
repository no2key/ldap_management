from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^ldap/', include('ldap.urls', namespace='ldap')),
)    

from django_platform import accounts
urlpatterns += patterns('', 
    url(r'accounts/login/', accounts.login_view, name='login'),
    url(r'accounts/logout/', accounts.logout_view, name='logout'),
)

from django_platform import account
urlpatterns += patterns('', 
	url(r'^$', account.info_view, name='info'),
    url(r'account/loggedin/', account.info_view, name='loggedin'),
    url(r'account/invalid/', account.invalid, name='invalid'),
    url(r'account/info/', account.info_view, name='info'),
)
