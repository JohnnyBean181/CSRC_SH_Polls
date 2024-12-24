from django.urls import path

from . import views

app_name = "Poll2024"
urlpatterns = [
    #path("", views.index, name="index"),
    path("", views.IndexView.as_view(), name="index"),
    # ex: /poll2024/5/
    #path("<int:question_id>/", views.detail, name="detail"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    # ex: /poll2024/5/results/
    #path("<int:question_id>/results/", views.results, name="results"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    # ex: /poll2024/5/vote/
    #path("<int:question_id>/vote/", views.vote, name="vote"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
]