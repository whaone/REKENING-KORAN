from abc import ABC, abstractmethod

class BaseBankParser(ABC):
    """
    Base class untuk semua bank adapter (AI-D).
    Setiap bank memiliki format kolom yang berbeda.
    """
    
    @abstractmethod
    def parse(self, file_path):
        """
        Mengembalikan list of dictionary yang sudah dinormalisasi.
        """
        pass
