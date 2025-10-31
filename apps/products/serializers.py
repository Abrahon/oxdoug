import re
import json
from rest_framework import serializers
from cloudinary.uploader import upload
from .models import Products, Category
from cloudinary.uploader import destroy  

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]



class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    category_detail = CategorySerializer(source="category", read_only=True)
    colors = serializers.ListField(
        child=serializers.CharField(), required=True, allow_empty=True
    )
    features = serializers.ListField(   
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )

    main_image_upload = serializers.ImageField( 
        write_only=True, required=False, allow_null=True
    )
    images_upload = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False, allow_null=True
    )
    video_upload = serializers.FileField(
        write_only=True, required=False, allow_null=True
    ) 

    class Meta:
        model = Products
        fields = [
            "id", "title", "product_code", "category","category_detail",
            "colors", "available_stock", "price", "discount","discounted_price", "description",
            "images", "images_upload","main_image","main_image_upload", "features", "video", "video_upload"  
        ]
        read_only_fields = ["id", "product_code", "images", "main_image" ,"video","discounted_price"]

    # -------------------------------
    # featureed  validation 
    # -------------------------------
    def validate_features(self, value):
        if not value:
            return []

        # Handle stringified list from Postman
        if isinstance(value, list) and len(value) == 1 and isinstance(value[0], str):
            try:
                value = json.loads(value[0])
            except json.JSONDecodeError:
                value = [v.strip() for v in value[0].split(",") if v.strip()]

        elif isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                value = [v.strip() for v in value.split(",") if v.strip()]

        # Ensure each item is a string
        for v in value:
            if not isinstance(v, str):
                raise serializers.ValidationError("Each feature must be a string.")

        return value
    
    # color validation
    def validate_colors(self, value):
        if not value:
            return []

        if isinstance(value, list) and len(value) == 1 and isinstance(value[0], str):
            try:
                value = json.loads(value[0])
            except json.JSONDecodeError:
                value = [c.strip() for c in value[0].split(",") if c.strip()]

        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                value = [c.strip() for c in value.split(",") if c.strip()]

        normalized = []
        for c in value:
            c = c.strip().upper()
            if not re.match(r"^#(?:[0-9A-F]{3}){1,2}$", c):
                raise serializers.ValidationError(f"Invalid color code: {c}")
            normalized.append(c)
        return normalized

    # -------------------------------
    # Create Product
    # -------------------------------
    def create(self, validated_data):
        images = validated_data.pop("images_upload", [])
        main_image_file = validated_data.pop("main_image_upload", None) 
        video_file = validated_data.pop("video_upload", None)
        product = Products.objects.create(**validated_data)

        # Upload images
        image_urls = []
        for image in images:
            try:
                result = upload(image)
                image_urls.append(result.get("secure_url"))
            except Exception as e:
                raise serializers.ValidationError({"images_upload": f"Image upload failed: {str(e)}"})

        if image_urls:
            product.images = image_urls

        # main image upload 
        if main_image_file:
            try:
                result = upload(main_image_file)
                product.main_image = result.get("secure_url")
            except Exception as e:
                raise serializers.ValidationError({"main_image_upload": f"Main image upload failed: {str(e)}"})

        # Upload video
        if video_file:
            try:
                result = upload(video_file, resource_type="video")
                product.video = result.get("secure_url")
            except Exception as e:
                raise serializers.ValidationError({"video_upload": f"Video upload failed: {str(e)}"})

        product.save()
        return product

    # -------------------------------
    # Update Product
    # -------------------------------
    def update(self, instance, validated_data):
        # Update colors
        colors = validated_data.pop("colors", None)
        if colors is not None:
            instance.colors = colors
        

        main_image_file = validated_data.pop("main_image_upload", None)

        if main_image_file:
                try:
                    result = upload(main_image_file)  # your upload function
                    instance.main_image = result.get("secure_url")
                except Exception as e:
                    raise serializers.ValidationError({
                        "main_image_upload": f"Main image upload failed: {str(e)}"
                    })


        # Handle images
        images = validated_data.pop("images_upload", None)
        replace_images = self.initial_data.get("replace_images", "false") == "true"
        deleted_images = self.initial_data.get("deleted_images", "[]")

        import json
        try:
            deleted_images = json.loads(deleted_images) if isinstance(deleted_images, str) else deleted_images
        except json.JSONDecodeError:
            deleted_images = []

        current_images = instance.images or []

        if deleted_images:
            for img_url in deleted_images:
                try:
                    public_id = img_url.split("/")[-1].split(".")[0]
                    destroy(public_id)
                except Exception:
                    pass
            current_images = [img for img in current_images if img not in deleted_images]

        if images:
            uploaded_urls = []
            for image in images:
                result = upload(image)
                uploaded_urls.append(result["secure_url"])

            if replace_images:
                instance.images = uploaded_urls
            else:
                instance.images = current_images + uploaded_urls
        else:
            instance.images = current_images

        # Handle video
        video_file = validated_data.pop("video_upload", None)
        if video_file:
            try:
                result = upload(video_file, resource_type="video")
                instance.video = result.get("secure_url")
            except Exception as e:
                raise serializers.ValidationError({"video_upload": f"Video upload failed: {str(e)}"})

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
