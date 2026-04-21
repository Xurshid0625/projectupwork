from django.db import models
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from jobs.models import Favorite
from users.models import Notification

from .models import (
    Category,
    Contract,
    Conversation,
    Job,
    JobAlert,
    JobCategory,
    Proposal,
    Review,
    SavedCandidate,
)
from .serializers import (
    ContractSerializer,
    JobSerializer,
    MessageSerializer,
    ProposalSerializer,
    ReviewSerializer,
)


class CustomPagination(PageNumberPagination):
    page_size = 3


class JobView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=JobSerializer)
    def post(self, request):
        serializer = JobSerializer(data=request.data)

        if serializer.is_valid():
            job = serializer.save(user=request.user)

            category_id = request.data.get("category_id")
            if category_id:
                JobCategory.objects.create(job=job, category_id=category_id)

            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def get(self, request):
        jobs = Job.objects.all().order_by("-created_at")

        search = request.GET.get("search")

        if search:
            jobs = jobs.filter(title__icontains=search)

        category_id = request.GET.get("category")
        if category_id:
            jobs = jobs.filter(jobcategory__category_id=category_id)

        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)


class JobDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        job = get_object_or_404(Job, pk=pk)
        serializer = JobSerializer(job)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=JobSerializer)
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

    @swagger_auto_schema(request_body=ProposalSerializer)
    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)

        if Proposal.objects.filter(job=job, freelancer=request.user).exists():
            return Response({"error": "Already applied"}, status=400)

        Notification.objects.create(
            user=job.user, message=f"{request.user.username} applied to your job"
        )

        serializer = ProposalSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(freelancer=request.user, job=job)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


class AppliedJobsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        proposals = Proposal.objects.filter(freelancer=request.user)

        data = proposals.values(
            "id", "job__id", "job__title", "bid_amount", "status", "created_at"
        )

        return Response(data)


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

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"action": openapi.Schema(type=openapi.TYPE_STRING)},
        )
    )
    def post(self, request, pk):
        proposal = get_object_or_404(Proposal, id=pk)

        if proposal.job.user != request.user:
            return Response({"error": "Not allowed"}, status=403)

        action = request.data.get("action")

        if action == "accept":
            proposal.status = "accepted"
            proposal.save()

            Notification.objects.create(
                user=proposal.freelancer, message="Your proposal was accepted"
            )
            contract = Contract.objects.create(
                job=proposal.job,
                freelancer=proposal.freelancer,
                client=proposal.job.user,
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

    @swagger_auto_schema(request_body=MessageSerializer)
    def post(self, request, contract_id):
        conversation = get_object_or_404(Conversation, contract_id=contract_id)

        if request.user not in [
            conversation.contract.client,
            conversation.contract.freelancer,
        ]:
            return Response({"error": "Not allowed"}, status=403)

        serializer = MessageSerializer(data=request.data)

        if serializer.is_valid():
            message = serializer.save(sender=request.user, conversation=conversation)

            if request.user == conversation.contract.client:
                receiver = conversation.contract.freelancer
            else:
                receiver = conversation.contract.client

            Notification.objects.create(
                user=receiver, message=f"New message from {request.user.username}"
            )

            return Response(serializer.data)

        return Response(serializer.errors, status=400)


class MessageListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, contract_id):
        conversation = get_object_or_404(Conversation, contract_id=contract_id)

        messages = conversation.messages.all().order_by("created_at")
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)


class CreateReviewView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=ReviewSerializer)
    def post(self, request, contract_id):

        contract = get_object_or_404(Contract, id=contract_id)

        if request.user not in [contract.client, contract.freelancer]:
            return Response({"error": "Not allowed"}, status=403)

        if request.user == contract.client:
            reviewee = contract.freelancer
        else:
            reviewee = contract.client

        if Review.objects.filter(contract=contract, reviewer=request.user).exists():
            return Response({"error": "Already reviewed"}, status=400)

        serializer = ReviewSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(reviewer=request.user, reviewee=reviewee, contract=contract)
            return Response(serializer.data)

        return Response(serializer.errors, status=400)


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        applied_jobs = Proposal.objects.filter(freelancer=user).count()
        contracts = Contract.objects.filter(freelancer=user).count()
        favorites = Favorite.objects.filter(user=user).count()

        return Response(
            {
                "applied_jobs": applied_jobs,
                "contracts": contracts,
                "favorites": favorites,
            }
        )


class ToggleFavoriteView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={})
    )
    def post(self, request, pk):
        user = request.user
        job = get_object_or_404(Job, pk=pk)

        favorite = Favorite.objects.filter(user=user, job=job).first()

        if favorite:
            favorite.delete()
            return Response({"message": "Removed from favorites"})
        else:
            Favorite.objects.create(user=user, job=job)
            return Response({"message": "Added to favorites"})


class FavoriteJobsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        favorites = Favorite.objects.filter(user=request.user)

        data = favorites.values("job__id", "job__title")

        return Response(data)


class JobAlertView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        alerts = JobAlert.objects.filter(user=request.user)
        return Response(
            [{"id": a.id, "keyword": a.keyword, "location": a.location} for a in alerts]
        )

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "keyword": openapi.Schema(type=openapi.TYPE_STRING),
                "location": openapi.Schema(type=openapi.TYPE_STRING),
            },
        )
    )
    def post(self, request):
        alert = JobAlert.objects.create(
            user=request.user,
            keyword=request.data.get("keyword"),
            location=request.data.get("location", ""),
        )
        return Response({"message": "Alert created"})


class SavedCandidateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        saved = SavedCandidate.objects.filter(client=request.user)

        return Response(
            [
                {
                    "id": s.id,
                    "freelancer_id": s.freelancer.id,
                    "name": s.freelancer.username,
                }
                for s in saved
            ]
        )

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"freelancer": openapi.Schema(type=openapi.TYPE_INTEGER)},
        )
    )
    def post(self, request):
        freelancer_id = request.data.get("freelancer")

        obj, created = SavedCandidate.objects.get_or_create(
            client=request.user, freelancer_id=freelancer_id
        )

        if not created:
            return Response({"message": "Already saved"})

        return Response({"message": "Saved"})


class JobApplicationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)

        if job.user != request.user:
            return Response({"error": "Not allowed"}, status=403)

        proposals = Proposal.objects.filter(job=job)

        search = request.GET.get("search")
        if search:
            proposals = proposals.filter(freelancer__username__icontains=search)

        proposals = proposals.order_by("-created_at")

        paginator = CustomPagination()
        result = paginator.paginate_queryset(proposals, request)

        return Response(
            [
                {
                    "id": p.id,
                    "freelancer_id": p.freelancer.id,
                    "freelancer": p.freelancer.username,
                    "bid_amount": p.bid_amount,
                    "status": p.status,
                    "cover_letter": p.cover_letter,
                }
                for p in proposals
            ]
        )


class CategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categories = Category.objects.all()
        return Response([{"id": c.id, "name": c.name} for c in categories])

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"name": openapi.Schema(type=openapi.TYPE_STRING)},
        )
    )
    def post(self, request):
        name = request.data.get("name")

        if not name:
            return Response({"error": "Name required"}, status=400)

        category = Category.objects.create(name=name)

        return Response({"id": category.id, "name": category.name})
