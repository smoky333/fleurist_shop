from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  # Админка
    path('', include('app.urls')),   # Основные маршруты вашего приложения
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Обработка медиафайлов в режиме отладки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
