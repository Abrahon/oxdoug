# from rest_framework import serializers
# from .models import HeroPromotion, HeroPromotionImage


# class HeroPromotionSerializer(serializers.ModelSerializer):
#     # Upload new images
#     images = serializers.ListField(
#         child=serializers.ImageField(),
#         write_only=True,
#         required=False
#     )

#     # Existing images read-only
#     existing_images = serializers.SerializerMethodField(read_only=True)

#     # Optional: IDs of existing images to delete
#     delete_images_ids = serializers.ListField(
#         child=serializers.IntegerField(),
#         write_only=True,
#         required=False
#     )

#     class Meta:
#         model = HeroPromotion
#         fields = ['id', 'title1', 'title2', 'description', 'images', 'existing_images', 'delete_images_ids']

#     def get_existing_images(self, obj):
#         # FIX: use the correct field name 'images'
#         return [{"id": img.id, "image": img.images.url} for img in obj.images.all()]

#     def update(self, instance, validated_data):
#         uploaded_images = validated_data.pop('images', [])
#         delete_ids = validated_data.pop('delete_images_ids', [])

#         # Update text fields
#         instance.title1 = validated_data.get('title1', instance.title1)
#         instance.title2 = validated_data.get('title2', instance.title2)
#         instance.description = validated_data.get('description', instance.description)
#         instance.save()

#         # Delete selected images if requested
#         if delete_ids:
#             HeroPromotionImage.objects.filter(hero_promotion=instance, id__in=delete_ids).delete()

#         # Add new images if provided
#         for image in uploaded_images:
#             HeroPromotionImage.objects.create(hero_promotion=instance, images=image)  # <- matches model

#         return instance

from rest_framework import serializers
from .models import HeroPromotion, HeroPromotionImage


class HeroPromotionImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(read_only=True)
    class Meta:
        model = HeroPromotionImage
        fields = ['id', 'image', 'heading', 'sub_heading']  # include id for frontend


class HeroPromotionSerializer(serializers.ModelSerializer):

    #  New images
    new_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    new_headings = serializers.ListField(
        child=serializers.CharField(max_length=255),
        write_only=True,
        required=False
    )

    new_subheadings = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )

    #  Delete images
    delete_images_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    #  Existing images (include id for replace)
    existing_images = HeroPromotionImageSerializer(
        source='images',
        many=True,
        read_only=True
    )

    class Meta:
        model = HeroPromotion
        fields = [
            'title1',
            'title2',
            'description',
            'new_images',
            'new_headings',
            'new_subheadings',
            'delete_images_ids',
            'existing_images',
        ]

    #  Validation
    def validate(self, attrs):
        images = attrs.get('new_images', [])
        headings = attrs.get('new_headings', [])
        subheadings = attrs.get('new_subheadings', [])

        if images:
            if headings and len(headings) != len(images):
                raise serializers.ValidationError(
                    "Number of headings must match number of images."
                )
            if subheadings and len(subheadings) != len(images):
                raise serializers.ValidationError(
                    "Number of subheadings must match number of images."
                )

        return attrs

    #  Update logic
    def update(self, instance, validated_data):
        new_images = validated_data.pop('new_images', [])
        new_headings = validated_data.pop('new_headings', [])
        new_subheadings = validated_data.pop('new_subheadings', [])
        delete_ids = validated_data.pop('delete_images_ids', [])

        # Update text fields
        instance.title1 = validated_data.get('title1', instance.title1)
        instance.title2 = validated_data.get('title2', instance.title2)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        #  Delete selected images
        if delete_ids:
            HeroPromotionImage.objects.filter(
                hero_promotion=instance,
                id__in=delete_ids
            ).delete()

        #  Add new images
        for idx, image in enumerate(new_images):
            HeroPromotionImage.objects.create(
                hero_promotion=instance,
                image=image,
                heading=new_headings[idx] if idx < len(new_headings) else '',
                sub_heading=new_subheadings[idx] if idx < len(new_subheadings) else ''
            )

        return instance
