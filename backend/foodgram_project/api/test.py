from django.contrib.auth import get_user_model


from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from djoser.views import UserViewSet as DjoserUserViewSet

from .pagination import PagePaginator
from .serializers import (
    AvatarSerializer,
    SubscriptionListSerializer,
    SubscriptionNewSerializer,
    UserSerializer,
)

from users.models import Subscription


User = get_user_model()

FILE_NAME = 'shopping_list.txt'


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для управления текущим пользователем."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = PagePaginator

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        """Отражение текущего пользователя."""
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=('put',),
        url_path='me/avatar',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def avatar(self, request):
        """Добавление/обновление аватара."""
        serializer = AvatarSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        """Удаление аватара."""
        user = self.request.user
        user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscriptions(self, request):
        """Подписки"""
        current_user = request.user
        subscribed_users = User.objects.filter(
            following__user=current_user
        )
        paginated_users = self.paginate_queryset(subscribed_users)
        serializer = SubscriptionListSerializer(
            paginated_users,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=[permissions.IsAuthenticated],
        url_path="subscribe"
    )
    def subscribe(self, request, id=None):
        """Создание подписки."""
        user_to_follow = get_object_or_404(User, id=id)
        subscription_data = {
            'user': request.user.id,
            'author': user_to_follow.id
        }
        serializer = SubscriptionNewSerializer(
            data=subscription_data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def remove_subscription(self, request, id=None):
        """Удаление подписки."""
        user_to_follow = get_object_or_404(User, id=id)
        current_user = request.user
        deleted_count, _ = Subscription.objects.filter(
            user=current_user,
            author=user_to_follow
        ).delete()
        if not deleted_count:
            return Response(
                {'detail': 'Вы не подписаны на данного пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)