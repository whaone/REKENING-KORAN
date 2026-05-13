import os
import uuid
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import TransactionImportJob
from .tasks import process_transaction_file
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from .models import BankTransaction
from .serializers import BankTransactionSerializer

class TransactionUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        bank_code = request.data.get('bank_code')
        file_obj = request.FILES.get('file')

        if not bank_code or not file_obj:
            return Response(
                {"error": "bank_code dan file wajib diisi."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. Simpan file ke direktori sementara
        # Gunakan UUID agar nama file tidak bentrok jika banyak user upload bersamaan
        file_ext = os.path.splitext(file_obj.name)[1]
        temp_file_name = f"upload_{uuid.uuid4()}{file_ext}"
        path = default_storage.save(f'tmp/uploads/{temp_file_name}', ContentFile(file_obj.read()))
        full_path = os.path.join(default_storage.location, path)

        # 2. Buat Record Job di Database
        job = TransactionImportJob.objects.create(
            user=request.user,
            bank_code=bank_code,
            file_name=file_obj.name,
            file_path=full_path,
            status='PENDING'
        )

        # 3. Pemicu Celery Task (Kirim ID saja, biarkan worker yang kerja berat)
        process_transaction_file.delay(job.id)

        return Response({
            "message": "File diterima dan sedang diproses.",
            "job_id": job.id,
            "status": job.status
        }, status=status.HTTP_202_ACCEPTED)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100 # Default 100 transaksi per halaman
    page_size_query_param = 'page_size'
    max_page_size = 1000

class BankTransactionListView(ListAPIView):
    """
    API untuk melihat daftar transaksi dengan fitur:
    - Pagination
    - Filter by Bank Code
    - Filter by Date Range
    - Filter by Type (Debit/Credit)
    """
    serializer_class = BankTransactionSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = BankTransaction.objects.all()
        
        # Ambil parameter dari URL query (misal: ?bank=BCA&start_date=2023-01-01)
        bank = self.request.query_params.get('bank')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        tx_type = self.request.query_params.get('type') # DB atau CR

        if bank:
            queryset = queryset.filter(bank_code=bank)
        if start_date and end_date:
            queryset = queryset.filter(transaction_date__range=[start_date, end_date])
        if tx_type:
            queryset = queryset.filter(tx_type=tx_type)

        return queryset