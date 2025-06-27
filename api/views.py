from typing import Any

import base64
from django.contrib.auth import login as dj_login, logout as dj_logout
from django.contrib.auth.models import AnonymousUser
from django.db import transaction, models
from django.http import HttpRequest
from rest_framework import status, generics, viewsets, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from werkzeug.security import generate_password_hash, check_password_hash
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import User, Club, UserClubs
from .serializers import UserSerializer, ClubSerializer


class UserViewSet(viewsets.ViewSet):
    """Implements /api/users endpoints"""

    permission_classes = [permissions.AllowAny]

    def list(self, request: HttpRequest):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def retrieve(self, request: HttpRequest, pk: int = None):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user)
        # Add clubs info
        clubs = (
            Club.objects.filter(userclubs__user_id=user.id)
            .values("id", "name")
        )
        data = serializer.data
        data["clubs"] = list(clubs)
        return Response(data)

    def create(self, request: HttpRequest):
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Check existing username/email
        username = serializer.validated_data["username"]
        email = serializer.validated_data["email"]
        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            return Response({"error": "Username or email already in use"}, status=status.HTTP_400_BAD_REQUEST)

        # Hash password if provided
        password_raw = request.data.get("password")
        if not password_raw:
            return Response({"error": "Password is required"}, status=status.HTTP_400_BAD_REQUEST)
        hashed_password = generate_password_hash(password_raw)

        # Create user
        with transaction.atomic():
            user = User.objects.create(
                username=username,
                email=email,
                password=hashed_password,
                firstname=serializer.validated_data["firstname"],
                lastname=serializer.validated_data["lastname"],
                profile_image=serializer.validated_data.get("profile_image"),
            )

        response_data = UserSerializer(user).data
        return Response(response_data, status=status.HTTP_201_CREATED)

    def destroy(self, request: HttpRequest, pk: int = None):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response({"message": "User deleted successfully"})

    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request: HttpRequest):
        q = request.query_params.get("q", "").strip()
        if not q:
            return Response([])

        users = User.objects.filter(
            models.Q(firstname__icontains=q)
            | models.Q(lastname__icontains=q)
            | models.Q(firstname__icontains=q.split(" ")[0], lastname__icontains=" ".join(q.split(" ")[1:]))
        )
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="upload_picture", permission_classes=[permissions.IsAuthenticated])
    def upload_picture(self, request: HttpRequest):
        user_id = request.user.id if request.user and not isinstance(request.user, AnonymousUser) else None
        if not user_id:
            return Response({"error": "Not logged in"}, status=status.HTTP_401_UNAUTHORIZED)

        file = request.FILES.get("profilePicture")
        if not file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        file_bytes = file.read()
        user = User.objects.get(pk=user_id)
        user.profile_image = file_bytes
        user.save()

        encoded = base64.b64encode(file_bytes).decode("utf-8")
        mime_type = "image/jpeg"  # naive
        data_uri = f"data:{mime_type};base64,{encoded}"
        return Response({"profile_image": data_uri})
    
    @action(detail=False, methods=["post"], url_path="upload_phone", permission_classes=[permissions.IsAuthenticated])
    def upload_phone(self, request: HttpRequest):
        user_id = request.user.id if request.user and not isinstance(request.user, AnonymousUser) else None
        if not user_id:
            return Response({"error": "Not logged in"}, status=status.HTTP_401_UNAUTHORIZED)

        phone = request.data.get("phone")
        if not phone:
            return Response({"error": "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.get(pk=user_id)
        user.phone = phone
        user.save()

        return Response({"message": "Phone number updated successfully", "phone": user.phone})

class ClubViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, url_path="by_college/(?P<college_id>[^/.]+)")
    def by_college(self, request, college_id: int = None):
        clubs = Club.objects.filter(college_clubs__college=college_id).values("id", "name")
        return Response(list(clubs))


@method_decorator(csrf_exempt, name="dispatch")
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # Disable auth to allow anonymous login

    def post(self, request: HttpRequest):
        try:
            username = request.data.get("username")
            password = request.data.get("password")
            if not username or not password:
                return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)

            if check_password_hash(user.password, password):
                # Persist session
                request.session["user_id"] = user.id
                return Response({"message": "Login successful", "user": UserSerializer(user).data})
            else:
                return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            # Catch-all to ensure JSON response (important for front-end fetch())
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name="dispatch")
class LogoutView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        request.session.flush()
        return Response({"message": "Logged out"})


class CurrentUserView(APIView):
    """Return currently logged-in user info"""

    def get(self, request: HttpRequest):
        user_id = request.session.get("user_id")
        if not user_id:
            return Response({"user": None})
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"user": None})
        data = UserSerializer(user).data
        clubs = Club.objects.filter(userclubs__user_id=user_id).values("id", "name")
        data["clubs"] = list(clubs)
        return Response({"user": data})


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def check_username(request: HttpRequest):
    username = request.data.get("username")
    if not username:
        return Response({"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)
    exists = User.objects.filter(username=username).exists()
    return Response({"exists": exists})


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def check_email(request: HttpRequest):
    email = request.data.get("email")
    if not email:
        return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
    exists = User.objects.filter(email=email).exists()
    return Response({"exists": exists})


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def test_db(request):
    try:
        # Simple ping by fetching 1
        User.objects.values_list("id", flat=True).first()
        return Response({"status": "success", "message": "Database connection successful"})
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 