from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from users.models import Profile
from buildings.models import Building
from buildings.serializers import BuildingsSerializer
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
        print(building.delete())
        return Response({'building_id': building_pk, 'status': 'succesfully deleted'})

    if request.method == 'PATCH':
        serializer = BuildingsSerializer(building, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Buiding succesfully updated', 'building': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])    
def user_buildings(request, user_pk):
    try:
        user = User.objects.get(pk=user_pk)
    except User.DoesNotExist:
        return Response({'error': 'user does not exist'}, status=status.HTTP_404_NOT_FOUND)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        return Response({'error': 'profile does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    buildings = profile.buildings.all()
    all_buildings = list(map(lambda x: BuildingsSerializer(x).data, buildings))
    return Response({'user': UserSerializer(user).data, "buildings": all_buildings}, status=status.HTTP_200_OK)
