from django.urls import path

from .views import tutorial_views as t_views
from .views import views

app_name = "Poll2024"

# these urls come from the tutorial, they're not used anymore.
tutorial_url = [
    #path("main", views.index, name="index"),
    path("main/", t_views.IndexView.as_view(), name="index"),
    # ex: /poll2024/5/
    #path("<int:question_id>/", views.detail, name="detail"),
    path("<int:pk>/", t_views.DetailView.as_view(), name="detail"),
    # ex: /poll2024/5/results/
    #path("<int:question_id>/results/", views.results, name="results"),
    path("<int:pk>/results/", t_views.ResultsView.as_view(), name="results"),
    # ex: /poll2024/5/vote/
    #path("<int:question_id>/vote/", views.vote, name="vote"),
    path("<int:question_id>/vote/", t_views.vote, name="vote"),
]
urlpatterns = [
    path("vote/", views.VoteCreateProxy.as_view(), name="vote_proxy"),
    path("vote/divition_level/", views.VoteCreate.as_view(), name="vote_division_level"),
    path("logout/", views.Logout.as_view(), name="exit"),
]

# uncomment following line to reintroduce urls from the tutorial.
# urlpatterns = tutorial_url + urlpatterns