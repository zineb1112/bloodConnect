from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('reset/', views.reset_password_page, name='reset'),
    path('newpassword/', views.newpassword_page, name='newpassword'),
    path('signup/', views.signup_page, name='signup'),
    path('post_request/', views.post_request_page, name='post_request'),
    path('campaign/', views.campaign_page, name='campaign'),
    path('donors/', views.donors_page, name='donors'),
    path('profile/', views.profile_page, name='profile'),
    path('forcast/', views.forcast_interface, name='forcast'), #H: for the forcasting server
    path('api/forecast/', views.get_forecast, name='get_forecast'), #H: API endpoint for forecast predictions
    path("donors/", views.donors_page, name="donors"),
    path("api/internal/blood-requests/", views.internal_blood_requests_api, name="internal_blood_requests_api"),
]
