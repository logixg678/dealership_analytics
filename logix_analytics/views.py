# logix_analytics/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth # To group by month
from django.utils import timezone
from .models import Dealership, Vehicle, SalesOrder, StatusLookup
import json # To pass data safely to JavaScript
from datetime import timedelta
from django.db.models import Case, When, Value, IntegerField # For conditional aggregation

@login_required
def dashboard_view(request):
    current_datetime = timezone.now()
    current_year = current_datetime.year
    today = current_datetime.date()

    # --- KPI Calculations (from previous step) ---
    total_dealerships = Dealership.objects.count()
    vehicles_in_stock_count = Vehicle.objects.filter(
        currentstatus__statusgrouping__iexact='Dealer Stock'
    ).count()
    ytd_sales_units = SalesOrder.objects.filter(
        retaildate__year=current_year,
        retaildate__lte=today
    ).count()
    ytd_sales_value_data = SalesOrder.objects.filter(
        retaildate__year=current_year,
        retaildate__lte=today
    ).aggregate(total_value=Sum('vehicle__basemsrp'))
    ytd_sales_value = ytd_sales_value_data['total_value'] if ytd_sales_value_data['total_value'] else 0

    # --- Monthly Sales Trend Data (Last 12 Months) ---
    twelve_months_ago = today - timedelta(days=365) # Approximate, good enough for monthly grouping
    
    # Ensure we only consider months up to the current month if data is sparse
    first_day_of_current_month = today.replace(day=1)

    sales_trend_data = SalesOrder.objects.filter(
        retaildate__gte=twelve_months_ago,
        retaildate__lte=today # Include sales up to today
    ).annotate(
        month=TruncMonth('retaildate') # Truncates date to the first day of the month
    ).values(
        'month' # Group by month
    ).annotate(
        count=Count('salesordersk') # Count sales orders in each month
    ).order_by('month') # Order by month

    # Prepare data for Chart.js
    sales_trend_labels = [item['month'].strftime("%b %Y") for item in sales_trend_data] # e.g., "Jan 2023"
    sales_trend_values = [item['count'] for item in sales_trend_data]

    # --- Inventory Status Breakdown Data ---
    inventory_status_data = Vehicle.objects.values(
        'currentstatus__statustext' # Group by the status text
    ).annotate(
        count=Count('vehiclesk') # Count vehicles in each status
    ).order_by('-count') # Order by count descending (optional, for better visual)

    # Prepare data for Chart.js bar chart
    inventory_status_labels = [item['currentstatus__statustext'] if item['currentstatus__statustext'] else "Unknown Status" for item in inventory_status_data]
    inventory_status_values = [item['count'] for item in inventory_status_data]

    top_n_dealerships = 5 # Or 10, or make it configurable later

    sales_by_dealership_data = SalesOrder.objects.filter(
        retaildate__year=current_year, # Consider YTD or last 12 months
        retaildate__lte=today
    ).values(
        'dealership__dealername' # Group by Dealership Name
    ).annotate(
        count=Count('salesordersk') # Count sales
    ).order_by('-count')[:top_n_dealerships] # Order by count descending and take top N

    sales_by_dealership_labels = [item['dealership__dealername'] if item['dealership__dealername'] else "Unknown Dealership" for item in sales_by_dealership_data]
    sales_by_dealership_values = [item['count'] for item in sales_by_dealership_data]

     # We'll filter for vehicles currently in "Dealer Stock"
    aging_vehicles = Vehicle.objects.filter(currentstatus__statusgrouping__iexact='Dealer Stock')

    # Initialize aging buckets
    aging_buckets = {
        "0-30 Days": 0,
        "31-60 Days": 0,
        "61-90 Days": 0,
        "91-120 Days": 0,
        "120+ Days": 0
    }
    
    # This is a Python-side calculation. For very large datasets, a DB-side CASE WHEN would be better.
    # But for a dashboard overview, this might be acceptable.
    for vehicle in aging_vehicles:
        if vehicle.currentstatusdate: # Ensure there's a date to compare against
            age_days = (today - vehicle.currentstatusdate).days
            if 0 <= age_days <= 30:
                aging_buckets["0-30 Days"] += 1
            elif 31 <= age_days <= 60:
                aging_buckets["31-60 Days"] += 1
            elif 61 <= age_days <= 90:
                aging_buckets["61-90 Days"] += 1
            elif 91 <= age_days <= 120:
                aging_buckets["91-120 Days"] += 1
            elif age_days > 120:
                aging_buckets["120+ Days"] += 1
    
    inventory_aging_labels = list(aging_buckets.keys())
    inventory_aging_values = list(aging_buckets.values())

    context = {
        'page_title': 'Dashboard Overview',
        'total_dealerships': total_dealerships,
        'vehicles_in_stock_count': vehicles_in_stock_count,
        'ytd_sales_units': ytd_sales_units,
        'ytd_sales_value': ytd_sales_value,
        'sales_trend_labels_json': json.dumps(sales_trend_labels),
        'sales_trend_values_json': json.dumps(sales_trend_values),

        # Add inventory status chart data
        'inventory_status_labels_json': json.dumps(inventory_status_labels),
        'inventory_status_values_json': json.dumps(inventory_status_values),
        # Add sales by dealership chart data
        'sales_by_dealership_labels_json': json.dumps(sales_by_dealership_labels),
        'sales_by_dealership_values_json': json.dumps(sales_by_dealership_values),
        # Add inventory aging chart data
        'inventory_aging_labels_json': json.dumps(inventory_aging_labels),
        'inventory_aging_values_json': json.dumps(inventory_aging_values),
    }
    return render(request, 'logix_analytics/dashboard.html', context)

    