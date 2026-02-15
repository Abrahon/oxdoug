from rest_framework import serializers
from .models import WhyChooseSection, WhyChooseCard

class WhyChooseCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhyChooseCard
        fields = ["id", "card_heading", "card_description", "icon", "order"]

class WhyChooseSectionSerializer(serializers.ModelSerializer):
    cards = WhyChooseCardSerializer(many=True)

    class Meta:
        model = WhyChooseSection
        fields = ["id", "heading1", "heading2", "description", "cards"]

    def create(self, validated_data):
        cards_data = validated_data.pop("cards")
        section = WhyChooseSection.objects.create(**validated_data)
        for card in cards_data:
            WhyChooseCard.objects.create(section=section, **card)
        return section

    def update(self, instance, validated_data):
        cards_data = validated_data.pop("cards", None)
        instance.heading1 = validated_data.get("heading1", instance.heading1)
        instance.heading2 = validated_data.get("heading2", instance.heading2)
        instance.description = validated_data.get("description", instance.description)
        instance.save()

        if cards_data is not None:
            instance.cards.all().delete()
            for card in cards_data:
                WhyChooseCard.objects.create(section=instance, **card)
        return instance
