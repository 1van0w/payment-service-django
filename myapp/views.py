from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Item, Order, Discount, Tax
import stripe
import os

# Инициализация Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

def get_stripe_payment_intent(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    intent = stripe.PaymentIntent.create(
        amount=int(item.price * 100),  # Сумма в копейках (для валюты в минорных единицах)
        currency=item.currency,
    )

    return JsonResponse({"client_secret": intent.client_secret})

def create_order(request):
    item_ids = request.POST.getlist('item_ids[]')
    items = Item.objects.filter(id__in=item_ids)

    # Создаем заказ и добавляем выбранные товары
    order = Order.objects.create()
    order.items.add(*items)
    order.calculate_total_amount()  # Рассчитываем общую сумму заказа

    # Применяем скидку и налог
    order.apply_discount(10.0)  # Пример: применяем скидку в 10%
    order.apply_tax(5.0)  # Пример: применяем налог в 5%

    # Создаем платежный интент для заказа
    client_secret = order.create_payment_intent()

    return JsonResponse({"client_secret": client_secret, "order_id": order.id})

# Регистрация моделей в админке Django
from django.contrib import admin
from .models import Item, Order, Discount, Tax

admin.site.register(Item)
admin.site.register(Order)
admin.site.register(Discount)
admin.site.register(Tax)
