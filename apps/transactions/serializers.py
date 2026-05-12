from rest_framework import serializers

class TransactionUploadSerializer(serializers.Serializer):
    bank_account_id = serializers.IntegerField()
    file = serializers.FileField()