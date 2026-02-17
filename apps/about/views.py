from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import OurStory
from .serializers import OurStorySerializer


class OurStoryView(generics.GenericAPIView):
    serializer_class = OurStorySerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return OurStory.objects.first()

    def get(self, request):
        story = self.get_object()
        if not story:
            return Response({"detail": "Our Story not created yet."}, status=404)
        serializer = self.get_serializer(story)
        return Response(serializer.data)

    def post(self, request):
        if OurStory.objects.exists():
            return Response(
                {"detail": "Our Story already exists. Use PUT/PATCH to update."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "Our Story created successfully.", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )

    def patch(self, request):
        story = self.get_object()
        if not story:
            return Response({"detail": "No Our Story exists to update."}, status=404)

        serializer = self.get_serializer(story, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "Our Story updated successfully.", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    def delete(self, request):
        story = self.get_object()
        if not story:
            return Response({"detail": "No Our Story exists to delete."}, status=404)

        story.delete()
        return Response(
            {"detail": "Our Story deleted successfully."},
            status=status.HTTP_200_OK
        )
