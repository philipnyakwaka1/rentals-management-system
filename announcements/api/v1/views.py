from announcements.models import Notice, Comment
from django.contrib.auth.models import User
from users.models import UserBuilding
from buildings.models import Building
from rest_framework.decorators import api_view, permission_classes
from announcements.serializers import NoticeSerializer, CommentSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser
from announcements.pagination import CustomPaginator
from rest_framework.exceptions import PermissionDenied, NotAuthenticated

"""
TO DOs
Implement endpoint to get all notices/comments belonging to a particular user
"""

def check_permission_filter_by_building(request, building):
    if not IsAdminUser().has_permission(request, None):
        if not UserBuilding.objects.filter(building=building, profile=request.user.profile).exists():
            raise PermissionDenied('user profile not linked to building')

def check_permission_filter_by_user(request, user):
    if not IsAdminUser().has_permission(request, None):
        if request.user != user:
            raise PermissionDenied('permission denied')

@api_view(['GET', 'PUT'])
def create_get_comment_api(request):

    def check_permission(building_id, user_id):
        try:
            building = Building.objects.get(pk=building_id)
            user = User.objects.get(pk=user_id)
            user_building = UserBuilding.objects.get(profile=user.profile, building=building)
            if user_building.relationship != 'tenant':
                raise PermissionDenied('cannot comment if not tenant')
        except Building.DoesNotExist as e:
            raise ValueError('building does not exist')
        except User.DoesNotExist:
            raise ValueError('user does not exist')
        except UserBuilding.DoesNotExist:
            raise PermissionDenied('user profile not linked to building')

    if request.method == 'GET':
        if not IsAdminUser().has_permission(request, None):
            return Response({'error': 'user lacks permission to access this data'}, status=status.HTTP_403_FORBIDDEN)
        comments = Comment.objects.all()
        paginator = CustomPaginator()
        paginated_queryset = paginator.paginate_queryset(comments, request)
        all_comments = list(map(lambda x: CommentSerializer(x).data, paginated_queryset))
        return paginator.get_paginated_response(all_comments)
    
    if request.method == 'PUT':
        try:
            if not IsAuthenticated().has_permission(request, None):
                raise NotAuthenticated('authentication required')
            if request.user.pk != int(request.data.get('tenant')):
                raise PermissionDenied('user lacks necessary permissions')
            check_permission(request.data.get('building'), request.data.get('tenant'))
            serializer = CommentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except NotAuthenticated as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        

