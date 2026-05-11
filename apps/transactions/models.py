import hashlib
from django.db import models
from apps.banks.models import BankAccount

class Transaction(models.Model):
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='transactions')
    date = models.DateTimeField()
    description = models.TextField()
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    direction = models.CharField(max_length=10, choices=[('DEBIT', 'Debit'), ('CREDIT', 'Credit')])
    balance_after = models.DecimalField(max_digits=20, decimal_places=2)
    
    # Security & Integrity: Mencegah Duplikasi
    transaction_hash = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # AI-C: Generate unique hash otomatis jika belum ada
        if not self.transaction_hash:
            hash_string = f"{self.account.id}{self.date}{self.amount}{self.description}"
            self.transaction_hash = hashlib.sha256(hash_string.encode()).hexdigest()
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['transaction_hash']),
            models.Index(fields=['date']),
        ]
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} - {self.amount} ({self.direction})"
