from django.db import models
from django.contrib.auth.models import User  # Using Django's built-in User model for admin and cashier roles
from django.db.models.signals import post_save
from django.dispatch import receiver

# Category model
class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return self.category_name


# Product model
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return self.product_name
    
    @property
    def stock_status(self):
        if self.quantity == 0:
            return 'No stock'
        elif self.quantity < 30:
            return 'Low stock'
        else:
            return 'High product'
    
    def update_quantity(self, new_quantity):
        self.quantity = new_quantity
        self.save()


# Inventory model
class Inventory(models.Model):
    inventory_id = models.AutoField(primary_key=True)
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.product_name} - Quantity: {self.quantity}"
    
    def save(self, *args, **kwargs):
        # Call the original save method
        super().save(*args, **kwargs)
        # Update the corresponding product quantity
        self.product.update_quantity(self.quantity)


# OrderTransaction model
class OrderTransaction(models.Model):
    order_id = models.AutoField(primary_key=True)
    transaction_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    paymentMethod= models.CharField(
        max_length=20,
        choices=[
            ('Cash', 'Cash'),
            ('Credit Card', 'Credit Card'),
            ('Debit Card', 'Debit Card'),
            ('Gcash', 'G-Cash Wallet'),
            ('Paymaya', 'Maya Wallet')
        ],
        default='Cash'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Completed', 'Completed'),
            ('Cancelled', 'Cancelled')
        ],
        default='Pending'
    )

    def __str__(self):
        return f"Order {self.order_id} by {self.user.username} on {self.transaction_date} Payment: {self.paymentMethod} - {self.status}"


# OrderItem model
class OrderItem(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(OrderTransaction, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at the time of transaction

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name} in Order {self.order.order_id}"

# Signal to adjust inventory after an OrderItem is saved
@receiver(post_save, sender=OrderItem)
def update_inventory(sender, instance, created, **kwargs):
    if created:  # Only adjust inventory if the OrderItem is newly created
        inventory_item = Inventory.objects.get(product=instance.product)

        if inventory_item.quantity >= instance.quantity:
            inventory_item.quantity -= instance.quantity
            inventory_item.save()  # Save the updated inventory
        else:
            # Handle insufficient stock scenario
            raise ValueError(f"Insufficient stock for {instance.product.product_name}")