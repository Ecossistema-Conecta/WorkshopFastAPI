from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor

from tools import tools

llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.5)


prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """Sua única função é auxiliar em manipulações no banco de dados através de ferramentas.

        Sua regra NÚMERO UM e mais importante é: NUNCA chame a ferramenta `create_hero` sem ter TODAS as seguintes informações:
        - name (nome público)
        - real_identity (identidade real/civil)
        - universe (universo)
        - power_level (nível de poder)

        Se o usuário não fornecer TODAS essas informações de uma vez, sua ÚNICA resposta deve ser perguntar pelas informações que estão faltando. NÃO invente dados. NÃO prossiga. Apenas pergunte.
        """
    ),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])


agent = create_openai_tools_agent(llm, tools, prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
