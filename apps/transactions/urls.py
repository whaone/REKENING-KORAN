from django.urls import path
from .views import TransactionUploadView, TransactionTaskStatusView

urlpatterns = [
    path(
        "upload/",
        TransactionUploadView.as_view(), name="api-transaction-upload"
    ),

    path(
        "status/<str:task_id>/",
        TransactionTaskStatusView.as_view(), name="transaction-status"
    ),

    path('list/', BankTransactionListView.as_view(), name='api-transaction-list'),
]
]