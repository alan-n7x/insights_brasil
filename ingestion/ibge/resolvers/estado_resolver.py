from ibge.models import Estado


class EstadoResolver:

    def __init__(self):
        self._cache = {
            e.ibge_id: e
            for e in Estado.objects.all()
        }

    def get(self, ibge_id):
        return self._cache.get(ibge_id)