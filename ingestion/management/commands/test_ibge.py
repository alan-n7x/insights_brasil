# management/commands/test_ibge.py

from django.core.management.base import BaseCommand

from ingestion.ibge.repositories.estado_repository import EstadoRepository


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        estados = EstadoRepository()
        
        print(estados.listar())
