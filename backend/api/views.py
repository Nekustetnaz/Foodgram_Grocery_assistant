from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import (Favorite, Ingredient, IngredientsInRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscription, User

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import AuthCheck
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeSerializer, RecipeSerializerCreate,
                          ShoppingCartSerializer, ShowSubscriptionsSerializer,
                          SubscriptionSerializer, TagSerializer)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    pagination_class = None
    search_fields = ('^name',)


class SubscribeView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id):
        data = {
            'subscriber': request.user.id,
            'subscription': id
        }
        serializer = SubscriptionSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        author = get_object_or_404(User, id=id)
        if Subscription.objects.filter(
           subscriber=request.user, subscription=author).exists():
            Subscription.objects.filter(
                subscriber=request.user, subscription=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class SubscriptionsView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    def get(self, request):
        queryset = User.objects.filter(subscription__subscriber=request.user)
        page = self.paginate_queryset(queryset)
        serializer = ShowSubscriptionsSerializer(page, many=True,
                                                 context={'request': request})
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = CustomPagination
    permission_classes = (AuthCheck,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeSerializerCreate

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk):
        if request.method == 'POST':
            data = {'owner': request.user.id, 'favorite': pk}
            serializer = FavoriteSerializer(data=data,
                                            context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        recipe = get_object_or_404(Recipe, id=pk)
        favorite = get_object_or_404(Favorite, owner=request.user,
                                     favorite=recipe)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            data = {'customer': request.user.id, 'purchase': pk}
            serializer = ShoppingCartSerializer(data=data,
                                                context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        recipe = get_object_or_404(Recipe, id=pk)
        purchase = get_object_or_404(ShoppingCart, customer=request.user,
                                     purchase=recipe)
        purchase.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        shopping_cart = IngredientsInRecipe.objects.filter(
            recipe__shopping_cart__customer=request.user
        ).values(
            name=F('ingredients__name'),
            measurement_unit=F('ingredients__measurement_unit')
        ).annotate(ingredients_sum=Sum('amount')).values_list(
            'ingredients__name',
            'ingredients_sum',
            'ingredients__measurement_unit'
        )
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=shopping.txt'
        shopping_cart_list = ['Shopping List:\n']
        for ingredients in shopping_cart:
            ingredient, amount, meaurement_unit, = ingredients
            shopping_cart_list.append(
                f'{ingredient} - {amount} {meaurement_unit}\n'
            )
        response.writelines(shopping_cart_list)
        return response
