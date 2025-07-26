# hostel/serializers.py

from rest_framework import serializers
from .models import User, Hostel, Room, Student, Complaint, LeaveRequest, Notice
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user_type'] = user.user_type
        return token

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type', 'phone', 'address']

class HostelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hostel
        fields = '__all__'

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    room = RoomSerializer()
    
    class Meta:
        model = Student
        fields = '__all__'

class ComplaintSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    
    class Meta:
        model = Complaint
        fields = '__all__'

class LeaveRequestSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    approved_by = UserSerializer(read_only=True)
    
    class Meta:
        model = LeaveRequest
        fields = '__all__'

class NoticeSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Notice
        fields = '__all__'