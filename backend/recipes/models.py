from django.core.validators import RegexValidator
from django.db import models

from users.models import User


class Ingredient(models.Model):
    """Ingredients for recipes model."""
    name = models.CharField('Name', max_length=256)
    measurement_unit = models.CharField('Measurement unit', max_length=20)

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Tags for recipes model."""
    name = models.CharField('Name', unique=True, max_length=200)
    color = models.CharField('Color', unique=True, max_length=7)
    slug = models.SlugField(
        'Slug',
        max_length=200,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[-a-zA-Z0-9_]+$',
            message='Incorrect username'
        )]
    )

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Recipes model."""
    name = models.CharField('Name', max_length=256)
    text = models.TextField('Description')
    cooking_time = models.PositiveSmallIntegerField('Cooking time')
    image = models.ImageField('Image', upload_to='recipes/images')
    author = models.ForeignKey(User,
                               verbose_name='Author',
                               on_delete=models.CASCADE,
                               related_name='my_recipes')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientsInRecipe',
        through_fields=('recipe', 'ingredients'),
        verbose_name='Ingredients',
        related_name='recipe_ingredients'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Tags',
        related_name='recipe_for_tags',
        blank=True
    )
    pub_date = models.DateTimeField('Publication date',
                                    auto_now_add=True)

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
        ordering = ('pub_date',)

    def __str__(self):
        return self.name


class IngredientsInRecipe(models.Model):
    """Intermidiate many-to-many model for Recipe and Ingredient."""
    recipe = models.ForeignKey(Recipe,
                               verbose_name='Recipe',
                               on_delete=models.CASCADE,
                               related_name='ingredients_for_recipe'
                               )
    ingredients = models.ForeignKey(Ingredient,
                                    verbose_name='Ingredients in recipe',
                                    on_delete=models.CASCADE,
                                    related_name='ingredients'
                                    )
    amount = models.PositiveIntegerField('Amount', default=1)

    class Meta:
        verbose_name = 'Ingredients in recipe'

    def __str__(self):
        return str(self.id)


class Favorite(models.Model):
    """User's favorites model."""
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owner'
    )
    favorite = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite'
    )

    class Meta:
        verbose_name = 'Favorite'

    def __str__(self):
        return str(self.id)


class ShoppingCart(models.Model):
    """User's shpopping cart model."""
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='customer'
    )
    purchase = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )

    class Meta:
        verbose_name = 'Shopping Cart'

    def __str__(self):
        return str(self.id)
