from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("assets/", views.asset_list, name="assets"),
]