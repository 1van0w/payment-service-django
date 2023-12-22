from django.db import models
import stripe

class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)  # Добавляем поле для валюты

class Order(models.Model):
    items = models.ManyToManyField(Item)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Общая сумма заказа
    payment_intent_id = models.CharField(max_length=100, blank=True, null=True)  # Идентификатор Stripe Payment Intent

    def calculate_total_amount(self):
        self.total_amount = sum(item.price for item in self.items.all())
        self.save()

    def apply_discount(self, discount_amount):
        Discount.objects.create(order=self, discount_amount=discount_amount)

    def apply_tax(self, tax_amount):
        Tax.objects.create(order=self, tax_amount=tax_amount)

    def create_payment_intent(self):
        stripe.api_key = "YOUR_STRIPE_SECRET_KEY"
        intent = stripe.PaymentIntent.create(
            amount=int(self.total_amount * 100),  # Сумма в минорных единицах валюты
            currency="usd",  # Ваша валюта, либо берется из заказа, если он хранит информацию о валюте
        )
        self.payment_intent_id = intent.id
        self.save()
        return intent.client_secret

class Discount(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)

class Tax(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
