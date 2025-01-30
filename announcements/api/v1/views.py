from rest_framework.decorators import api_view
from announcements.models import Notice, Comment
from announcements.serializers import NoticeSerializer, CommentSerializer
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response

@api_view(['GET', 'PUT'])
def create_get_comment_api(request):
    if request.method == 'GET':
        comments = Comment.objects.all()
        all_comments = list(map(lambda x: CommentSerializer(x).data, comments))
        return Response({'comments': all_comments}, status=status.HTTP_200_OK)
    
    if request.method == 'PUT':
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PATCH'])
def get_update_comment_api(request, comment_pk):
    if request.method == 'GET':
        try:
            comment =Comment.objects.get(pk=comment_pk)
            serializer = CommentSerializer(comment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response({'error': 'comment id does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PATCH':
        try:
            comment =Comment.objects.get(pk=comment_pk)
        except Comment.DoesNotExist:
            return Response({'error': 'comment id does not exist'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT']) 
def create_get_notice_api(request):
    if request.method == 'GET':
        notices = Notice.objects.all()
        all_notices = list(map(lambda x: NoticeSerializer(x).data, notices))
        return Response({'notices': all_notices}, status=status.HTTP_200_OK)
    
    if request.method == 'PUT':
        serializer = NoticeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PATCH'])
def get_update_notice_api(request, notice_pk):
    if request.method == 'GET':
        try:
            notice =Notice.objects.get(pk=notice_pk)
            serializer = NoticeSerializer(notice)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except notice.DoesNotExist:
            return Response({'error': 'notice id does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PATCH':
        try:
            notice =Notice.objects.get(pk=notice_pk)
        except Notice.DoesNotExist:
            return Response({'error': 'notice id does not exist'}, status=status.HTTP_404_NOT_FOUND)
        serializer = NoticeSerializer(notice, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def user_comments(request):
    pass

@api_view(['GET'])
def user_notices(request):
    pass