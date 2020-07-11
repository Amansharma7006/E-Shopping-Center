from django.conf import settings
from django.urls import path,include
from app1 import views as v1
app_name='app1'

urlpatterns = [
    path('',v1.HomeView.as_view(),name='home'),

    path('list/',v1.listing),

    path('category/',v1.category),

    path('contact/',v1.contact),

    path('about/',v1.about),

    path('shop/',v1.shopping),
    path('rental/',v1.rental),
    path('hotel/',v1.hotel),
    path('food/',v1.food),

    path('shirt/',v1.shirt),
    path('Jeans/',v1.Jeans),
    path('Jackets/',v1.Jackets),
    path('Shoes/',v1.Shoes),
    path('rental_car/',v1.rental_car),
    path('own_car/',v1.own_car),
    path('rental_bike/',v1.rental_bike),
    path('own_bike/',v1.own_bike),
    path('rental_flats/',v1.rental_flats),
    path('south/',v1.south),


    path('products/<slug>/',v1.ItemDetailView.as_view(),name='products'),

    path('checkout/',v1.CheckoutView.as_view(),name='checkout'),

    path('order_summary/',v1.OrderSummaryView.as_view(),name='order_summary'),

    path('payment/<payment_option>/',v1.PaymentView.as_view(),name='payment'),

    path('request-refund/',v1.RequestRefundView.as_view(),name='request-refund'),

    path('add_to_cart/<slug>/',v1.add_to_cart,name='add_to_cart'),

    path('add_coupon/',v1.AddCouponView.as_view(),name='add_coupon'),

    path('success/',v1.success,name='success'),

    path('userform/',v1.useradd),

    path('remove_single_item_from_cart/<slug>/',v1.remove_single_item_from_cart,name='remove_single_item_from_cart'),

    path('remove_from_cart/<slug>/',v1.remove_from_cart,name='remove_from_cart')
]
