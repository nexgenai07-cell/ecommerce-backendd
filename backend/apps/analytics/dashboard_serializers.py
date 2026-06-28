# PATH: apps/analytics/dashboard_serializers.py

from rest_framework import serializers


class DashboardSerializer(serializers.Serializer):
    """Plain serializer — just documents the response shape, data is built in the view"""
    total_revenue = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_orders = serializers.IntegerField()
    total_customers = serializers.IntegerField()
    total_products = serializers.IntegerField()
    revenue_growth = serializers.CharField()
    orders_growth = serializers.CharField()
    pending_orders = serializers.IntegerField()
    low_stock_products = serializers.IntegerField()
    today_revenue = serializers.DecimalField(max_digits=14, decimal_places=2)
    today_orders = serializers.IntegerField()