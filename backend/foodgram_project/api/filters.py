from django_filters.rest_framework import FilterSet, filters

from food_recipes.models import Ingredient


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
