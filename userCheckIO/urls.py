from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"), 
    # path("assets/", views.asset_list, name="asset_list"), # This generic asset list is no longer the primary view.
    # The user_asset_view path should now point to views.user_asset_view
    path("user_assets/", views.user_asset_view, name="user_asset_view"),
    # URLs for assign/unassign actions
    path("user/<int:user_id>/assign/", views.assign_asset_to_user_view, name="assign_asset"),
    path("asset/<int:asset_id>/unassign/", views.unassign_asset_from_user_view, name="unassign_asset"),
]