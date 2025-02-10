"""e_cross_2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import re_path, include#, path

from django.conf import settings            #### for dev server only
from django.conf.urls.static import static  #### for dev server only

urlpatterns = [
    re_path('admin/', admin.site.urls),
    re_path(r'^core/', include('core.urls')),
    re_path(r'^find/', include('find.urls')),
    re_path(r'^cross/', include('cross.urls')),
    re_path(r'^app/', include('app_proc.urls')),
    re_path(r'^cable/', include('cable.urls')),
    re_path(r'^statist/', include('statist.urls')),
    re_path(r'^manual/', include('manual.urls')),
    #re_path(r'^plan/', include('plan.urls')),
    #re_path(r'^rent/', include('eq_rent.urls')),
    #re_path(r'^mess/', include('mess.urls')),
    #url(r'^hard/', include('hard.urls')),
    re_path(r'^api/vols/', include('vols_api.urls')),
    re_path(r'^', include('find.urls')),
    re_path(r'^__debug__/', include('debug_toolbar.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  #### for dev server only
