from ibge.models.territorio import Municipio


class MunicipioResolver:

    def __init__(self):

        self._cache = {m.ibge_id: m for m in Municipio.objects.all()}

    def get(self, ibge_id):

        return self._cache.get(ibge_id)
