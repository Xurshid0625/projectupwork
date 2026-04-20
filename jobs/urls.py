from django.urls import path
from .views import JobView, JobDetailView, ApplyJobView, JobProposalsView, ProposalActionView, ContractView, MessageListView, SendMessageView

urlpatterns = [
   path('', JobView.as_view()),
   path('<int:pk>/', JobDetailView.as_view()),
   path('<int:job_id>/apply/', ApplyJobView.as_view()),
   path('<int:job_id>/proposals/', JobProposalsView.as_view()),
   path('proposals/<int:pk>/action/', ProposalActionView.as_view()),
   path('contracts/', ContractView.as_view()),
   path('contracts/<int:contract_id>/messages/', MessageListView.as_view()),
   path('contracts/<int:contract_id>/send/', SendMessageView.as_view()),
]