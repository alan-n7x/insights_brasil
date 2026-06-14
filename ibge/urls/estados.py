from django.urls import path
from ibge.views.views import estados

urlpatterns = [
    path("", estados, name="estados"),
]