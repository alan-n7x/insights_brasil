"""Repositório para persistência de fatos de indicadores municipais.

Operações de upsert para a tabela fato que relaciona municípios,
indicadores, tempo e valores.
"""

from ibge.models import FatoIndicador, Tempo


class FatoIndicadorRepository:
    """Camada de persistência para o modelo FatoIndicador.

    Responsável apenas por operações de banco, sem regras de negócio.
    """

    @staticmethod
    def save(municipio, indicador, ano: int, valor: float):
        """Persiste um valor de indicador para um município em um ano específico.

        Cria o registro Tempo se necessário e realiza upsert em FatoIndicador.

        Args:
            municipio: Instância do modelo Municipio.
            indicador: Instância do modelo Indicador.
            ano: Ano de referência do dado.
            valor: Valor numérico do indicador.

        Returns:
            Tupla (objeto, criado) onde criado indica se foi uma inserção nova.
        """
        # Get or create Tempo record for the year
        tempo, _ = Tempo.objects.get_or_create(
            ano=ano,
            mes=None,
            trimestre=None
        )
        
        obj, created = FatoIndicador.objects.update_or_create(
            municipio=municipio,
            indicador=indicador,
            tempo=tempo,
            defaults={
                "valor": valor
            }
        )
        return obj, created