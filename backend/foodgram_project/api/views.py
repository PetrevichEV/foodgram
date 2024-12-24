from rest_framework import viewsets
# from rest_framework.generics import get_object_or_404
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.filters import SearchFilter
# from rest_framework.pagination import LimitOffsetPagination

from food_recipes.models import Recipe
# from food_recipes.models import (
#     Tag, Ingredient, Recipe, Favourites, ShoppingList)
# from users.models import User, Follow

# from .permissions import IsOwnerOrReadOnlypip list
from .serializers import RecipeSerializer


class TagViewSet(viewsets.ModelViewSet):
    pass

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

class FavouritesViewSet(viewsets.ModelViewSet):
    pass

class ShoppingListViewSet(viewsets.ModelViewSet):
    pass

class UserViewSet(viewsets.ModelViewSet):
    pass

class FollowViewSet(viewsets.ModelViewSet):
    pass

class FollowListViewSet(viewsets.ModelViewSet):
    pass
