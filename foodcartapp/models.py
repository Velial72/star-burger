from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.timezone import now
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import F, Sum
from decimal import Decimal


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name='ресторан',
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f'{self.restaurant.name} - {self.product.name}'


class OrderQuerySet(models.QuerySet):
    def calculate_price(self):
        order = self.annotate(
            order_price=Sum(F("items__product__price") * F("items__quantity"))
        )
        return order
    

class Order(models.Model):
    ORDER_STATUS = [
        ('U', 'Необработан'),
        ('P', 'Готовится'),
        ('D', 'Доставка'),
        ('F', 'Выполнен'),
    ]
    PAYMENT = [
        ('C', 'Наличностью'),
        ('O', 'Онлайн'),
        ('CC', 'Картой'),
    ]
    address = models.CharField(
        max_length=50,
        verbose_name='Адрес',
        db_index=True
    )
    firstname = models.CharField(
        max_length=50,
        verbose_name='Имя'
    )
    lastname = models.CharField(
        max_length=50,
        verbose_name='Фамилия'
    )
    phonenumber = PhoneNumberField(
        verbose_name='Мобильный номер',
        region='RU',
        db_index=True
    )
    status = models.CharField(
        verbose_name='Статус заказа',
        max_length=15,
        db_index=True,
        choices=ORDER_STATUS,
        default='U'
    )
    payment = models.CharField(
        verbose_name='Способ оплаты',
        max_length=10,
        db_index=True,
        choices=PAYMENT,
        default='C'
    )
    comment = models.TextField(
        verbose_name='Комментарий',
        blank=True
    )
    created_at = models.DateTimeField(
        verbose_name='Время создания заказа',
        default=now,
        db_index=True
    )
    called_at = models.DateTimeField(
        verbose_name='Время звонка',
        null=True,
        blank=True,
        db_index=True
    )
    delivered_at = models.DateTimeField(
        verbose_name='Время доставки',
        null=True,
        blank=True,
        db_index=True
    )
    objects = OrderQuerySet.as_manager()
    restaurant = models.ForeignKey(Restaurant, on_delete=models.SET_NULL,
                                   null=True, 
                                   blank=True, 
                                   related_name='orders', 
                                   verbose_name='Ресторан')
                                

    class Meta:
        verbose_name='Заказ'
        verbose_name_plural='Заказы'

    def __str__(self):
        return f'{self.firstname} {self.lastname} {self.address}'
    

class OrderProduct(models.Model):
    order = models.ForeignKey(Order,
                              verbose_name='Элементы заказа',
                              on_delete=models.CASCADE,
                              related_name='items')
    product = models.ForeignKey(Product,
                                verbose_name='Товар',
                                on_delete=models.SET_NULL,
                                null=True)
    quantity = models.IntegerField(verbose_name='Количество',
                                   validators=[MinValueValidator(1)])
    price = models.DecimalField(verbose_name='Стоимость',
                                max_digits=8,
                                decimal_places=2,
                                validators=[MinValueValidator(Decimal('0.00'))])

    class Meta:
        verbose_name='Элемент заказа'
        verbose_name_plural='Элементы заказа'