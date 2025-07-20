from rest_framework import serializers
from .models import User




class UserResponseSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(allow_null=True, required=False)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'profile_image', 'is_online', 'last_seen', 'created_at', 'updated_at']
        read_only_fields = ['id','last_seen' ,'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'name', 'password']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value
    
    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError("Name cannot be empty.")
        elif len(value) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long.")
        return value
    
    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            name=validated_data.get('name', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
    
    
    
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "User with this email does not exist."})

        if not user.check_password(password):
            raise serializers.ValidationError({"password": "Incorrect password."})

        attrs['user'] = user
        return attrs
