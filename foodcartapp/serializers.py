from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField

from .models import Order, OrderProduct, Product


class OrderProductSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField()

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
        order = Order.objects.create(**validated_data)

        for item in products_data:
            if not item.get('price'):
                print(item['product'].price)
                item['price'] = float(item['quantity'] * item['product'].price)
            OrderProduct.objects.create(order=order, **item)
        return order