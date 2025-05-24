from rest_framework.decorators import api_view, permission_classes
from announcements.models import Notice, Comment
from announcements.serializers import NoticeSerializer, CommentSerializer
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from announcements.pagination import CustomPaginator
from rest_framework.exceptions import PermissionDenied

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticatedOrReadOnly])
def create_get_comment_api(request):
    if request.method == 'GET':
        comments = Comment.objects.all()
        paginator = CustomPaginator()
        paginated_queryset = paginator.paginate_queryset(comments, request)
        all_comments = list(map(lambda x: CommentSerializer(x).data, paginated_queryset))
        return paginator.get_paginated_response(all_comments)
    
    if request.method == 'PUT':
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def get_update_comment_api(request, comment_pk):

    def check_permission(tenant, comment):
        if tenant != comment.tenant:
            raise PermissionDenied('user not authorized to perform this action')
    
    if request.method == 'GET':
        try:
            comment =Comment.objects.get(pk=comment_pk)
            serializer = CommentSerializer(comment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response({'error': 'comment id does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'DELETE':
        try:
            comment = Comment.objects.get(pk=comment_pk)
            check_permission(request.user, comment)
            comment.delete()
            return Response({'comment_id': comment_pk, 'message': 'succesfully deleted'}, status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response({'error': 'comment id does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            return Response({'error': 'user not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'PATCH':
        try:
            comment =Comment.objects.get(pk=comment_pk)
            check_permission(request.user, comment)
        except Comment.DoesNotExist:
            return Response({'error': 'comment id does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            return Response({'error': 'user not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticatedOrReadOnly])
def create_get_notice_api(request):
    if request.method == 'GET':
        notices = Notice.objects.all()
        paginator = CustomPaginator()
        paginated_queryset = paginator.paginate_queryset(notices, request)
        all_notices = list(map(lambda x: NoticeSerializer(x).data, paginated_queryset))
        return paginator.get_paginated_response(all_notices)
    
    if request.method == 'PUT':
        serializer = NoticeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def get_update_notice_api(request, notice_pk):

    def check_permission(owner, notice):
        if owner != notice.owner:
            raise PermissionDenied('user not authorized to perform this action')
    if request.method == 'GET':
        try:
            notice =Notice.objects.get(pk=notice_pk)
            serializer = NoticeSerializer(notice)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Notice.DoesNotExist:
            return Response({'error': 'notice id does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'DELETE':
        try:
            notice = Notice.objects.get(pk=notice_pk)
            check_permission(request.user, notice)
            notice.delete()
            return Response({'notice_id': notice_pk, 'message': 'succesfully deleted'}, status=status.HTTP_200_OK)
        except Notice.DoesNotExist:
            return Response({'error': 'notice id does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PATCH':
        try:
            notice =Notice.objects.get(pk=notice_pk)
            check_permission(request.user, notice)
        except Notice.DoesNotExist:
            return Response({'error': 'notice id does not exist'}, status=status.HTTP_404_NOT_FOUND)
        serializer = NoticeSerializer(notice, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
