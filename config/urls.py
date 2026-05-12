from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Nantinya kita akan tambahkan route API di sini
    path('api/transactions/', include('apps.transactions.urls')),
]
