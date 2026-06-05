from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .serializers import RegisterSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):

    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():

        serializer.save()

        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user:
        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'username': user.username,
        })

    return Response(
        {'error': 'Invalid credentials'},
        status=status.HTTP_401_UNAUTHORIZED,
    )



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):

    try:

        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"error": "Refresh token required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        token = RefreshToken(refresh_token)

        token.blacklist()

        return Response(
            {"message": "Logout successful"},
            status=status.HTTP_200_OK
        )

    except Exception as e:

        return Response(
             {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )