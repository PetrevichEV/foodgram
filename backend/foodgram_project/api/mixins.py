# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework import serializers
# from django.shortcuts import get_object_or_404




# class UserRecipeRelationMixin:
#     """Валиддация связи User-Recipe и сериализация в кратком виде."""
#     model = None
#     error_message = None

#     def validate(self, data):
#         user = data['user']
#         recipe = data['recipe']
#         if self.model.objects.filter(user=user, recipe=recipe).exists():
#             raise serializers.ValidationError(
#                 self.error_message
#             )
#         return data

#     def to_representation(self, instance):
#         """Возвращаем краткую информацию о рецептах."""
#         from .serializers import SimpleRecipeSerializer
#         recipe = instance.recipe
#         serializer = SimpleRecipeSerializer(recipe, context=self.context)
#         return serializer.data


# class AddDeleteRecipeMixin:
#     """Добавление/удаление рецепта из избранного/корзины."""

#     model = None
#     serializer_class = None

#     def add_delete_recipe(self, request, pk=None):
#         user = request.user

#         if request.method == 'POST':
#             recipe = get_object_or_404(self.model, pk=pk)
#             if self.model.objects.filter(user=user, recipe=recipe).exists():
#                 return Response({'detail': 'Рецепт уже добавлен!'},
#                                 status=status.HTTP_400_BAD_REQUEST)

#             object = self.model.objects.create(user=user, recipe=recipe)
#             serializer = self.serializer_class(object)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#         elif request.method == 'DELETE':
#             deleted_count, _ = self.model.objects.filter(
#                 user=user, recipe=self.get_object()
#             ).delete()

#             if deleted_count == 0:
#                 return Response(
#                     {'detail': 'Рецепт не найден!'},
#                     status=status.HTTP_400_BAD_REQUEST)
#             return Response(status=status.HTTP_204_NO_CONTENT)

#         return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # def add_delete_recipe(self, request, model, serializer_class, pk=None):
    #     user = request.user
    #     recipe = get_object_or_404(Recipe, pk=pk)

    #     if request.method == 'POST':
    #         if model.objects.filter(user=user, recipe=recipe).exists():
    #             return Response({'detail': 'Рецепт уже добавлен!'},
    #                             status=status.HTTP_400_BAD_REQUEST)

    #         object = model.objects.create(user=user, recipe=recipe)
    #         serializer = serializer_class(object)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)

    #     elif request.method == 'DELETE':
    #         deleted_count, _ = model.objects.filter(
    #             user=user, recipe=recipe
    #         ).delete()

    #         if deleted_count == 0:
    #             return Response(
    #                 {'detail': 'Рецепт не найден!'},
    #                 status=status.HTTP_400_BAD_REQUEST)
    #         return Response(status=status.HTTP_204_NO_CONTENT)

    #     return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # @action(
    #     detail=True,
    #     methods=('POST', 'DELETE'),
    #     url_path='favorite',
    #     url_name='favorite',
    #     permission_classes=[permissions.IsAuthenticated])
    # def favorite(self, request, pk=None):
    #     """Добавление/удаление рецепта из избранного."""
    #     return self.check_recipe_action(
    #         request, Favourites, FavoriteSerializer, pk
    #     )

    # @action(
    #     detail=True,
    #     methods=('POST', 'DELETE'),
    #     url_path='shopping_cart',
    #     url_name='shopping_cart',
    #     permission_classes=[permissions.IsAuthenticated]
    # )
    # def shopping_cart(self, request, pk=None):
    #     """Добавление/удаление рецепта из корзины покупок."""
    #     return self.check_recipe_action(
    #         request, ShoppingList, ShoppingListSerializer, pk
    #     )
