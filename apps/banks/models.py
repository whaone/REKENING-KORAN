from django.db import models

class Bank(models.Model):
    name = models.CharField(max_length=100) # Contoh: BCA, Mandiri
    code = models.CharField(max_length=20, unique=True) # Contoh: BCA, BMRI

    def __str__(self):
        return self.name

class BankAccount(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='accounts')
    account_number = models.CharField(max_length=50, unique=True)
    account_name = models.CharField(max_length=255)
    currency = models.CharField(max_length=10, default="IDR")

    def __str__(self):
        return f"{self.account_number} - {self.account_name}"
