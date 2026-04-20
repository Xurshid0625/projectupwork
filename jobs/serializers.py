from rest_framework import serializers
from .models import Job, Proposal

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ['user']
        
        
class ProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = '__all__'
        read_only_fields = ['freelancer', 'status', 'job']