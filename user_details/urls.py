from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('authorize/', views.authorize, name='authorize'),
    path('callback/', views.callback, name='callback'),
    # Other URL patterns
    path('get_emails/', views.get_emails, name='get_emails'),
    path('feedback/', views.feedback, name='feedback'),
    path('thank_you/', views.thank_you, name='thank_you'),
    # path('authorize/', views.authorize, name='authorize'),
]
