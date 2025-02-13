from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from users.models import Profile
from buildings.models import Building
from buildings.serializers import BuildingsSerializer
from announcements.serializers import CommentSerializer, NoticeSerializer
from users.serializers import UserSerializer, UserProfileSerializer
from django.core import serializers


@api_view(['GET', 'PUT'])
def create_query_buildings(request):
    if request.method =='GET':
        all_buildings = Building.objects.all()
        buildings = serializers.serialize('geojson', all_buildings)
        return Response(buildings)

    if request.method == 'PUT':
        try:
            user = User.objects.get(pk=request.data.get('user_id'))
        except User.DoesNotExist:
            return Response({'error': 'user does not exist'}, status=status.HTTP_404_NOT_FOUND)
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            return Response({'error': 'profile does not exist'}, status=status.HTTP_404_NOT_FOUND)
        serializer = BuildingsSerializer(data=request.data)
        if serializer.is_valid():
            building = serializer.save()
            profile.buildings.add(building, through_defaults={'relationship': 'owner'})
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'DELETE', 'PATCH'])
def get_update_building_api(request, building_pk):
    try:
        building = Building.objects.get(pk=building_pk)
    except Building.DoesNotExist:
        return Response({'error': 'building does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BuildingsSerializer(building)
        return Response({'building': serializer.data}, status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        building.delete()
        return Response({'building_id': building_pk, 'status': 'succesfully deleted'})

    if request.method == 'PATCH':
        serializer = BuildingsSerializer(building, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Buiding succesfully updated', 'building': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def user_buildings(request, building_pk):
    try:
        building = Building.objects.get(pk=building_pk)
        user_profiles = building.profile.all()
        users = list(map(lambda x: {'user': { **UserSerializer(x.user).data, 'profile': UserProfileSerializer(x).data}}, user_profiles))
        return Response(users, status=status.HTTP_200_OK)
    except Building.DoesNotExist:
        return Response({'error': 'Building does not exist'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def building_comments(request, building_pk):
    try:
        building = Building.objects.get(pk=building_pk)
        comments = building.comments.all()
        response = {'building': { **BuildingsSerializer(building).data, 'comments': list(map(lambda x: CommentSerializer(x).data, comments))}}
        return Response(response, status=status.HTTP_200_OK)
    except Building.DoesNotExist:
        return Response({'error': 'Building does not exist'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def building_notices(request, building_pk):
    try:
        building = Building.objects.get(pk=building_pk)
        notices = building.notices.all()
        response = {'building': { **BuildingsSerializer(building).data, 'notices': list(map(lambda x: NoticeSerializer(x).data, notices))}}
        return Response(response, status=status.HTTP_200_OK)
    except Building.DoesNotExist:
        return Response({'error': 'Building does not exist'}, status=status.HTTP_404_NOT_FOUND)