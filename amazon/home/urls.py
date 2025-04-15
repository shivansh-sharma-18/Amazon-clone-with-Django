from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('profile/', views.profile, name='profile'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/', views.order_confirmation, name='order_confirmation'),

    # Product Categories
    path('clothes/', views.clothes, name='clothes'),
    path('health/', views.health, name='health'),
    path('beauty/', views.beauty, name='beauty'),
    path('orders/', views.orders, name='orders'),
    path('fashion_trends/', views.fashion_trends, name='fashion_trends'),
    path('mobiles/', views.mobiles, name='mobiles'),
    path('new_arrival_toys/', views.new_arrival_toys, name='new_arrival_toys'),
    path('pet_care/', views.pet_care, name='pet_care'),
    path('furniture/', views.furniture, name='furniture'),
    path('cart/', views.cart, name='cart'),

    # # Chatbot
    # path('chatbot/', views.chatbot, name='chatbot'),
    # path('get_ai_response/', views.get_ai_response, name='get_ai_response'),
]
