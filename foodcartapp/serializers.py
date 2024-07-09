from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from django.db.models import Count

from .models import Order, OrderProduct, Product, Restaurant


class OrderProductSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=8, decimal_places=2, required=False)

    class Meta:
        model = OrderProduct
        fields = ['product', 'price', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True, write_only=True)
    phonenumber = PhoneNumberField(region='RU')
    
    class Meta:
        model = Order
        fields = ['address', 'firstname', 'lastname', 'phonenumber', 'products']
    

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        product_ids = [item['product'].id for item in products_data]

        available_restaurants = Restaurant.objects.filter(
            menu_items__product__in=product_ids,
            menu_items__availability=True
        ).annotate(product_count=Count('menu_items')).filter(product_count=len(product_ids))

        if not available_restaurants.exists():
            raise serializers.ValidationError("No restaurant can fulfill this order")

        order = Order.objects.create(**validated_data)

        for item in products_data:
            product = item['product']
            quantity = item['quantity']
            price = item.get('price', product.price * quantity)  # Изменено: добавлено вычисление цены
            OrderProduct.objects.create(order=order, product=product, quantity=quantity, price=price)
        return order