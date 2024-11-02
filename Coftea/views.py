from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from reportlab.pdfgen import canvas
from io import BytesIO
from django.db.models import Sum
from django.views.generic.list import ListView
from .models import Category, Product, Inventory, OrderTransaction, OrderItem
from django.utils import timezone
from datetime import timedelta
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from decimal import Decimal
import json

@method_decorator(login_required, name='dispatch')
class HomePageView(ListView):
    model = Category
    context_object_name = 'home'
    template_name = "home.html"

def request_invoice(request, order_id):
    order = get_object_or_404(OrderTransaction, pk=order_id)
    order_items = OrderItem.objects.filter(order=order)

    # Render the invoice template as an HTML page ready for printing
    return render(request, 'invoice_template.html', {
        'order': order,
        'order_items': order_items
    })

def dashboard(request):
    recent_orders = OrderTransaction.objects.order_by('-transaction_date')[:5]
    total_sales = OrderTransaction.objects.aggregate(total_sales=Sum('total_price'))['total_sales'] or 0
    total_revenue = total_sales  # Assuming total_sales as total revenue for this example
    total_expenses = 0  # This can be calculated or fetched from another source if applicable
    
    context = {
        'recent_orders': recent_orders,
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
    }
    return render(request, 'dashboard.html', context)

def pos(request):
    recent_orders = OrderTransaction.objects.order_by('-transaction_date')[:5]
    categories = Category.objects.all()
    products = Product.objects.all()
    payment_choices = OrderTransaction._meta.get_field('paymentMethod').choices
    if request.method == "POST":
        checkout_items = request.POST.get('checkout_items', '[]')  # Get the checkout items JSON
        apply_discount = request.POST.get('apply_discount')  # Get the discount checkbox value
        payment_method = request.POST.get('paymentMethod')
        try:
            items = json.loads(checkout_items)  # Parse the JSON
        except json.JSONDecodeError:
            return redirect('pos')  # Handle JSON decoding errors

        if not items:
            return redirect('pos')  # Handle empty checkout scenario

        total_price = Decimal(0)  # Use Decimal for precise monetary calculations
        order = OrderTransaction(user=request.user, total_price=total_price, paymentMethod=payment_method)
        order.save()  # Save the order first to get order ID

        for item in items:
            product_id = item.get('id')
            quantity = item.get('quantity')

            if product_id is None or quantity is None:
                continue  # Skip if invalid item

            try:
                product = Product.objects.get(product_id=product_id)  # Fetch product by product_id
            except Product.DoesNotExist:
                continue  # Skip if product does not exist

            price = Decimal(product.price)  # Ensure price is a Decimal
            total_price += price * quantity  # Calculate total price

            # Create OrderItem
            order_item = OrderItem(order=order, product=product, quantity=quantity, price=price)
            order_item.save()

        # Apply discount if the checkbox was checked
        if apply_discount == 'on':  # Check if the checkbox was checked
            discount_amount = total_price * Decimal(0.20)  # Calculate 20% discount as Decimal
            total_price -= discount_amount  # Reduce total price by discount

        # Update total price of the order
        order.total_price = total_price
        order.save()

        # Redirect to the same page with a success message
        return redirect('pos')

    context = {
        'recent_orders': recent_orders,
        'categories': categories,
        'products': products,
        'payment_choices': payment_choices,
    }
    return render(request, 'pos.html', context)


# Reports View
def reports(request):
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())  # Start of the current week
    start_of_month = today.replace(day=1)  # Start of the current month

    daily_sales = OrderTransaction.objects.filter(transaction_date__date=today).aggregate(daily_sales=Sum('total_price'))['daily_sales'] or 0
    weekly_sales = OrderTransaction.objects.filter(transaction_date__date__gte=start_of_week).aggregate(weekly_sales=Sum('total_price'))['weekly_sales'] or 0
    monthly_sales = OrderTransaction.objects.filter(transaction_date__date__gte=start_of_month).aggregate(monthly_sales=Sum('total_price'))['monthly_sales'] or 0

    context = {
        'daily_sales': daily_sales,
        'weekly_sales': weekly_sales,
        'monthly_sales': monthly_sales,
    }
    return render(request, 'reports.html', context)


# Inventory View
def inventory(request):
    inventory_data = Inventory.objects.select_related('product').all()
    context = {
        'inventory_data': inventory_data,
    }
    return render(request, 'inventory.html', context)


# Order History View
def order_history(request):
    orders = OrderTransaction.objects.order_by('-transaction_date').select_related('user').prefetch_related('items__product')
    
    context = {
        'orders': orders,
    }
    return render(request, 'order_history.html', context)