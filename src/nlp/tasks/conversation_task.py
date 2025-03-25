from crewai import Task, Agent

class ConversationTask(Task):
    def __init__(self, agent: Agent):
        """
        Creates a task for handling user conversation about travel.
        """
        super().__init__(
            description="""
                <DESCRIPTION>
                    Engaje em uma conversa natural com o usuário sobre suas necessidades de viagem
                    e interesses. Entenda seus requisitos, responda perguntas e
                    facilite o processo de busca de voos.
                </DESCRIPTION>
                
                <RULES>
                    - Mantenha um tom natural e conversacional durante toda a interação
                    - Responda apropriadamente a saudações e conversas casuais
                    - Faça perguntas esclarecedoras quando necessário para entender as necessidades de viagem
                    - Se o usuário estiver interessado em encontrar voos, colete os detalhes necessários:
                        - Local de origem
                        - Local de destino
                        - Data de partida
                        - Data de retorno (se aplicável)
                        - Número de passageiros
                    - Mantenha o contexto da conversa
                    - Quando o usuário perguntar sobre voos, use essas informações para ajudar o agente de busca de voos
                    - A mensagem do usuário estará disponível na variável 'message'
                    - O histórico do chat estará disponível na variável 'history'
                </RULES>
            """,
            agent=agent,
            expected_output="""
                <EXPECTED_OUTPUT>
                    - Respostas naturais e relevantes às mensagens do usuário
                    - Perguntas de acompanhamento apropriadas quando necessário
                    - Explicações claras das opções de voo quando fornecidas
                    - Informações úteis relacionadas a viagens com base nas perguntas do usuário
                </EXPECTED_OUTPUT>
            """
        )