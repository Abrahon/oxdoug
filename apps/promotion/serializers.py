from rest_framework import serializers
from .models import HeroPromotion, HeroPromotionImage

class HeroPromotionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroPromotionImage
        fields = ['id', 'image']


class HeroPromotionSerializer(serializers.ModelSerializer):
    images = HeroPromotionImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(write_only=True), write_only=True, required=False
    )

    class Meta:
        model = HeroPromotion
        fields = ['id', 'title1', 'title2', 'description', 'images', 'uploaded_images']

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])

        # Update text fields
        instance.title1 = validated_data.get('title1', instance.title1)
        instance.title2 = validated_data.get('title2', instance.title2)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        # Add new images if provided
        for image in uploaded_images:
            HeroPromotionImage.objects.create(hero_promotion=instance, image=image)

        return instance
