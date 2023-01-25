from django.urls import path
from weather_API.views import weather

urlpatterns = [
    path('', weather, name='weather' ),
]
