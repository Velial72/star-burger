import requests
from geopy import distance
from environs import Env


from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q, Case, When, IntegerField

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.conf import settings
from geopy.distance import geodesic


from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem
from place.models import Place


env = Env()
env.read_env()

yandex_geocoder_api_key = env.str('YANDEX_GEOCODER_API_KEY')


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


def fetch_coordinates(address):
    place = Place.objects.filter(address=address).first()
    if place and place.lat and place.lon:
        return float(place.lat), float(place.lon)
    else:
        apikey = settings.YANDEX_GEOCODER_API_KEY
        base_url = "https://geocode-maps.yandex.ru/1.x"
        response = requests.get(base_url, params={
            "geocode": address,
            "apikey": apikey,
            "format": "json",
        })
        response.raise_for_status()
        found_places = response.json()['response']['GeoObjectCollection']['featureMember']

        if found_places:
            most_relevant = found_places[0]
            lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")

            Place.objects.create(address=address, lat=lat, lon=lon)

            return float(lat), float(lon)
        else:
            return None
        

@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = (Order.objects
              .filter(Q(status='U') | Q(status='P'))
              .annotate(
                  status_order=Case(
                      When(status='U', then=0),
                      When(status='P', then=1),
                      output_field=IntegerField()
                  )
              )
              .order_by('status_order')
              .calculate_price())
    
    for order in orders:
        available_restaurants = get_available_restaurants(order)
        order_coordinates = fetch_coordinates(order.address)
        
        restaurants_with_distance = []
        for restaurant in available_restaurants:
            restaurant_coordinates = fetch_coordinates(restaurant.address)
            if restaurant_coordinates and order_coordinates:
                distance = geodesic(order_coordinates, restaurant_coordinates).kilometers
                restaurants_with_distance.append((restaurant, round(distance, 2)))
            else:
                restaurants_with_distance.append((restaurant, None))
        
        restaurants_with_distance.sort(key=lambda x: (x[1] is None, x[1]))
        order.available_restaurants = restaurants_with_distance

    return render(request, template_name='order_items.html', context={'orders': orders})


def get_available_restaurants(order):
    order_product_names = {item.product for item in order.items.all()}
    
    available_restaurants = Restaurant.objects.filter(
        menu_items__product__name__in=order_product_names, 
        menu_items__availability=True
    ).distinct()
    
    return available_restaurants