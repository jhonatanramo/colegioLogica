from django.core.management.base import BaseCommand
from config.models import Iglesia, Usuario  # importa tus modelos correctamente

class Command(BaseCommand):
    help = 'Seed initial data'

    def handle(self, *args, **kwargs):
        # Datos a insertar
        data = [
            {'nombre':'El Torno'},
            {'nombre':'Jorochito'},
            {'nombre':'Tiquipalla'},
            {'nombre':'La Angostura'},
            {'nombre':'La Guardia'},
            {'nombre':'Km 6'},
            {'nombre':'La Central'},
            {'nombre':'Otro'},
        ]

        # Crear registros
        for item in data:
            Iglesia.objects.get_or_create(nombre=item['nombre'])

        self.stdout.write(self.style.SUCCESS('Datos iniciales cargados correctamente!'))
