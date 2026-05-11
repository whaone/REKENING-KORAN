from apps.transactions.models import Transaction
from django.db import transaction

class TransactionParserService:
    def __init__(self, parser_instance, account):
        self.parser = parser_instance
        self.account = account

    def process_file(self, file_content):
        parsed_data = self.parser.parse(file_content)
        new_transactions = []

        with transaction.atomic():
            for data in parsed_data:
                # Membuat objek transaksi tanpa menyimpannya dulu (memory-only)
                tx = Transaction(
                    account=self.account,
                    **data
                )
                # Logic hashing otomatis di model akan mencegah duplikasi (AI-C)
                # Cek apakah hash sudah ada di database
                if not Transaction.objects.filter(transaction_hash=tx.transaction_hash).exists():
                    new_transactions.append(tx)

            # Simpan semua transaksi baru sekaligus (Performance Strategy)
            if new_transactions:
                Transaction.objects.bulk_create(new_transactions)
        
        return len(new_transactions)
