from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Count
from django.views.generic.list import ListView
from .models import Category, Product, Inventory, OrderTransaction
from django.utils import timezone
from datetime import timedelta
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

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

@method_decorator(login_required, name='dispatch')
class HomePageView(ListView):
    model = Category
    context_object_name = 'dashboard'
    template_name = "dashboard.html"

def pos(request):
    recent_orders = OrderTransaction.objects.order_by('-transaction_date')[:5]
    categories = Category.objects.all()
    products = Product.objects.all()
    if request.method == 'POST':
        # Process POS transaction logic here (e.g., saving an order)
        # This is a placeholder; handling product selection and order saving can be implemented as needed.
        pass

    context = {
        'recent_orders': recent_orders,
        'categories': categories,
        'products': products,
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
