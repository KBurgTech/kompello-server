from rest_framework import serializers


class SimpleResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
