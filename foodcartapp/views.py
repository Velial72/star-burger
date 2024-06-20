from django.http import JsonResponse
from django.templatetags.static import static
import json
from phonenumber_field.phonenumber import PhoneNumber
import phonenumbers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Product, Order, OrderProduct
from .serializers import OrderSerializer


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


@api_view(['POST'])
def register_order(request):
#     try:
#         order = request.data
#         ordered_items = order.get('products')
#     except ValueError:
#         return Response({'Error': 'ValueError'})
#     if 'products' not in order:
#         return Response({'Error': "'products' обязательное для заполнения поле"}, status=400)
#     if not ordered_items:
#         return Response({'Error': "'products' должен быть не пустым списком"}, status=400)
#     if not isinstance(ordered_items, list):
#         return Response({'Error': "'products' должен быть списком"}, status=400)
#     required_fields = ['address', 'firstname', 'lastname', 'phonenumber']
#     missing_fields = [field for field in required_fields if not order.get(field)]
#     phonenumber = order.get('phonenumber')
#     if missing_fields:
#         return Response({'Error': f"Пропущен обязательный элемент: {', '.join(missing_fields)}"}, status=400)
#     for field in required_fields:
#         if not isinstance(order.get(field), str):
#             return Response({'Error': f"{field}: Not a valid string"}, status=400)

#     try:
#         phone = PhoneNumber.from_string(phone_number=phonenumber, region='RU')
#         if not phone.is_valid():
#             raise phonenumbers.phonenumberutil.NumberParseException(0, "Введен некорректный номер телефона")
#         phone = phone.as_e164
#     except phonenumbers.phonenumberutil.NumberParseException:
#         return Response({'Error': 'Введен некорректный номер телефона'}, status=400)


    

#     new_order = Order.objects.create(
#         address=order.get('address'),
#         name=order.get('firstname'),
#         surname=order.get('lastname'),
#         phone=phone,
#     )

#     for item in ordered_items:
#         product_id = item.get('product')
#         quantity = item.get('quantity')

#         if quantity is None:
#             return Response({'Error': 'Поле количество не может быть пустыми'}, status=400)
#         try:
#             ordered_product = Product.objects.get(id=item.get('product'))
#             OrderProduct.objects.create(
#                 order=new_order,
#                 product=ordered_product,
#                 quantity=item.get('quantity')
#             )
#         except Product.DoesNotExist:
#             return Response({'Error': f"'products': недопустимый первичный ключ '{product_id}'"}, status=400)

#     return Response(order)

    serializer = OrderSerializer(data=request.data)
    if serializer.is_valid():
        order = serializer.save()
        response_data = {
            'id': order.id,
            'address': order.address,
            'firstname': order.firstname,
            'lastname': order.lastname,
            'phonenumber': order.phonenumber.as_e164
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # serializer = OrderSerializer(data=request.data)
    # if serializer.is_valid():
    #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
    # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)