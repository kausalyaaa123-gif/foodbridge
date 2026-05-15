from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('donate/', views.donate_view, name='donate'),
    path('claim/', views.claim_feed, name='claim'),
    path('logout/', views.logout_view, name='logout'),
    path('process-claim/<int:donation_id>/', views.process_claim, name='process_claim'),
    path('signup/', views.signup_view, name='signup'),
]