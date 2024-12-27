from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import RecipeSerializer, IngredientSerializer, TagSerializer, UserSerializer, AvatarSerializer
from food_recipes.models import Recipe, Ingredient, Tag
from rest_framework import viewsets, permissions, filters, status
from rest_framework.permissions import AllowAny
from djoser.views import UserViewSet as DjoserUserViewSet
from djoser.serializers import SetPasswordSerializer
from .permissions import IsOwnerOrReadOnly

from django.contrib.auth import get_user_model


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    @action(detail=False,
            methods=('get',),
            permission_classes=(permissions.IsAuthenticated),
            url_path='me/avatar'
            )
    def me(self, request, *args, **kwargs):
        """Получение данных текущего пользователя."""
        return Response(self.get_serializer(request.user).data)

    @action(
        detail=False,
        methods=('get', 'put', 'delete'),
        permission_classes=[permissions.AllowAny],
        url_path='/me/avatar',
    )
    def avatar(self, request):
        if request.method == 'PUT':
            serializer = AvatarSerializer(request.user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        request.user.avatar = None
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class FavouritesViewSet(viewsets.ModelViewSet):
    pass


class ShoppingListViewSet(viewsets.ModelViewSet):
    pass


class UserViewSet(viewsets.ModelViewSet):
    pass


class SubscriptionViewSet(viewsets.ModelViewSet):
    pass


class SubscriptionListViewSet(viewsets.ModelViewSet):
    pass
