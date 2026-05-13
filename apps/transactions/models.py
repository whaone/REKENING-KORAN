import hashlib
from django.db import models
from django.conf import settings

class TransactionImportJob(models.Model):
    """
    Model untuk melacak status pemrosesan file yang diunggah.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='import_jobs'
    )
    bank_code = models.CharField(max_length=20)  # Contoh: BCA, MANDIRI, BNI
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500) # Path di storage (MinIO/S3/Local)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    task_id = models.CharField(max_length=255, null=True, blank=True) # ID dari Celery
    total_rows = models.IntegerField(default=0)
    error_log = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Job {self.id} - {self.bank_code} ({self.status})"


class BankTransaction(models.Model):
    """
    Model inti untuk menyimpan data transaksi dari berbagai bank dalam format standar.
    """
    TX_TYPE_CHOICES = [
        ('DB', 'Debit'),
        ('CR', 'Credit'),
    ]

    # Relasi ke job yang memproses transaksi ini
    import_job = models.ForeignKey(
        TransactionImportJob, 
        on_delete=models.CASCADE, 
        related_name='transactions'
    )
    
    bank_code = models.CharField(max_length=20, db_index=True)
    account_number = models.CharField(max_length=50, null=True, blank=True)
    transaction_date = models.DateField(db_index=True)
    description = models.TextField()
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    tx_type = models.CharField(max_length=2, choices=TX_TYPE_CHOICES)
    reference_number = models.CharField(max_length=100, null=True, blank=True)
    
    # Signature digunakan untuk mencegah data ganda (Idempotency)
    # Hash dari (bank_code + date + description + amount + tx_type)
    signature = models.CharField(
        max_length=64, 
        unique=True, 
        db_index=True,
        help_text="Unique hash to prevent duplicate transactions"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Bank Transaction"
        verbose_name_plural = "Bank Transactions"
        ordering = ['-transaction_date', '-created_at']

    def __str__(self):
        return f"[{self.bank_code}] {self.transaction_date} - {self.amount} ({self.tx_type})"

    @staticmethod
    def generate_signature(bank_code, date, description, amount, tx_type):
        """
        Fungsi statis untuk menghasilkan hash unik bagi setiap baris transaksi.
        """
        data_string = f"{bank_code}|{date}|{description}|{amount}|{tx_type}"
        return hashlib.sha256(data_string.encode('utf-8')).hexdigest()