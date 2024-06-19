from django.http import JsonResponse
from django.templatetags.static import static
import json
from phonenumber_field.phonenumber import PhoneNumber

from .models import Product, Order, OrderProduct


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def register_order(request):
    try:
        order = json.loads(request.body.decode())
        ordered_items = order.get('products')
    except ValueError:
        return JsonResponse({'Error': 'ValueError'})
    
    new_order = Order.objects.create(
        address=order.get('address'),
        name=order.get('firstname'),
        surname=order.get('lastname'),
        phone=PhoneNumber.from_string(
            phone_number=order.get('phonenumber'),
            region='RU'
        ).as_e164,
    )

    for item in ordered_items:
        ordered_product = Product.objects.get(id=item.get('product'))
        OrderProduct.objects.create(
            order=new_order,
            product=ordered_product,
            quantity=item.get('quantity')
        )
