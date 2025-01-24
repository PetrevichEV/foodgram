from django_filters.rest_framework import FilterSet, filters

from food_recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    """Фильтр для модели Recipe."""

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
        label='Теги'
    )

    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited',
        label='Избранное'
    )

    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart',
        label='В корзине'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def filter_is_favorited(self, queryset, name, value):
        if value is True:
            return queryset.filter(is_favorited=True)
        elif value is False:
            return queryset.filter(is_favorited=False)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value is True:
            return queryset.filter(is_in_shopping_cart=True)
        elif value is False:
            return queryset.filter(is_in_shopping_cart=False)
        return queryset
