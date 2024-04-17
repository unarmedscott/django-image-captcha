from django.urls import path
from django.shortcuts import render

from . import views

def serve_out(tmpl_name):
    return lambda request: render(request, tmpl_name)

urlpatterns = [
    path("", views.index),
    path("login/", serve_out('login.html')),
    path('captcha/', views.manage_captcha), # GET a captcha by json, POST verification
]
