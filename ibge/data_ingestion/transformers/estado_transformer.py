class EstadoTransformer:

    def transform(self, estado):

        return {
            "ibge_id": estado["id"],
            "nome": estado["nome"],
            "sigla": estado["sigla"],
            "regiao": estado["regiao"]["nome"],
        }
