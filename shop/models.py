from django.db import models
from django.utils import timezone


class Product(models.Model):
    product_id = models.AutoField
    product_name = models.CharField(max_length=50)
    category = models.CharField(max_length=50, default="")
    subcategory = models.CharField(max_length=50, default="")
    price = models.IntegerField(default=0)
    desc = models.CharField(max_length=200)
    pub_date = models.DateField()
    image = models.ImageField(upload_to="shop/images", default="")
    stock_quantity = models.PositiveIntegerField(default=0)  # New field for inventory quantity
    low_stock_threshold = models.PositiveIntegerField(default=5)  # New field for low stock threshold

    def __str__(self):
        return self.product_name


class Contact(models.Model):
    msg_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=70, default="")
    phone = models.CharField(max_length=70, default="")
    desc = models.CharField(max_length=500, default="")
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

import json
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class Orders(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('online', 'Online'),
        ('other', 'Other'),
    ]

    order_id = models.AutoField(primary_key=True)
    items_json = models.CharField(max_length=5000)
    userId = models.IntegerField(default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    name = models.CharField(max_length=90, null=True, blank=True)
    email = models.CharField(max_length=111, null=True, blank=True)
    address = models.CharField(max_length=111, null=True, blank=True)
    city = models.CharField(max_length=111, null=True, blank=True)
    state = models.CharField(max_length=111, null=True, blank=True)
    zip_code = models.CharField(max_length=111, null=True, blank=True)
    phone = models.CharField(max_length=111, default="", null=True, blank=True)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='cash')
    payment_comments = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Order {self.order_id}"

    def save(self, *args, **kwargs):
        # Ensure payment_comments is filled if payment method is 'Other'
        if self.payment_method == 'other' and not self.payment_comments:
            raise ValueError("Payment comments are required for 'Other' payment method.")

        # Validate stock and deduct only for products with stock_quantity > 0
        items = json.loads(self.items_json)
        for item_id, item_data in items.items():
            try:
                # Extract quantity from the list [quantity, product_name, price]
            
                quantity = item_data[0]  # Get the first element (quantity)
                # Use 'id' to match the Product model's primary key
                product = Product.objects.get(id=int(item_id.replace('pr', '')))
                # Only validate and deduct stock if stock_quantity > 0
                if product.stock_quantity > 0:
                    if product.stock_quantity < quantity:
                        raise ValidationError(
                            f"Insufficient stock for {product.product_name}. Available: {product.stock_quantity}"
                        )
                    product.stock_quantity -= quantity
                    product.save()
                # If stock_quantity == 0, skip stock validation and deduction
            except Product.DoesNotExist:
                raise ValidationError(f"Product with ID {item_id} does not exist.")
            except (TypeError, IndexError):
                raise ValidationError(f"Invalid cart data format for item {item_id}.")

        super().save(*args, **kwargs)

class OrderUpdate(models.Model):
    update_id = models.AutoField(primary_key=True)
    order_id = models.IntegerField(default="")
    update_desc = models.CharField(max_length=5000)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.update_desc


from django.db import models

class Advertise(models.Model):
    name = models.CharField(max_length=200)
    image2 = models.ImageField(upload_to="shop/advertise/", default="")
    
    def __str__(self):
        return self.name


# models.py
from django.db import models

class Table(models.Model):
    number = models.PositiveIntegerField(unique=True) 
    status = models.CharField(max_length=20, default='Blank')  
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Amount associated with the table

    def __str__(self):
        return f'Table {self.number}'



class GroceryItem(models.Model):
    STATUS_CHOICES = [
        ('done', 'Done'),
        ('waiting', 'In Waiting'),
        ('not_yet', 'Not Yet'),
    ]

    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='not_yet')
    timestamp = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.quantity} units"