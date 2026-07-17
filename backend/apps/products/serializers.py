from rest_framework import serializers
from .models import Product, ProductImage, ProductHistory, StockMovement


class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.CharField(read_only=True)

    class Meta:
        model = ProductImage
        fields = [
            "id",
            "image",
            "is_primary",
            "created_at",
        ]


class ProductListSerializer(serializers.ModelSerializer):
    primary_image = serializers.SerializerMethodField()
    in_stock = serializers.BooleanField(read_only=True)
    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "price",
            "original_price",
            "stock",
            "in_stock",
            "sku",
            "category",
            "primary_image",
            "is_active",
        ]

    def get_category(self, obj):
        if not obj.category:
            return None

        return {
            "id": obj.category.id,
            "name": obj.category.name,
        }

    def get_primary_image(self, obj):
        img = obj.images.filter(is_primary=True).first() or obj.images.first()

        if not img:
            return None

        image = img.image

        if not image:
            return None

        if hasattr(image, "url"):
            return image.url

        return str(image)

class LowStockProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "stock",
            "low_stock_threshold",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    in_stock = serializers.BooleanField(read_only=True)
    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "original_price",
            "stock",
            "in_stock",
            "sku",
            "category",
            "is_active",
            "low_stock_threshold",
            "publish_at",
            "images",
            "created_at",
            "updated_at",
        ]

    def get_category(self, obj):
        if not obj.category:
            return None

        return {
            "id": obj.category.id,
            "name": obj.category.name,
        }


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    sku = serializers.CharField(required=False, allow_blank=True)
    stock_to_add = serializers.IntegerField(
        write_only=True,
        required=False,
        default=0,
        min_value=0,
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "original_price",
            "stock",
            "stock_to_add",
            "sku",
            "category",
            "is_active",
            "low_stock_threshold",
            "publish_at",
        ]
        read_only_fields = ["id"]

    def validate_sku(self, value):
        if not value:
            return value

        qs = Product.objects.filter(sku=value)

        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError(
                "A product with this SKU already exists."
            )

        return value

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["store"] = request.user.stores.first()

        stock_to_add = validated_data.pop("stock_to_add", 0)
        validated_data["stock"] = stock_to_add

        return super().create(validated_data)

    def update(self, instance, validated_data):
        # NOTE (stock race-condition fix): 'stock_to_add' on this endpoint
        # is kept working for backward compatibility, but the frontend
        # should no longer send it once a product already exists — stock
        # changes after creation now go through the dedicated, atomic
        # POST /api/v1/products/{id}/stock/adjust/ endpoint instead,
        # which is safe under concurrent checkout/cancel activity. This
        # PUT/update path is NOT safe for concurrent stock changes since
        # it reads instance.stock in Python before saving.
        stock_to_add = validated_data.pop("stock_to_add", 0)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.stock += stock_to_add
        instance.save()

        return instance
    
class ProductHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(
        source="changed_by.name",
        read_only=True,
        default="System",
    )

    class Meta:
        model = ProductHistory
        fields = [
            "id",
            "changed_by_name",
            "old_price",
            "new_price",
            "old_stock",
            "new_stock",
            "reason",
            "created_at",
        ]


# NEW (stock race-condition fix): validates the request body for
# POST /api/v1/products/{id}/stock/adjust/. Only the 5 manual-adjustment
# reasons are accepted here — 'order_placed' / 'order_cancelled' are
# system-only reasons used internally by checkout/cancel flows and are
# never accepted from this endpoint.
class StockAdjustSerializer(serializers.Serializer):
    MANUAL_REASON_CHOICES = [
        "restock",
        "damaged",
        "correction",
        "return",
        "other",
    ]

    delta = serializers.IntegerField()
    reason = serializers.ChoiceField(choices=MANUAL_REASON_CHOICES)
    note = serializers.CharField(required=False, allow_blank=True, max_length=255)

    def validate_delta(self, value):
        if value == 0:
            raise serializers.ValidationError("delta cannot be 0.")
        return value