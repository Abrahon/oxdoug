from rest_framework import serializers
from .models import WhyChooseSection

class WhyChooseSectionSerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()  # return full Cloudinary URL

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
    def get_icon(self, obj):
        if obj.icon:
            return obj.icon.url  # Full Cloudinary URL
        return None