@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def get_update_comment_api(request, comment_id):

    def check_permission(tenant, comment):
        if tenant != comment.tenant:
            raise PermissionDenied('user lacks permission to perform this action')
    
    if request.method == 'GET':
        try:
            comment =Comment.objects.get(pk=comment_id)
            if not IsAdminUser().has_permission(request, None):
                check_permission(request.user, comment)
            serializer = CommentSerializer(comment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response({'error': 'comment id does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except PermissionError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'DELETE':
        try:
            comment = Comment.objects.get(pk=comment_id)
            check_permission(request.user, comment)
            comment.delete()
            return Response({'comment_id': comment_id, 'message': 'succesfully deleted'}, status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response({'error': 'comment id does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            return Response({'error': 'user not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PATCH':
        try:
            comment =Comment.objects.get(pk=comment_id)
            check_permission(request.user, comment)
        except Comment.DoesNotExist:
            return Response({'error': 'comment id does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            return Response({'error': 'user not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def building_comments(request, building_id):
    try:
        building = Building.objects.get(pk=building_id)
        check_permission_filter_by_building(request, building)
        all_building_comments = building.comments.all()
        paginator = CustomPaginator()
        paginated_queryset = paginator.paginate_queryset(all_building_comments, request)
        comments = list(map(lambda x: CommentSerializer(x).data, paginated_queryset))
        return paginator.get_paginated_response(comments)
    except Building.DoesNotExist:
        return Response({'error': 'Building does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_comments(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        check_permission_filter_by_user(request, user)
        all_user_comments = Comment.objects.filter(tenant=user)
        paginator = CustomPaginator()
        paginated_queryset = paginator.paginate_queryset(all_user_comments, request)
        comments = list(map(lambda x: CommentSerializer(x).data, paginated_queryset))
        return paginator.get_paginated_response(comments)
    except User.DoesNotExist:
        return Response({'error': 'user does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET', 'PUT'])
def create_get_notice_api(request):

    def check_permission(building_id, user_id):
        try:
            building = Building.objects.get(pk=building_id)
            user = User.objects.get(pk=user_id)
            user_building = UserBuilding.objects.get(profile=user.profile, building=building)
            if user_building.relationship != 'owner':
                raise PermissionDenied('cannot create notice if not owner')
        except Building.DoesNotExist:
            raise ValueError('building does not exist')
        except User.DoesNotExist:
            raise ValueError('user does not exist')
        except UserBuilding.DoesNotExist:
            raise PermissionDenied('user profile not linked to building')

    if request.method == 'GET':
        if not IsAdminUser().has_permission(request, None):
            return Response({'error': 'user lacks permission to access this data'}, status=status.HTTP_403_FORBIDDEN)
        notices = Notice.objects.all()
        paginator = CustomPaginator()
        paginated_queryset = paginator.paginate_queryset(notices, request)
        all_notices = list(map(lambda x: NoticeSerializer(x).data, paginated_queryset))
        return paginator.get_paginated_response(all_notices)
    
    if request.method == 'PUT':
        try:
            if not IsAuthenticated().has_permission(request, None):
                raise NotAuthenticated('authentication required')
            if int(request.data.get('owner')) != request.user.pk:
                raise PermissionDenied('user does not have necessary permission')
            check_permission(request.data.get('building'), request.data.get('owner'))
            serializer = NoticeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except NotAuthenticated as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def get_update_notice_api(request, notice_id):

    def check_permission(owner, notice):
        if owner != notice.owner:
            if not IsAdminUser().has_permission(request, None):
                raise PermissionDenied('user not authorized to perform this action')
    if request.method == 'GET':
        try:
            notice =Notice.objects.get(pk=notice_id)
            check_permission(request.user, notice)
            serializer = NoticeSerializer(notice)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Notice.DoesNotExist:
            return Response({'error': 'notice id does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'DELETE':
        try:
            notice = Notice.objects.get(pk=notice_id)
            check_permission(request.user, notice)
            notice.delete()
            return Response({'notice_id': notice_id, 'message': 'succesfully deleted'}, status=status.HTTP_200_OK)
        except Notice.DoesNotExist:
            return Response({'error': 'notice id does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PATCH':
        try:
            notice =Notice.objects.get(pk=notice_id)
            check_permission(request.user, notice)
            serializer = NoticeSerializer(notice, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Notice.DoesNotExist:
            return Response({'error': 'notice id does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def building_notices(request, building_id):
    try:
        building = Building.objects.get(pk=building_id)
        check_permission_filter_by_building(request, building)
        all_building_notices = building.notices.all()
        paginator = CustomPaginator()
        paginated_queryset = paginator.paginate_queryset(all_building_notices, request)
        notices = list(map(lambda x: NoticeSerializer(x).data, paginated_queryset))
        return paginator.get_paginated_response(notices)
    except Building.DoesNotExist:
        return Response({'error': 'Building does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_notices(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        check_permission_filter_by_user(request, user)
        all_user_notices = Notice.objects.filter(owner=user)
        paginator = CustomPaginator()
        paginated_queryset = paginator.paginate_queryset(all_user_notices, request)
        notices = list(map(lambda x: NoticeSerializer(x).data, paginated_queryset))
        return paginator.get_paginated_response(notices)
    except User.DoesNotExist:
        return Response({'error': 'user does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
