import csv
from datetime import datetime
from apps.parsers.base import BaseBankParser

class BCACSVParser(BaseBankParser):
    def parse(self, file_content):
        transactions = []
        # Mengasumsikan file_content adalah file-like object dari CSV bank
        reader = csv.DictReader(file_content)
        
        for row in reader:
            # Normalisasi data sesuai skema database kita (AI-C)
            normalized_data = {
                'date': datetime.strptime(row['Tgl'], '%d/%m/%Y'),
                'description': row['Keterangan'],
                'amount': float(row['Jumlah'].replace(',', '')),
                'direction': 'CREDIT' if row['DB/CR'] == 'CR' else 'DEBIT',
                'balance_after': float(row['Saldo'].replace(',', ''))
            }
            transactions.append(normalized_data)
            
        return transactions
