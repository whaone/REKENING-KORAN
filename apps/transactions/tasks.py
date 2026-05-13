import os
import logging
from celery import shared_task
from django.db import transaction, IntegrityError
from django.utils import timezone
from .models import TransactionImportJob, BankTransaction
from apps.parsers.adapters.bca_parser import BCACSVParser  # Asumsi parser yang sudah dibuat

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def process_transaction_file(self, job_id):
    """
    Task utama untuk memproses file rekening koran secara asynchronous.
    Menggunakan Job ID untuk melacak status di database.
    """
    try:
        # 1. Ambil data Job
        job = TransactionImportJob.objects.get(id=job_id)
        job.status = 'PROCESSING'
        job.task_id = self.request.id
        job.save()

        # 2. Inisialisasi Parser berdasarkan Bank Code
        # Di sini kita bisa menggunakan Factory Pattern jika bank sudah banyak
        if job.bank_code == 'BCA':
            parser = BCACSVParser()
        else:
            raise ValueError(f"Parser untuk bank {job.bank_code} belum didukung.")

        # 3. Parsing File
        # Membaca file dari path yang tersimpan di job.file_path
        with open(job.file_path, 'r') as f:
            parsed_data = parser.parse(f.read())

        # 4. Siapkan Objek untuk Bulk Insert (Efisien & Ringan)
        transaction_objects = []
        for item in parsed_data:
            # Generate signature untuk Idempotency (Cek Duplikat)
            sig = BankTransaction.generate_signature(
                bank_code=job.bank_code,
                date=item['date'],
                description=item['description'],
                amount=item['amount'],
                tx_type=item['type']
                signature=sig
            )

            transaction_objects.append(
                BankTransaction(
                    import_job=job,
                    bank_code=job.bank_code,
                    transaction_date=item['date'],
                    description=item['description'],
                    amount=item['amount'],
                    tx_type=item['type'],
                    reference_number=item.get('reference_number'),
                    signature=sig
                )
            )

        # 5. Eksekusi Database dengan Atomic Transaction & Bulk Create
        # ignore_conflicts=True membuat mesin tetap ringan karena tidak crash saat ada data ganda
        with transaction.atomic():
            created_objs = BankTransaction.objects.bulk_create(
                transaction_objects, 
                batch_size=1000, 
                ignore_conflicts=True
            )
            
            # 6. Update Status Job Sukses
            job.status = 'SUCCESS'
            job.total_rows = len(transaction_objects)
            job.save()

        return f"Job {job_id} selesai. {len(transaction_objects)} baris diproses."

    except TransactionImportJob.DoesNotExist:
        logger.error(f"Job ID {job_id} tidak ditemukan.")
        return "Job tidak ditemukan."

    except Exception as e:
        # 7. Update Status Job Gagal & Log Error
       logger.error(f"Error Job {job_id}: {str(e)}")
        if job:
            job.status = 'FAILED'
            job.error_log = str(e)
            job.save()
            
            # Tetap hapus file meskipun gagal agar tidak menumpuk sampah
            if os.path.exists(job.file_path):
                os.remove(job.file_path)
        return f"Job {job_id} Gagal.