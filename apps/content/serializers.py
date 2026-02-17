from rest_framework import serializers
from .models import WhyChooseSection
from .models import DER



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

