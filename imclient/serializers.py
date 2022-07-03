from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import ImFile

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

class ImFileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model =  ImFile
        fields = ['fname','fsize', 'fdate', 'fhuman']
