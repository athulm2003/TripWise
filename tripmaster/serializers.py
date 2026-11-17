from rest_framework import serializers
from django.contrib.auth.models import User
from tripmaster.models import TripDb,TripMemberDb


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['username','email','password']
        
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model=TripDb
        fields="__all__"
        read_only_fields=["id","created_by","created_at","updated_at"]

class TripMemberSerializer(serializers.ModelSerializer):
    username=serializers.CharField(write_only=True)                                 #To accept a username from the API request.
    member_username=serializers.CharField(source='user.username',read_only=True)    #Retrieves the username from the related User object.
    member_user_id=serializers.IntegerField(source='user.id',read_only=True)        #To display the ID of the user who joined the trip.

    class Meta:
        model=TripMemberDb
        fields=['id','username','member_username','member_user_id','created_at']
        read_only_fields=['is','created_at']

    def validate_username(self,value):
        try:
            user=User.objects.get(username=value)
        except user.DoesNotExist:
            raise serializers.ValidationError("This User is Not Registered...")
        trip =self.context['trip']

        if user == trip.created_by:
            raise serializers.ValidationError("Trip creator is already the owner...!")
        if TripMemberDb.objects.filter(trip=trip,user=user).exists():
            raise serializers.ValidationError("This user is already a member...!")

        return value

    def create(self,validated_data):
        username=validated_data.pop("username")
        user=User.objects.get(username=username)
        trip=self.context['trip']
        return TripMemberDb.objects.create(trip=trip, user=user)