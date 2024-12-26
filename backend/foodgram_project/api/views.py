from rest_framework import viewsets, permissions, filters
from rest_framework.permissions import AllowAny
from djoser.views import UserViewSet as DjoserUserViewSet
from djoser.serializers import SetPasswordSerializer
from .permissions import IsOwnerOrReadOnly


from food_recipes.models import Recipe, Ingredient


from .serializers import RecipeSerializer, IngredientSerializer


class TagViewSet(viewsets.ModelViewSet):
    pass


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
