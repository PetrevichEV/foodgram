from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    TagViewSet,
    IngredientViewSet,
    RecipeViewSet,
    FavouritesViewSet,
    ShoppingListViewSet,
    UserViewSet,
    SubscriptionViewSet,
    SubscriptionListViewSet
)

router = DefaultRouter()

router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register(
    r'recipes/(?P<id>\d+)/favorite',
    FavouritesViewSet,
    basename='favorites'
)
router.register(
    r'recipes/(?P<id>\d+)/shopping_cart',
    ShoppingListViewSet,
    basename='shopping'
)
# router.register('users', UserViewSet, basename='users')
router.register(
    'users/subscriptions/',
    SubscriptionListViewSet,
    basename='subscriptions'),
router.register(
    r'users/(?P<id>\d+)/subscribe',
    SubscriptionViewSet,
    basename='subscribe'
)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
