class IBGELocalidadesClient:

    def __init__(self, client):

        self.client = client

    def get_estados(self):

        return self.client.get("v1", "localidades/estados")

    def get_municipios(self):

        return self.client.get("v1", "localidades/municipios")
