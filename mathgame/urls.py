from django.urls import path
from . import views

urlpatterns = [
    path('',views.home, name='home'),
    path('quiz/', views.quiz, name='quiz'),
    path('play/', views.play_quiz, name='play_quiz'),
    path("play-again/", views.play_again, name="play_again"),
]
