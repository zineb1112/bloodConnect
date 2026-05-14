from django.urls import path, include
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
     path("profile/", views.profile, name="profile"),

    # Donor dashboard (THE donor page)
    path("donor/", views.donor_dashboard, name="donor"),

    path("registerView/", views.register_view, name="registerView"),
    path("loginView/", views.login_view, name="loginView"),
    path("resetpassView/", views.reset_password_view, name="resetpassView"),
    path("newpasswordView/", views.new_password_view, name="newpasswordView"),
    path("editeview/", views.edit_view, name="edit_view"),

    path("register/", views.donor_register, name="donor-register"),
    path("login/", views.donor_login, name="donor-login"),


    path('logout/', views.donor_logout, name='logout'),
    path("donor/edit/", views.edit_donor, name="edit_donor"),
    path("password/reset/", views.reset_password, name="reset_password"),


    # Hospital uses this internal endpoint:
    path("api/donors/internal/donors/", views.internal_donors_api, name="internal_donors_api"),
    path('', include('django_prometheus.urls')),
]
