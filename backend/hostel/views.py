# hostel/views.py

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import User, Hostel, Room, Student, Complaint, LeaveRequest, Notice
from .serializers import (
    UserSerializer, HostelSerializer, RoomSerializer,
    StudentSerializer, ComplaintSerializer, LeaveRequestSerializer,
    NoticeSerializer
)
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class HostelViewSet(viewsets.ModelViewSet):
    queryset = Hostel.objects.all()
    serializer_class = HostelSerializer
    permission_classes = [permissions.IsAuthenticated]

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        hostel_id = self.request.query_params.get('hostel_id')
        if hostel_id:
            queryset = queryset.filter(hostel_id=hostel_id)
        return queryset

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def me(self, request):
        student = get_object_or_404(Student, user=request.user)
        serializer = self.get_serializer(student)
        return Response(serializer.data)

class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.user_type == 'STUDENT':
            student = get_object_or_404(Student, user=self.request.user)
            queryset = queryset.filter(student=student)
        elif self.request.user.user_type == 'WARDEN':
            hostels = Hostel.objects.filter(warden=self.request.user)
            rooms = Room.objects.filter(hostel__in=hostels)
            students = Student.objects.filter(room__in=rooms)
            queryset = queryset.filter(student__in=students)
        return queryset

    def perform_create(self, serializer):
        if self.request.user.user_type == 'STUDENT':
            student = get_object_or_404(Student, user=self.request.user)
            serializer.save(student=student)
        else:
            serializer.save()

class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.user_type == 'STUDENT':
            student = get_object_or_404(Student, user=self.request.user)
            queryset = queryset.filter(student=student)
        elif self.request.user.user_type == 'WARDEN':
            hostels = Hostel.objects.filter(warden=self.request.user)
            rooms = Room.objects.filter(hostel__in=hostels)
            students = Student.objects.filter(room__in=rooms)
            queryset = queryset.filter(student__in=students)
        return queryset

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        leave_request = self.get_object()
        if request.user.user_type not in ['ADMIN', 'WARDEN']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        leave_request.status = 'APPROVED'
        leave_request.approved_by = request.user
        leave_request.save()
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        leave_request = self.get_object()
        if request.user.user_type not in ['ADMIN', 'WARDEN']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        leave_request.status = 'REJECTED'
        leave_request.approved_by = request.user
        leave_request.save()
        return Response({'status': 'rejected'})

class NoticeViewSet(viewsets.ModelViewSet):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.user_type == 'STUDENT':
            student = get_object_or_404(Student, user=self.request.user)
            if student.room:
                queryset = queryset.filter(
                    Q(is_for_all=True) | 
                    Q(hostels=student.room.hostel)
                )
            else:
                queryset = queryset.filter(is_for_all=True)
        elif self.request.user.user_type == 'WARDEN':
            hostels = Hostel.objects.filter(warden=self.request.user)
            queryset = queryset.filter(
                Q(is_for_all=True) | 
                Q(hostels__in=hostels)
            )
        return queryset.distinct()