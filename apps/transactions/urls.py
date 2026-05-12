from django.urls import path
from .views import TransactionUploadView

urlpatterns = [
    path('upload/', TransactionUploadView.as_view(), name='transaction-upload'),
]