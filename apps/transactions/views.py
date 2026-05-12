from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from django.shortcuts import get_object_or_404

from apps.banks.models import BankAccount
from apps.parsers.adapters.bca_parser import BCACSVParser
from apps.parsers.services import TransactionParserService

class TransactionUploadView(APIView):
    # Atribut ini sudah cukup, tidak perlu import decorator parser_classes
    parser_classes = [MultiPartParser] 

    def post(self, request, *args, **kwargs):
        serializer = TransactionUploadSerializer(data=request.data)
        
        if serializer.is_valid():
            account_id = serializer.validated_data['bank_account_id']
            file_obj = serializer.validated_data['file']
            
            # 1. Ambil objek rekening bank
            account = get_object_or_404(BankAccount, id=account_id)
            
            # 2. Inisialisasi Parser (Nantinya bisa otomatis pilih berdasarkan kode bank)
            # Untuk sekarang kita gunakan BCA Adapter sebagai default
            parser = BCACSVParser()
            service = TransactionParserService(parser, account)
            
            try:
                # 3. Proses file
                count = service.process_file(file_obj.read())
                
                return Response({
                    "status": "success",
                    "message": f"Berhasil memproses {count} transaksi baru.",
                    "data": {"imported_count": count}
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    "status": "error",
                    "message": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)