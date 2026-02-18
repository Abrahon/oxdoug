from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import OurStory
from .serializers import OurStorySerializer
from .models import JoinOurJourney
from .serializers import JoinOurJourneySerializer



class OurStoryView(generics.GenericAPIView):
    serializer_class = OurStorySerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        # Public GET
        if self.request.method == 'GET':
            return [permissions.AllowAny()]

        # Admin for POST / PATCH / DELETE
        return [permissions.IsAdminUser()]

    def get_object(self):
        return OurStory.objects.first()

    #  Public GET
    def get(self, request):
        story = self.get_object()
        if not story:
            return Response({"detail": "Our Story not created yet."}, status=404)

        serializer = self.get_serializer(story)
        return Response(serializer.data)

    #  Admin POST (Create once)
    def post(self, request):
        if OurStory.objects.exists():
            return Response(
                {"detail": "Our Story already exists. Use PATCH to update."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "Our Story created successfully.", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )

    #  Admin PATCH (Update)
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

    #  Admin DELETE
    def delete(self, request):
        story = self.get_object()
        if not story:
            return Response({"detail": "No Our Story exists to delete."}, status=404)

        story.delete()
        return Response(
            {"detail": "Our Story deleted successfully."},
            status=status.HTTP_200_OK
        )



# join journey

class JoinOurJourneyView(generics.GenericAPIView):
    serializer_class = JoinOurJourneySerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        # GET → Public
        if self.request.method == 'GET':
            return [permissions.AllowAny()]

        # POST / PUT / PATCH → Admin only
        return [permissions.IsAdminUser()]

    def get_object(self):
        return JoinOurJourney.objects.first()

    # PUBLIC GET
    def get(self, request):
        journey = self.get_object()
        if not journey:
            return Response(
                {"detail": "Join Our Journey not created yet."},
                status=404
            )

        serializer = self.get_serializer(journey)
        return Response(serializer.data)

    # ADMIN POST (Create once)
    def post(self, request):
        if JoinOurJourney.objects.exists():
            return Response(
                {"detail": "Section already exists. Use PUT/PATCH to update."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "Join Our Journey created successfully.", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )

    # ADMIN PUT (Full update)
    def put(self, request):
        journey = self.get_object()
        if not journey:
            return Response({"detail": "No section exists to update."}, status=404)

        serializer = self.get_serializer(journey, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "Join Our Journey updated successfully.", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    # ADMIN PATCH (Partial update)
    def patch(self, request):
        journey = self.get_object()
        if not journey:
            return Response({"detail": "No section exists to update."}, status=404)

        serializer = self.get_serializer(journey, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "Join Our Journey updated successfully.", "data": serializer.data},
            status=status.HTTP_200_OK
        )
