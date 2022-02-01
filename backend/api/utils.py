from django.db.models import F, Sum
from django.http.response import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from recipes.models import IngredientRecipe


@api_view(['GET'])
def download_shopping_cart(request):
    user = request.user
    if not user.is_anonymous:
        shopping_cart = user.customer.all()
        recipes = shopping_cart.values('recipe').all()
        ingredients = IngredientRecipe.objects.filter(recipe_id__in=recipes)
        shopping_list = ingredients.values(
            'ingredient__name', 'ingredient__unit', 'amount'
        ).annotate(
            name=F('ingredient__name'),
            unit=F('ingredient__unit'),
            total=Sum('amount'),
        ).order_by('-total')
        text = '\n'.join([
            f"{item['name']} ({item['unit']}) - {item['total']}"
            for item in shopping_list
        ])
        filename = "foodgram_shopping_cart.txt"
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment: filename={filename}'
        return response
    return Response(
            data={"detail": "Учетные данные не были предоставлены"},
            status=status.HTTP_401_UNAUTHORIZED,
        )
