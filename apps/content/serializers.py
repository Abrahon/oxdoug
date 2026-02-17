from rest_framework import serializers
from .models import WhyChooseSection
from .models import DER
from .models import Section,ContactInfo



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



from rest_framework import serializers
from .models import Section

class SectionSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)
    icon1 = serializers.ImageField(required=False, allow_null=True)
    icon2 = serializers.ImageField(required=False, allow_null=True)
    icon3 = serializers.ImageField(required=False, allow_null=True)
    icon4 = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Section
        fields = [
            'heading1', 'description1', 'icon1',
            'heading2', 'description2', 'icon2',
            'heading3', 'description3', 'icon3',
            'heading4', 'description4', 'icon4',
            'image',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
# contact



class ContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInfo
        fields = ['email', 'contact_number', 'location', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
