from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('posts', views.PostViewSet, basename='posts')

urlpatterns = [
    path("", include(router.urls)),

    path("tags/", views.TagView.as_view()),
    path("tags/<slug:tag_slug>/", views.TagDetailView.as_view()),

    path("aside/", views.AsideView.as_view()),

    path("feedback/", views.FeedBackView.as_view()),

    path('register/', views.RegisterView.as_view()),

    path('profile/', views.ProfileView.as_view()),

    path("comments/", views.CommentView.as_view()),
    path("comments/<slug:post_slug>/", views.CommentView.as_view()),
]
