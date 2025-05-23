from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'api'

router = DefaultRouter()
router.register(r'tags', views.TagViewSet, basename='tags')
router.register(r'recipes', views.RecipeViewSet, basename='recipes')
router.register(r'ingredients', views.IngredientViewSet,
                basename='ingredients')
router.register(r'users', views.UserViewSet, basename='users')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('s/<str:short_id>/', views.redirect_to_recipe,
         name='redirect-to-recipe'),
]
