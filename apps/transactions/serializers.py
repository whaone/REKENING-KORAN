from rest_framework import serializers
from .models import TransactionImportJob

class TransactionUploadSerializer(serializers.Serializer):
    bank_code = serializers.ChoiceField(choices=['BCA', 'MANDIRI', 'BNI', 'BRI'])
    file = serializers.FileField()

    def validate_file(self, value):
        # Tambahkan validasi ekstensi file (csv, xlsx, pdf)
        if not value.name.endswith(('.csv', '.xlsx', '.pdf')):
            raise serializers.ValidationError("Format file tidak didukung.")
        return value

class BankTransactionSerializer(serializers.ModelSerializer):
    # Menambahkan label teks untuk pilihan DB/CR agar lebih mudah dibaca frontend
    tx_type_display = serializers.CharField(source='get_tx_type_display', read_only=True)

    class Meta:
        model = BankTransaction
        fields = [
            'id', 'bank_code', 'transaction_date', 'description', 
            'amount', 'tx_type', 'tx_type_display', 'reference_number', 'created_at'
        ]