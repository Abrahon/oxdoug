from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import HeroPromotion, HeroPromotionImage
from .serializers import HeroPromotionSerializer


class HeroPromotionSingletonView(generics.GenericAPIView):
    serializer_class = HeroPromotionSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]  # Public GET
        return [permissions.IsAdminUser()]   # Admin POST/PUT/PATCH/DELETE

    def get_object(self):
        """Return the singleton HeroPromotion or None"""
        return HeroPromotion.objects.first()

    # Public GET
    def get(self, request):
        hero = self.get_object()
        if not hero:
            return Response({"detail": "No Hero Promotion exists yet."}, status=404)
        serializer = self.get_serializer(hero)
        return Response(serializer.data)

    # Admin POST (create only if not exists)
    def post(self, request):
        if HeroPromotion.objects.exists():
            return Response(
                {"detail": "Hero Promotion already exists. Use PUT/PATCH to update."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        hero = serializer.save()

        # Handle images with headings/subheadings
        images = request.FILES.getlist('new_images')
        headings = request.data.getlist('new_headings', [])
        subheadings = request.data.getlist('new_subheadings', [])

        for idx, image in enumerate(images):
            heading = headings[idx] if idx < len(headings) else ''
            sub_heading = subheadings[idx] if idx < len(subheadings) else ''
            HeroPromotionImage.objects.create(
                hero_promotion=hero,
                image=image,
                heading=heading,
                sub_heading=sub_heading
            )

        return Response(
            {"detail": "Hero Promotion created successfully.", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )

    # Admin PUT (full update)
    def put(self, request):
        hero = self.get_object()
        if not hero:
            return Response({"detail": "No Hero Promotion exists to update."}, status=404)

        serializer = self.get_serializer(hero, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # ✅ Add new images
        images = request.FILES.getlist('new_images')
        headings = request.data.getlist('new_headings', [])
        subheadings = request.data.getlist('new_subheadings', [])

        for idx, image in enumerate(images):
            HeroPromotionImage.objects.create(
                hero_promotion=hero,
                image=image,
                heading=headings[idx] if idx < len(headings) else '',
                sub_heading=subheadings[idx] if idx < len(subheadings) else ''
            )
        
        # ✅ Delete selected images
        delete_ids = request.data.getlist('delete_images_ids')
        if delete_ids:
            delete_ids = [int(i) for i in delete_ids]  # convert to int
            HeroPromotionImage.objects.filter(
                hero_promotion=hero,
                id__in=delete_ids
            ).delete()
        
        return Response(
        {"detail": "Hero Promotion updated successfully.", "data": serializer.data},
        status=status.HTTP_200_OK
    )
    
    # Admin PATCH (partial update)
    def patch(self, request):
        hero = self.get_object()
        if not hero:
            return Response({"detail": "No Hero Promotion exists to update."}, status=404)

        serializer = self.get_serializer(hero, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        print("Serializer after save:", serializer.data)

        # ✅ Update or replace specific images one at a time
        image_updates = request.data.get('image_updates', [])  # list of dicts: {"id": x, "image": file, "heading": "", "sub_heading": ""}
        for item in image_updates:
            image_id = item.get("id")
            image_obj = HeroPromotionImage.objects.filter(hero_promotion=hero, id=image_id).first()
            if image_obj:
                if "image" in item:
                    image_obj.image = item["image"]  # Replace existing image file
                if "heading" in item:
                    image_obj.heading = item["heading"]
                if "sub_heading" in item:
                    image_obj.sub_heading = item["sub_heading"]
                image_obj.save()
                print(f"Updated image ID {image_id}")

        # ✅ Add new image (only if explicitly provided, single image)
        new_image = request.FILES.get('new_image')  # only one image
        new_heading = request.data.get('new_heading', '')
        new_subheading = request.data.get('new_subheading', '')
        if new_image:
            HeroPromotionImage.objects.create(
                hero_promotion=hero,
                image=new_image,
                heading=new_heading,
                sub_heading=new_subheading
            )
            print("Added new image:", new_image)

        # ✅ Delete specific images (if IDs provided)
        delete_ids = request.data.getlist('delete_images_ids', [])
        if delete_ids:
            delete_ids = [int(i) for i in delete_ids]
            HeroPromotionImage.objects.filter(hero_promotion=hero, id__in=delete_ids).delete()
            print("Deleted images with IDs:", delete_ids)

        return Response(
            {"detail": "Hero Promotion partially updated successfully.", "data": serializer.data},
            status=status.HTTP_200_OK
        )