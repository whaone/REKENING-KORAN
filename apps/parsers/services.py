from django.db import transaction
from apps.transactions.models import Transaction

class TransactionParserService:
    def __init__(self, parser_instance, account):
        self.parser = parser_instance
        self.account = account

    def process_file(self, file_content):
        # 1. Parsing data mentah menggunakan adapter
        parsed_data = self.parser.parse(file_content)
        new_transactions = []

        # 2. Proses validasi dalam satu transaksi database (atomic)
        with transaction.atomic():
            for data in parsed_data:
                tx = Transaction(account=self.account, **data)
                
                # Model Transaction secara otomatis membuat hash unik (AI-C)
                # untuk mencegah duplikasi (Idempotency)
                if not Transaction.objects.filter(transaction_hash=tx.transaction_hash).exists():
                    new_transactions.append(tx)

            # 3. Simpan secara massal untuk efisiensi tinggi
            if new_transactions:
                Transaction.objects.bulk_create(new_transactions)
        
        return len(new_transactions)