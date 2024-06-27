from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField

from .models import Order, OrderProduct, Product


# class OrderProductSerializer(serializers.Serializer):
#     product = serializers.IntegerField()
#     quantity = serializers.IntegerField()


# class OrderSerializer(serializers.Serializer):
#     address = serializers.CharField()
#     firstname = serializers.CharField()
#     lastname = serializers.CharField()
#     phonenumber = PhoneNumberField(region='RU')
#     products = OrderProductSerializer(many=True)


#     def validate_products(self, value):
#         if not value:
#             raise serializers.ValidationError("'products' должен быть не пустым списком")
#         return value


#     def validate_phonenumber(self, value):
#         if not value.is_valid():
#             raise serializers.ValidationError("Введен некорректный номер телефона")
#         return value


#     def create(self, validated_data):
#         products_data = validated_data.pop('products')
#         order = Order.objects.create(**validated_data)
#         for item in products_data:
#             try:
#                 product = Product.objects.get(id=item['product'])
#                 OrderProduct.objects.create(order=order, product=product, quantity=item['quantity'])
#             except Product.DoesNotExist:
#                 raise serializers.ValidationError(f"'products': недопустимый первичный ключ '{item['product']}'")
#         return order

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

    def validate_products(self, value):
        if not value:
            raise serializers.ValidationError("'products' должен быть не пустым списком")
        return value

    def validate_phonenumber(self, value):
        if not value.is_valid():
            raise serializers.ValidationError("Введен некорректный номер телефона")
        return value

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        order = Order.objects.create(**validated_data)
        for item in products_data:
            if not item.get('price'):
                item['price'] = float(item['quantity'] * item['product'].price)
            OrderProduct.objects.create(order=order, **item)
        return order