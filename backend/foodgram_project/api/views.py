from rest_framework import viewsets, permissions
from djoser.views import UserViewSet as DjoserUserViewSet
from djoser.serializers import SetPasswordSerializer
from .permissions import IsOwnerOrReadOnly

from food_recipes.models import Recipe, Ingredient


from .serializers import RecipeSerializer, IngredientSerializer


class TagViewSet(viewsets.ModelViewSet):
    pass


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


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
