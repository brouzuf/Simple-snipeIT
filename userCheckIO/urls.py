from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("admin_login/", views.login_view, name="admin_login"),
    path("logout/", views.logout_view, name="logout"), 
    path("user_assets/", views.user_asset_view, name="user_asset_view"),
    path("assets/featured/", views.filtered_asset_list_view, name="featured_asset_list"),
    # URLs for assign/unassign actions
    path("user/<int:user_id>/assign/", views.assign_asset_to_user_view, name="assign_asset"),
    path("asset/<int:asset_id>/unassign/", views.unassign_asset_from_user_view, name="unassign_asset"), # Kept for direct unassignment if still used
    path('user/<int:user_id>/unassign_by_tag/', views.unassign_asset_by_tag_view, name='unassign_asset_by_tag'),
    path("configure_categories/", views.configure_asset_categories_view, name="configure_asset_categories"),
]