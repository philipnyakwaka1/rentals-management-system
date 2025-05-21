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
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import permission_classes
from buildings.pagination import CustomPaginator
from django.db.models.deletion import ProtectedError

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticatedOrReadOnly])
def create_query_buildings(request):
    if request.method =='GET':
        all_buildings = Building.objects.all()
        geojson = request.query_params.get('geojson') == 'true'
        if geojson:
            buildings = serializers.serialize('geojson', all_buildings)
            return Response(buildings)
        
        paginator = CustomPaginator()
        paginated_queryset = paginator.paginate_queryset(all_buildings, request)
        buildings = list(map(lambda x: serializers.serialize('geojson', [x]), paginated_queryset))
        return paginator.get_paginated_response(buildings)


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

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def add_building_profile(request, building_pk):
    try:
        building = Building.objects.get(pk=building_pk)
    except Building.DoesNotExist:
        return  Response({'error': 'building does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    if 'user_id' in request.data and 'relationship' in request.data:
        try:
            user = User.objects.get(pk=request.data.get('user_id'))
        except User.DoesNotExist:
            return  Response({'error': 'user does not exist'}, status=status.HTTP_404_NOT_FOUND)
        if user.profile:
            user.profile.buildings.add(building, through_defaults={'relationship': request.data.get('relationship')})
            return Response({'message': f'profile with user id {user.pk} successful added to building id {building.pk}'}, status=status.HTTP_200_OK)
        return Response({'error': 'user profile does not exist'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'error': 'must provide user id and relationship to building'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'DELETE', 'PATCH'])
@permission_classes([IsAuthenticatedOrReadOnly])
def get_update_building_api(request, building_pk):
    try:
        building = Building.objects.get(pk=building_pk)
    except Building.DoesNotExist:
        return Response({'error': 'building does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        data = serializers.serialize('geojson', [building])
        return Response(data, status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        try:
            building.delete()
            return Response({'building_id': building_pk, 'status': 'succesfully deleted'})
        except ProtectedError:
            return Response('building has an unresolved notice', status=status.HTTP_409_CONFLICT)

    if request.method == 'PATCH':
        serializer = BuildingsSerializer(building, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Buiding succesfully updated', 'building': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def building_users(request, building_pk):
    try:
        building = Building.objects.get(pk=building_pk)
        user_profiles = building.profile.all()
        paginator = CustomPaginator()
        paginated_queryset = paginator.paginate_queryset(user_profiles, request)
        users = list(map(lambda x: {'user': { **UserSerializer(x.user).data, 'profile': UserProfileSerializer(x).data}}, paginated_queryset))
        return paginator.get_paginated_response(users)
    except Building.DoesNotExist:
        return Response({'error': 'Building does not exist'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def building_comments(request, building_pk):
    try:
        building = Building.objects.get(pk=building_pk)
        all_comments = building.comments.all()
        paginator = CustomPaginator()
        paginated_queryset = paginator.paginate_queryset(all_comments, request)
        comments = list(map(lambda x: CommentSerializer(x).data, paginated_queryset))
        return paginator.get_paginated_response(comments)
    except Building.DoesNotExist:
        return Response({'error': 'Building does not exist'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def building_notices(request, building_pk):
    try:
        building = Building.objects.get(pk=building_pk)
        all_notices = building.notices.all()
        paginator = CustomPaginator()
        paginated_queryset = paginator.paginate_queryset(all_notices, request)
        notices = list(map(lambda x: NoticeSerializer(x).data, paginated_queryset))
        return paginator.get_paginated_response(notices)
    except Building.DoesNotExist:
        return Response({'error': 'Building does not exist'}, status=status.HTTP_404_NOT_FOUND)