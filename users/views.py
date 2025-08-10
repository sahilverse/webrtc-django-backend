from rest_framework import status, generics

from rest_framework.permissions import AllowAny

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import authenticate
from django.db import transaction

from myproject.responses import api_response
from django.contrib.auth import get_user_model


from .serializers import (UserCreateSerializer, UserLoginSerializer, UserResponseSerializer)

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from loguru import logger


User = get_user_model()
class RegisterUserView(generics.CreateAPIView):
   permission_classes = [AllowAny]
   serializer_class = UserCreateSerializer
   
   @transaction.atomic
   def perform_create(self, serializer):
       user = serializer.save()
       return user
   
   @swagger_auto_schema(
        operation_description="Register a new user.",
        request_body=UserCreateSerializer,
        responses={
            201: openapi.Response(description="User register successfully"),
            400: openapi.Response(description="Bad Request"),
            500: openapi.Response(description="Internal Server error"),
        },
        tags=["User"],
    )
    
   def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                    self.perform_create(serializer)
                    return api_response(
                        is_success=True,
                        status_code=status.HTTP_201_CREATED,
                        result={
                            "message": "User Created Successfully."
                        }
                    )
            return api_response(
                    is_success=False,
                    error_message=serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return api_response(
                    is_success=False,
                    error_message= "Internal Server Error",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
          
          
          
          
class UserLoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    authentication_classes = [JWTAuthentication]
    serializer_class = UserLoginSerializer
    
    @swagger_auto_schema(
        operation_description="Login user and obtain tokens.",
        responses={
            200: openapi.Response(description="Login successful."),
            400: openapi.Response(description="Bad request"),
            401: openapi.Response(description="Invalid credentials"),
            500: openapi.Response(description="Internal server error"),
        },
        tags=["User"],
    )

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data.get('email')
                password = serializer.validated_data.get('password')

                user = authenticate(request, email=email, password=password)

                if user is not None:
                    user_data = UserResponseSerializer(user).data

                    refresh = RefreshToken.for_user(user)
                    refresh_token = str(refresh)
                    access_token = str(refresh.access_token)

                    return api_response(
                        is_success=True,
                        status_code=status.HTTP_200_OK,
                        result={
                            "user": user_data,
                            "refresh_token": refresh_token,
                            "access_token": access_token,
                        }
                    )
                else:
                    return api_response(
                        is_success=False,
                        error_message="Invalid email or password.",
                        status_code=status.HTTP_401_UNAUTHORIZED,
                    )
            return api_response(
                is_success=False,
                error_message=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return api_response(
                is_success=False,
                error_message="Internal Server Error",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = UserResponseSerializer

    def get_object(self):
        return self.request.user
    
    @swagger_auto_schema(
        operation_description="Get user profile.",
        responses={
            200: openapi.Response(description="User details retrieved successfully."),
            404: openapi.Response(description="User not found"),
            500: openapi.Response(description="Internal server error"),
        },
        tags=["User"],
    )
    def get(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            serializer = self.serializer_class(user)
            return api_response(
                is_success=True,
                status_code=status.HTTP_200_OK,
                result=serializer.data
            )
        except User.DoesNotExist:
            return api_response(
                is_success=False,
                error_message="User not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return api_response(
                is_success=False,
                error_message="Internal Server Error",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            
            
            
class UserSearchView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserResponseSerializer
    
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['first_name', 'last_name', 'email']
    filterset_fields = ['is_online', 'last_seen', 'is_active']
    
    def get_queryset(self):
        return User.objects.all()

    @swagger_auto_schema(
        operation_description="Search users by first name, last name, or email (using 'search'). Filter by is_online, last_seen, and is_active.",
        manual_parameters=[
            openapi.Parameter(
                'search', openapi.IN_QUERY,
                description="Search by first name, last name, or email (partial matches allowed)",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'is_online', openapi.IN_QUERY,
                description="Filter users by online status (true/false)",
                type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter(
                'last_seen', openapi.IN_QUERY,
                description="Filter users by last seen timestamp (ISO 8601 format)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATETIME
            ),
            openapi.Parameter(
                'is_active', openapi.IN_QUERY,
                description="Filter users by active status (true/false)",
                type=openapi.TYPE_BOOLEAN
            ),
        ],
        responses={200: openapi.Response(description="Users retrieved successfully.")},
        tags=["User"],
    )
    def get(self, request, *args, **kwargs):
        try:
            response = super().get(request, *args, **kwargs)
            return api_response(
                is_success=True,
                status_code=status.HTTP_200_OK,
                result={
                    "message": "Users retrieved successfully.",
                    "data": response.data
                }
            )
        except Exception as e:
            logger.error(f"Error in UserSearchView: {str(e)}") 
            return api_response(
                is_success=False,
                error_message="Internal Server Error",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )