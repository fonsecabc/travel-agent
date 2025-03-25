import logging
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, Type
from crewai.tools import BaseTool
from crewai_tools import SerperDevTool

logger = logging.getLogger(__name__)

class FlightSearchToolInput(BaseModel):
    """Input schema for FlightSearchTool."""
    origin: str = Field(..., description="Local de origem (pode ser código de aeroporto ou nome da cidade)")
    destination: str = Field(..., description="Local de destino (pode ser código de aeroporto ou nome da cidade)")
    departure_date: str = Field(..., description="Data de partida no formato YYYY-MM-DD")
    return_date: Optional[str] = Field(None, description="Data de retorno no formato YYYY-MM-DD (opcional para voos só de ida)")
    adults: int = Field(1, description="Número de passageiros adultos")
    children: int = Field(0, description="Número de passageiros crianças")
    infants_in_seat: int = Field(0, description="Número de bebês com assento")
    infants_on_lap: int = Field(0, description="Número de bebês no colo")

class FlightSearchTool(BaseTool):
    """
    Ferramenta de busca de voos usando o SerperDevTool.
    """
    name: str = "Ferramenta de Busca de Voos"
    description: str = "Busca voos em tempo real usando o Serper."
    args_schema: Type[BaseModel] = FlightSearchToolInput

    def __init__(self):
        super().__init__()
        self.serper_tool = SerperDevTool()

    def _run(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        adults: int = 1,
        children: int = 0,
        infants_in_seat: int = 0,
        infants_on_lap: int = 0,
    ) -> Dict[str, Any]:
        """
        Busca voos usando o SerperDevTool.
        
        Args:
            origin: Local de origem (pode ser código de aeroporto ou nome da cidade)
            destination: Local de destino (pode ser código de aeroporto ou nome da cidade)
            departure_date: Data de partida no formato YYYY-MM-DD
            return_date: Data de retorno no formato YYYY-MM-DD (opcional para voos só de ida)
            adults: Número de passageiros adultos
            children: Número de passageiros crianças
            infants_in_seat: Número de bebês com assento
            infants_on_lap: Número de bebês no colo
            
        Returns:
            Dicionário com resultados da busca
        """
        logger.info(f"Buscando voos de {origin} para {destination} em {departure_date}")
        
        try:
            # Constrói a query de busca
            search_query = f"passagens aéreas voos mais baratas de {origin} para {destination} em {departure_date}"
            if return_date:
                search_query += f" retorno {return_date}"
            
            if adults > 1 or children > 0 or infants_in_seat > 0 or infants_on_lap > 0:
                search_query += f" para {adults} adultos"
                if children > 0:
                    search_query += f", {children} crianças"
                if infants_in_seat > 0:
                    search_query += f", {infants_in_seat} bebês com assento"
                if infants_on_lap > 0:
                    search_query += f", {infants_on_lap} bebês no colo"

            # Executa a busca usando o SerperDevTool
            results = self.serper_tool.run(search_query)

            # Processa e formata os resultados
            formatted_results = {
                "search_query": search_query,
                "results": results,
                "origin": origin,
                "destination": destination,
                "departure_date": departure_date,
                "return_date": return_date,
                "passengers": {
                    "adults": adults,
                    "children": children,
                    "infants_in_seat": infants_in_seat,
                    "infants_on_lap": infants_on_lap
                }
            }

            return formatted_results
            
        except Exception as e:
            logger.error(f"Erro ao buscar voos: {str(e)}")
            return {
                "error": str(e),
                "message": "Falha ao encontrar voos. Por favor, verifique os parâmetros da busca."
            } 