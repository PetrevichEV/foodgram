from rest_framework import serializers


class UserRecipeRelationMixin:
    """Валидация связи User-Recipe и сериализация в кратком виде."""

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError('Рецепт уже добавлен!')
        return data

    def to_representation(self, instance):
        """Возвращаем краткую информацию о рецептах."""
        recipe = instance.recipe
        from .serializers import SimpleRecipeSerializer
        serializer = SimpleRecipeSerializer(recipe, context=self.context)
        return serializer.data

    class Meta:
        fields = ('user', 'recipe')
