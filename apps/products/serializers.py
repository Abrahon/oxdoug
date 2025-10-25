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


# class ProductSerializer(serializers.ModelSerializer):
#     category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
#     colors = serializers.ListField(
#         child=serializers.CharField(), required=True, allow_empty=True
#     )
#     images_upload = serializers.ListField(
#         child=serializers.ImageField(), write_only=True, required=False, allow_null=True
#     )

#     class Meta:
#         model = Product
#         fields = [
#             "id", "title", "product_code", "category",
#             "colors", "available_stock", "price", "discount", "description",
#             "images", "images_upload",'features'
#         ]

#         read_only_fields = ["id", "product_code", "images"]


#     # -------------------------------
#     # Colors validation
#     # -------------------------------
#     def validate_colors(self, value):
#         if not value:
#             return []

#         # Handle stringified JSON arrays
#         if isinstance(value, list) and len(value) == 1 and isinstance(value[0], str):
#             try:
#                 value = json.loads(value[0])
#             except json.JSONDecodeError:
#                 value = [c.strip() for c in value[0].split(",") if c.strip()]

#         if isinstance(value, str):
#             try:
#                 value = json.loads(value)
#             except json.JSONDecodeError:
#                 value = [c.strip() for c in value.split(",") if c.strip()]

#         # Validate each HEX color
#         normalized = []
#         for c in value:
#             c = c.strip().upper()
#             if not re.match(r"^#(?:[0-9A-F]{3}){1,2}$", c):
#                 raise serializers.ValidationError(f"Invalid color code: {c}")
#             normalized.append(c)
#         return normalized

#     # -------------------------------
#     # Create Product
#     # -------------------------------
#     def create(self, validated_data):
#         images = validated_data.pop("images_upload", [])
#         product = Product.objects.create(**validated_data)

#         image_urls = []
#         print(images)
#         for image in images:
#             try:
#                 result = upload(image)  # Upload to Cloudinary
#                 image_urls.append(result.get("secure_url"))
#             except Exception as e:
#                 raise serializers.ValidationError({"images_upload": f"Image upload failed: {str(e)}"})

#         if image_urls:
#             product.images = image_urls  # Store list of URLs in JSONField
#             product.save(update_fields=["images"])

#         return product

#     # -------------------------------


#     def update(self, instance, validated_data):
#         # Update colors if provided
#         colors = validated_data.pop("colors", None)
#         if colors is not None:
#             instance.colors = colors  

#         # Pop fields
#         images = validated_data.pop("images_upload", None)
#         replace_images = self.initial_data.get("replace_images", "false") == "true"
#         deleted_images = self.initial_data.get("deleted_images", "[]")

#         # Convert deleted_images string (from Postman) to Python list safely
#         import json
#         try:
#             deleted_images = json.loads(deleted_images) if isinstance(deleted_images, str) else deleted_images
#         except json.JSONDecodeError:
#             deleted_images = []

#         # Start with current images
#         current_images = instance.images or []

#         # 🗑️ Remove deleted images
#         if deleted_images:
#             # Optional: remove from Cloudinary as well
#             for img_url in deleted_images:
#                 try:
#                     public_id = img_url.split("/")[-1].split(".")[0]  # extract public id
#                     destroy(public_id)
#                 except Exception:
#                     pass

#             current_images = [img for img in current_images if img not in deleted_images]

#         # ☁️ Upload new images if provided
#         if images:
#             uploaded_urls = []
#             for image in images:
#                 result = upload(image)  # your upload() function (Cloudinary)
#                 uploaded_urls.append(result["secure_url"])

#             if replace_images:
#                 # Replace all images completely
#                 instance.images = uploaded_urls
#             else:
#                 # Add to remaining images
#                 instance.images = current_images + uploaded_urls
#         else:
#             # No new uploads — just keep remaining after deletion
#             instance.images = current_images

#         # ✅ Update other fields
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)

#         instance.save()
#         return instance


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    colors = serializers.ListField(
        child=serializers.CharField(), required=True, allow_empty=True
    )
    images_upload = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False, allow_null=True
    )
    video_upload = serializers.FileField(
        write_only=True, required=False, allow_null=True
    )  # ✅ New video upload field

    class Meta:
        model = Products
        fields = [
            "id", "title", "product_code", "category",
            "colors", "available_stock", "price", "discount","discounted_price", "description",
            "images", "images_upload", "features", "video", "video_upload"  # include video fields
        ]
        read_only_fields = ["id", "product_code", "images", "video","discounted_price"]

    # -------------------------------
    # Colors validation (unchanged)
    # -------------------------------
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
