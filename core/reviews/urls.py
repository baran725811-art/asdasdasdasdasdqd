#core\reviews\urls.py
from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('add/', views.add_review, name='add_review'),
    path('list/', views.review_list, name='review_list'),
]