import base64
from rest_framework import serializers
from .models import User, Club


class Base64ImageField(serializers.Field):
    """Helper to convert binary image to base64-encoded data URI on serialization."""

    def to_representation(self, value):
        if value is None:
            return None
        encoded = base64.b64encode(value).decode('utf-8')
        # Default to jpeg; consumers know type
        return f"data:image/jpeg;base64,{encoded}"

    def to_internal_value(self, data):
        # Expect data URI or raw base64 string
        if isinstance(data, bytes):
            return data
        if data.startswith('data:'):
            header, encoded = data.split(',', 1)
            return base64.b64decode(encoded)
        return base64.b64decode(data)


class UserSerializer(serializers.ModelSerializer):
    profile_image = Base64ImageField(source='profile_image', allow_null=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'firstname', 'lastname', 'profile_image']


class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = ['id', 'name'] 