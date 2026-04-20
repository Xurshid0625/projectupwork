from django.urls import path
from .views import JobView, JobDetailView, ApplyJobView, JobProposalsView, ProposalActionView, ContractView, MessageListView, SendMessageView, CreateReviewView, DashboardView, ToggleFavoriteView, AppliedJobsView, FavoriteJobsView, JobAlertView, SavedCandidateView, JobApplicationsView

urlpatterns = [
   path('', JobView.as_view()),
   path('<int:pk>/', JobDetailView.as_view()),
   path('<int:job_id>/apply/', ApplyJobView.as_view()),
   path('<int:job_id>/proposals/', JobProposalsView.as_view()),
   path('proposals/<int:pk>/action/', ProposalActionView.as_view()),
   path('contracts/', ContractView.as_view()),
   path('contracts/<int:contract_id>/messages/', MessageListView.as_view()),
   path('contracts/<int:contract_id>/send/', SendMessageView.as_view()),
   path('contracts/<int:contract_id>/review/', CreateReviewView.as_view()),
   path('dashboard/', DashboardView.as_view()),
   path('jobs/<int:pk>/favorite/', ToggleFavoriteView.as_view()),
   path('applied-jobs/', AppliedJobsView.as_view()),
   path('favorites/', FavoriteJobsView.as_view()),
   path('job-alerts/', JobAlertView.as_view()),
   path('saved-candidates/', SavedCandidateView.as_view()),
   path('jobs/<int:job_id>/applications/', JobApplicationsView.as_view()),
]