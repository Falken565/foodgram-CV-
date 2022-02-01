
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import get_object_or_404
from rest_framework import decorators, permissions, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from api.permissions import IsAuthor
from api.serializers import FollowListSerializer, FollowSerializer
from recipes.models import Follow

from .models import User
from .serializers import (SetPasswordSerializer, UserCreateSerializer,
                          UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    # pagination_class = PageNumberPagination
    lookup_field = 'id'

    def get_serializer_class(self):
        if (self.action == 'list' or
                self.action == 'retrieve' or self.action == 'me'):
            return UserSerializer
        elif self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'set_password':
            return SetPasswordSerializer

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [permissions.AllowAny, ]
        return super(self.__class__, self).get_permissions()

    @decorators.action(
        ['GET'],
        detail=False,
        permission_classes=[permissions.IsAuthenticated, ]
    )
    def me(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(instance=user)
        return Response(
            serializer.data, status=status.HTTP_200_OK
        )

    @decorators.action(
        ['POST'],
        detail=False,
        permission_classes=[permissions.IsAuthenticated, ]
    )
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()
        update_session_auth_hash(self.request, self.request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(
        ['GET'],
        detail=False,
        permission_classes=[IsAuthor, ],
    )
    def subscriptions(self, request, *args, **kwargs):
        authors = User.objects.filter(following__user=request.user)
        paginator = PageNumberPagination()
        paginator.page_size = 6
        authors_page = paginator.paginate_queryset(authors, request)
        serializer = FollowListSerializer(authors_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @decorators.action(
        ['GET', 'DELETE'],
        detail=False,
        url_path=r'(?P<author_id>\d+)/subscribe',
        permission_classes=[permissions.IsAuthenticated, ])
    def subscribe(self, request, *args, **kwargs):
        user = request.user
        user_pk = user.id
        author_id = self.kwargs.get('author_id')
        author = get_object_or_404(User, id=author_id)
        if request.method == 'GET':
            if user != author:
                serializer_val = FollowSerializer(
                    data={'user': user_pk, 'author': author_id}
                )
                serializer_val.is_valid(raise_exception=True)
                serializer_val.save()
                serializer = FollowListSerializer(author)
                return Response(serializer.data)
            return Response(
                    data={"errors": "Подписка на себя запрещена"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        elif request.method == 'DELETE':
            follow = Follow.objects.filter(user=user, author=author)
            if follow.exists():
                follow.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    data={"errors": "Do not subscribed on author"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
