from rest_framework import serializers
from .models import WhyChooseSection
from .models import DER
from .models import Section


class WhyChooseSectionSerializer(serializers.ModelSerializer):
    icon = serializers.ImageField(required=False, allow_null=True) # DRF expects get_icon method

    class Meta:
        model = WhyChooseSection
        fields = [
            'id',
            'heading1',
            'heading2',
            'description',
            'card_heading',
            'card_description',
            'icon',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def to_representation(self, instance):
        """Return full Cloudinary URL for icon."""
        ret = super().to_representation(instance)
        if instance.icon:
            # instance.icon.url is the Cloudinary URL
            ret['icon'] = instance.icon.url
        else:
            ret['icon'] = None
        return ret


# how workes


class DERSerializer(serializers.ModelSerializer):
    icon = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = DER
        fields = ['id', 'icon', 'title', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']

    def to_representation(self, instance):
        """Return full Cloudinary URL for icon."""
        ret = super().to_representation(instance)
        if instance.icon:
            # instance.icon.url is the Cloudinary URL
            ret['icon'] = instance.icon.url
        else:
            ret['icon'] = None
        return ret

# section



class SectionSerializer(serializers.ModelSerializer):
    # Convert all CloudinaryFields to URLs
    image = serializers.SerializerMethodField()
    icon1 = serializers.SerializerMethodField()
    icon2 = serializers.SerializerMethodField()
    icon3 = serializers.SerializerMethodField()
    icon4 = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = [
            'id',
            'heading1', 'description1', 'icon1',
            'heading2', 'description2', 'icon2',
            'heading3', 'description3', 'icon3',
            'heading4', 'description4', 'icon4',
            'image',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_image(self, obj):
        return obj.image.url if obj.image else None

    def get_icon1(self, obj):
        return obj.icon1.url if obj.icon1 else None

    def get_icon2(self, obj):
        return obj.icon2.url if obj.icon2 else None

    def get_icon3(self, obj):
        return obj.icon3.url if obj.icon3 else None

    def get_icon4(self, obj):
        return obj.icon4.url if obj.icon4 else None
