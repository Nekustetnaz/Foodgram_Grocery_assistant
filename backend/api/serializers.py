from recipes.models import (Favorite, Ingredient, IngredientsInRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers
from users.models import Subscription, User
from users.serializers import CustomUserSerializer

from .fields import Base64ImageField


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('id', 'name', 'measurement_unit')


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source='ingredients',
                                            read_only=True)
    measurement_unit = serializers.SlugRelatedField(
        source='ingredients',
        slug_field='measurement_unit',
        read_only=True,
    )
    name = serializers.SlugRelatedField(
        source='ingredients',
        slug_field='name',
        read_only=True,
    )

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('id', 'name', 'measurement_unit')


class IngredientsInRecipeSerializerCreate(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'amount')

    def validate(self, data):
        if int(data['amount']) == 0:
            raise serializers.ValidationError('Amount should be more than 0')
        return data


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientsInRecipeSerializer(
        source='ingredients_for_recipe',
        many=True,
        read_only=True
    )
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'text', 'cooking_time', 'image', 'author',
                  'ingredients', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            owner=request.user, favorite__id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            customer=request.user, purchase__id=obj.id).exists()


class RecipeSerializerCreate(serializers.ModelSerializer):
    ingredients = IngredientsInRecipeSerializerCreate(many=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'text', 'cooking_time', 'image', 'author',
                  'ingredients', 'tags')

    def validate(self, data):
        ingredients_list = []
        for ingredient in data['ingredients']:
            if ingredient['id'].id in ingredients_list:
                raise serializers.ValidationError('Duplicated ingredients')
            ingredients_list.append(ingredient['id'].id)
        if data['cooking_time'] == 0:
            raise serializers.ValidationError(
                'Cooking time should be more than 0'
            )
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        request = self.context.get('request')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        temp_data = [IngredientsInRecipe(recipe=recipe,
                                         amount=ingredient['amount'],
                                         ingredients=ingredient['id'])
                     for ingredient in ingredients]
        IngredientsInRecipe.objects.bulk_create(temp_data)
        recipe.tags.set(tags)
        return recipe

    def update(self, obj, validated_data):
        ingredients = validated_data.pop('ingredients')
        IngredientsInRecipe.objects.filter(recipe=obj).delete()
        temp_data = [IngredientsInRecipe(recipe=obj,
                                         amount=ingredient['amount'],
                                         ingredients=ingredient['id'])
                     for ingredient in ingredients]
        IngredientsInRecipe.objects.bulk_create(temp_data)
        return super().update(obj, validated_data)

    def to_representation(self, obj):
        return RecipeSerializer(
            obj, context={'request': self.context.get('request'), }).data


class ShowRecipesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class ShowSubscriptionsSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return Subscription.objects.filter(
            subscriber=self.context.get('request').user,
            subscription=obj
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = Recipe.objects.filter(author=obj)
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return ShowRecipesSerializer(
            recipes, many=True, context={'request': request}).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ('subscriber', 'subscription')

    def validate(self, data):
        if Subscription.objects.filter(
            subscriber=self.context['request'].user,
            subscription=data['subscription']
        ).exists():
            raise serializers.ValidationError('Already subscribed.')
        if self.context['request'].user == data['subscription']:
            raise serializers.ValidationError("Can't subscribe to yourself.")
        return data

    def to_representation(self, obj):
        return ShowSubscriptionsSerializer(
            obj.subscription,
            context={'request': self.context.get('request')}).data


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('owner', 'favorite')

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        if Favorite.objects.filter(owner=request.user,
                                   favorite=data['favorite']).exists():
            raise serializers.ValidationError('Already in favorites.')
        return data

    def to_representation(self, obj):
        request = self.context.get('request')
        return ShowRecipesSerializer(obj.favorite,
                                     context={'request': request}).data


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('customer', 'purchase')

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        if ShoppingCart.objects.filter(customer=request.user,
                                       purchase=data['purchase']).exists():
            raise serializers.ValidationError('Already in shopping list.')
        return data

    def to_representation(self, obj):
        request = self.context.get('request')
        return ShowRecipesSerializer(obj.purchase,
                                     context={'request': request}).data
