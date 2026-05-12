import csv
from datetime import datetime
from decimal import Decimal

class BCACSVParser:
    
    def parse(self, file_content):
        """
        Logika untuk memproses file CSV dari BCA
        """
        transactions = []
        # Decode content jika dalam bentuk bytes
        decoded_file = file_content.decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        
        for row in reader:
            # Sesuaikan mapping kolom dengan format CSV BCA Anda
            try:
                transactions.append({
                    'date': self._parse_date(row.get('Tgl', row.get('Date'))),
                    'description': row.get('Keterangan', row.get('Description')),
                    'amount': self._parse_amount(row.get('Jumlah', row.get('Amount'))),
                    'type': row.get('DB/CR', '').strip()
                })
            except Exception as e:
                continue
                
        return transactions

    def _parse_date(self, date_str):
        # Sesuaikan format tanggal BCA (contoh: DD/MM)
        return datetime.now().date() # Placeholder

    def _parse_amount(self, amount_str):
        if not amount_str: return Decimal('0')
        return Decimal(amount_str.replace(',', ''))