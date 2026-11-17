from django.shortcuts import render,get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from tripmaster.serializers import UserSerializer,TripSerializer,TripMemberSerializer
from tripmaster.models import TripDb,TripMemberDb
from rest_framework import authentication,permissions,serializers
from tripmaster.permissions import OwnerOnly
from rest_framework.exceptions import PermissionDenied

# Create your views here.

class SignUpView(APIView):
    def post(self,request):
        form_data=request.data
        serializer_instance=UserSerializer(data=form_data)
        if serializer_instance.is_valid():
            serializer_instance.save()
            return Response(data=serializer_instance.data,status=210)
        else:
            return Response(serializer_instance.errors,status=400)
    def get(self,request):
        qs=User.objects.all()
        serializer_instance=UserSerializer(qs,many=True)
        return Response(data=serializer_instance.data)
    def delete(self,request,pk):                                # No Need to Use a Serializer Here
        User.objects.get(id=pk).delete()                     # Because don't need to convert or validate any complex incoming data.
        return Response({
            "Message" : "User Deleted Successfully...!"
        })

class TripListCreateView(APIView):
    authentication_classes=[authentication.BasicAuthentication]
    permission_classes=[OwnerOnly]

    def get(self,request):
        qs=TripDb.objects.filter(created_by=request.user)
        serializer_instance=TripSerializer(qs,many=True)
        return Response(data=serializer_instance.data)
        
    def post(self,request):
        form_data=request.data
        serializer_instance=TripSerializer(data=form_data)
        if serializer_instance.is_valid():
            serializer_instance.save(created_by=request.user)
            return Response(data={
                "Message" : "Trip Created Successfully...!",
                "Your Trip details" : serializer_instance.data
            })
        else:
            return Response(data=serializer_instance.errors)

class TripRetrieveUpdateDeleteView(APIView):
    authentication_classes=[authentication.BasicAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    
    def get(self,request,pk):
        trip_obj=get_object_or_404(TripDb,id=pk)
        # 1 Trip to Wayanad Wayanad  5..
        if trip_obj.created_by == request.user:
            serializer_instance=TripSerializer(trip_obj)
            return Response(data=serializer_instance.data)
        else:
            raise serializers.ValidationError("Access Denied...!")

    def put(self,request,pk):
        trip_obj=get_object_or_404(TripDb,id=pk)
        if trip_obj.created_by != request.user:            #only the person who created the trip can have the access to update the trip
            raise serializers.ValidationError("Access Denied...!")
        form_data=request.data
        serializer_instance=TripSerializer(data=form_data, instance=trip_obj)
        if serializer_instance.is_valid():
            serializer_instance.save()
            return Response(data={
                "Message" : "Trip Details Updated Successfully..!",
                "Updated Data": serializer_instance.data
            })
        else:
            return Response(data=serializer_instance.errors)        #Tells the serializer which existing record should be updated.

    def delete(self,request,pk):
        trip_obj=get_object_or_404(TripDb,id=pk)
        if trip_obj.created_by == request.user:
            trip_obj.delete()
            return Response(data={
                "Message" : "Trip Deleted Successfully....!"
            })
        else:
            raise serializers.ValidationError("Access Denied...!")

class TripMemberListCreateView(APIView):
    authentication_classes=[authentication.BasicAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    
    def get(self,request,trip_id):
        #Get the Trip
        trip_object=get_object_or_404(TripDb,id=trip_id)
        # 3  Trip to Pune      Deepu

        is_owner=trip_object.created_by == request.user
        is_member=TripMemberDb.objects.filter(trip=trip_object,user=request.user).exists()

        if not (is_owner or is_member):
            raise PermissionDenied("You are not allowed to access this trip...!")

        members=TripMemberDb.objects.filter(trip=trip_object)
        serializer_instance=TripMemberSerializer(members,many=True)
        return Response(data=serializer_instance.data)

    def post(self,request,trip_id):
        trip_object=get_object_or_404(TripDb,id=trip_id)

        if trip_object.created_by != request.user:
            raise PermissionDenied("Only the Trip owner can add Members...!")
        
        form_data=request.data
        serializer_instance=TripMemberSerializer(data=form_data,context={'trip': trip_object})
        if serializer_instance.is_valid():
            serializer_instance.save()
            return Response(data={
                "Message" : "Member Added Successfully...!"
            })
        else:
            return Response(data=serializer_instance.errors)

    # def delete(self,request,trip_id,pk):
    #     trip_object=get_object_or_404(TripDb,id=trip_id)

    #     if trip_object.created_by == request.user:
    #         TripMemberDb.objects.get(id=pk).delete()
    #         return Response(data={
    #             "Message" : "The Member Deleted Successfully..!"
    #         })
    #     else:
    #         raise PermissionDenied("Only the Trip Owner can Delete Members..!")

        #OR
class TripMemberDeleteView(APIView):
    authentication_classes=[authentication.BasicAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    
    def delete(self,request,trip_id,member_id):
        trip_object=get_object_or_404(TripDb,id=trip_id)

        if trip_object.created_by !=request.user:
            raise PermissionDenied("Only the Trip Owner can Delete Members..!")
        member_object=get_object_or_404(TripMemberDb,id=member_id,trip=trip_object)
        member_object.delete()
        return Response(data={
            "Message" : "Trip member deleted Sucessfully...!"
        })