# PATH: apps/categories/serializers.py

from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image', 'product_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()

    def create(self, validated_data):
        # store is injected from the view (request.user's store) — never from client input
        request = self.context['request']
        validated_data['store'] = request.user.stores.first()
        return super().create(validated_data)
    
    def validate_name(self, value):
      qs = Category.objects.filter(name=value)

      if self.instance:
        qs = qs.exclude(pk=self.instance.pk)

      if qs.exists():
        raise serializers.ValidationError(
            "A category with this name already exists."
        )

      return value