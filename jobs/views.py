from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Job, Proposal, Contract, Conversation
from .serializers import JobSerializer, ProposalSerializer, ContractSerializer, MessageSerializer
from django.db import models
from django.shortcuts import get_object_or_404



class JobView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = JobSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def get(self, request):
        jobs = Job.objects.all().order_by('-created_at')
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)


class JobDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        job = get_object_or_404(Job, pk=pk)
        serializer = JobSerializer(job)
        return Response(serializer.data)

    def put(self, request, pk):
        job = get_object_or_404(Job, pk=pk)

        if job.user != request.user:
            return Response({"error": "Not allowed"}, status=403)

        serializer = JobSerializer(job, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        job = get_object_or_404(Job, pk=pk)

        if job.user != request.user:
            return Response({"error": "Not allowed"}, status=403)

        job.delete()
        return Response({"message": "Deleted"})
    
    
    
class ApplyJobView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)

        # ❗ oldin apply qilganmi tekshiramiz
        if Proposal.objects.filter(job=job, freelancer=request.user).exists():
            return Response({"error": "Already applied"}, status=400)

        serializer = ProposalSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(
                freelancer=request.user,
                job=job
            )
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)
    
class JobProposalsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)

        if job.user != request.user:
            return Response({"error": "Not allowed"}, status=403)

        proposals = Proposal.objects.filter(job=job)
        serializer = ProposalSerializer(proposals, many=True)
        return Response(serializer.data)
    
    
class ProposalActionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        proposal = get_object_or_404(Proposal, id=pk)

        if proposal.job.user != request.user:
            return Response({"error": "Not allowed"}, status=403)

        action = request.data.get("action")

        if action == "accept":
            proposal.status = "accepted"
            proposal.save()
            
            contract = Contract.objects.create(
                job=proposal.job,
                freelancer=proposal.freelancer,
                client=proposal.job.user
            )
            
            Conversation.objects.create(contract=contract)

            return Response({"message": "Accepted, contract and chat created"})

        elif action == "reject":
                proposal.status = "rejected"
                proposal.save()
                return Response({"message": "Rejected"})

        return Response({"error": "Invalid action"}, status=400)
    
class ContractView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        contracts = Contract.objects.filter(
            models.Q(client=request.user) | models.Q(freelancer=request.user)
        )

        serializer = ContractSerializer(contracts, many=True)
        return Response(serializer.data)
    
class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, contract_id):
        conversation = get_object_or_404(Conversation, contract_id=contract_id)

        # ❗ faqat shu contract userlari yozishi mumkin
        if request.user not in [conversation.contract.client, conversation.contract.freelancer]:
            return Response({"error": "Not allowed"}, status=403)

        serializer = MessageSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(
                sender=request.user,
                conversation=conversation
            )
            return Response(serializer.data)

        return Response(serializer.errors, status=400)
    
class MessageListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, contract_id):
        conversation = get_object_or_404(Conversation, contract_id=contract_id)

        messages = conversation.messages.all().order_by('created_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
