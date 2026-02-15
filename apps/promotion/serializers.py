from rest_framework import serializers
from .models import HeroPromotion, HeroPromotionImage


class HeroPromotionSerializer(serializers.ModelSerializer):
    # Upload new images
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    # Existing images read-only
    existing_images = serializers.SerializerMethodField(read_only=True)

    # Optional: IDs of existing images to delete
    delete_images_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = HeroPromotion
        fields = ['id', 'title1', 'title2', 'description', 'images', 'existing_images', 'delete_images_ids']

    def get_existing_images(self, obj):
        # FIX: use the correct field name 'images'
        return [{"id": img.id, "image": img.images.url} for img in obj.images.all()]

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('images', [])
        delete_ids = validated_data.pop('delete_images_ids', [])

        # Update text fields
        instance.title1 = validated_data.get('title1', instance.title1)
        instance.title2 = validated_data.get('title2', instance.title2)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        # Delete selected images if requested
        if delete_ids:
            HeroPromotionImage.objects.filter(hero_promotion=instance, id__in=delete_ids).delete()

        # Add new images if provided
        for image in uploaded_images:
            HeroPromotionImage.objects.create(hero_promotion=instance, images=image)  # <- matches model

        return instance
