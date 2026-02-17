from rest_framework import serializers
from .models import OurStory

class OurStorySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = OurStory
        fields = [
            'story_description',
            'mission_description',
            'vision_description',
            'image',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
