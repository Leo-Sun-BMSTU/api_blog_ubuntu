from django.shortcuts import render
from rest_framework import viewsets
from . import serializers
from .models import Post, Comment
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import pagination
from rest_framework import generics
from taggit.models import Tag
from rest_framework.views import APIView
from django.core.mail import send_mail
from rest_framework import filters


class PageNumberSetPagination(pagination.PageNumberPagination):
    """
    Класс реализации пагинации.
    """
    page_size = 2
    page_size_query_param = 'page_size'
    ordering = 'created_at'


class PostViewSet(viewsets.ModelViewSet):
    """
    Класс представления записи/записей блога (постов) и их поиска.
    """
    search_fields = ('content', 'h1')
    filter_backends = (filters.SearchFilter,)
    serializer_class = serializers.PostSerializer
    queryset = Post.objects.all()
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]
    pagination_class = PageNumberSetPagination


class TagDetailView(generics.ListAPIView):
    """
    Класс представления записей при запросе по тегу.
    """
    serializer_class = serializers.PostSerializer
    pagination_class = PageNumberSetPagination
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        """
        Метод возвращает запись с определённым тэгом.
        :return:
        """
        tag_slug = self.kwargs['tag_slug'].lower()
        tag = Tag.objects.get(slug=tag_slug)
        return Post.objects.filter(tags=tag)


class TagView(generics.ListAPIView):
    """
    Класс представления для сериализатора тэга.
    """
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    permission_classes = [permissions.AllowAny]


class AsideView(generics.ListAPIView):
    """
    Класс представления возвращающий 2 последних поста.
    """
    queryset = Post.objects.all().order_by('-id')[:2]
    serializer_class = serializers.PostSerializer
    permission_classes = [permissions.AllowAny]


class FeedBackView(APIView):
    """
    Класс представления для сериалайзера формы обратной связи.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.ContactSerailizer

    def post(self, request, *args, **kwargs):
        serializer_class = serializers.ContactSerailizer(data=request.data)
        if serializer_class.is_valid():
            data = serializer_class.validated_data
            name = data.get('name')
            from_email = data.get('email')
            subject = data.get('subject')
            message = data.get('message')
            send_mail(f'От {name} | {subject}', message, from_email, ['auto.sending1103@gmail.com'])
            return Response({"success": "Sent"})


class RegisterView(generics.GenericAPIView):
    """
    Класс представления регистрации.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.RegisterSerializer

    def post(self, request, *args,  **kwargs):
        """
        Метод отправки и сохранения данных пользователя.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": serializers.UserSerializer(user, context=self.get_serializer_context()).data,
            "message": "Пользователь успешно создан",
        })


class ProfileView(generics.GenericAPIView):
    """
    Класс представления профиля пользователя.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.UserSerializer

    def get(self, request, *args,  **kwargs):
        """
        Метод получения данных о пользователе
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        return Response({
            "user": serializers.UserSerializer(request.user, context=self.get_serializer_context()).data,
        })


class CommentView(generics.ListCreateAPIView):
    """
    Класс представления комментария
    """
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Метод получения данных о комментариях и их создание.
        :return:
        """
        post_slug = self.kwargs['post_slug'].lower()
        post = Post.objects.get(slug=post_slug)
        return Comment.objects.filter(post=post)
