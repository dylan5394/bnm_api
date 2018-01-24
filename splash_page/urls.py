from django.conf.urls import url

from splash_page import views


handler404 = 'splash_page.views.page_not_found'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^submit-email$', views.submit_email, name='submit_email'),
    url(r'^forgot-password$', views.forgot_password, name='forgot_password'),
    url(r'^reset-password$', views.reset_password, name='reset_password'),
]
