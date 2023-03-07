from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientsInRecipe, Recipe,
                     ShoppingCart, Tag)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorite',)
    list_filter = ('author', 'name', 'tags',)

    def favorite(self, obj):
        return obj.favorite.all().count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)


admin.site.register(Favorite)
admin.site.register(IngredientsInRecipe)
admin.site.register(ShoppingCart)
admin.site.register(Tag)
