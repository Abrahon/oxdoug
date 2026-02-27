from rest_framework import serializers
from .models import FAQ,ShippingPolicy,TermsAndConditions,ReturnPolicy,ReturnHelp,FooterSection


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = [
            "id",
            "question",
            "answer",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_question(self, value):
        if FAQ.objects.filter(question__iexact=value).exclude(
            id=self.instance.id if self.instance else None
        ).exists():
            raise serializers.ValidationError("This question already exists.")
        return value
    

# shipping polecy

class ShippingPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingPolicy
        fields = ['id', 'heading', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    

# return polecy


class ReturnPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnPolicy
        fields = '__all__'



class TermsAndConditionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsAndConditions
        fields = '__all__'


# return policy


class ReturnHelpSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnHelp
        fields = "__all__"



# footer info

class InfoSectionSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = FooterSection
        fields = ['id', 'title', 'content', 'image', 'image_url']  # include image_url for convenience

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url  # CloudinaryField automatically gives full URL
        return None