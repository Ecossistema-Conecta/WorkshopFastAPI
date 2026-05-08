import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from app.agent.agent import agent_executor
from app.services.heroes import HeroService

st.set_page_config(page_title="Chat Demo", page_icon="💬", layout="wide")

def render_sidebar():
    with st.sidebar:
        st.markdown("## 🦸 Heróis")
        st.divider()
        with HeroService() as svc:
            heroes = svc.get_all_heroes()

        if not heroes:
            st.caption("Nenhum herói ainda. Peça ao agente para criar um!")
            return

        palette = ["#e63946", "#2196f3"]
        for i, hero in enumerate(heroes):
            color = palette[i % 2]
            power_pct = min(hero.power_level or 0, 100)
            st.markdown(
                f"""
                <div style="
                    background: #1e1e2e;
                    border-left: 4px solid {color};
                    border-radius: 8px;
                    padding: 10px 14px;
                    margin-bottom: 10px;
                ">
                    <div style="font-weight:700; font-size:15px; color:#fff;">{hero.name}</div>
                    <div style="font-size:12px; color:#aaa; margin:2px 0 6px;">
                        <span style="
                            background:{color}33;
                            color:{color};
                            border-radius:4px;
                            padding:1px 7px;
                            font-weight:600;
                        ">{hero.universe}</span>
                        &nbsp;·&nbsp;{hero.real_identity}
                    </div>
                    <div style="font-size:11px; color:#888; margin-bottom:4px;">Nível de poder</div>
                    <div style="background:#333; border-radius:4px; height:6px; width:100%;">
                        <div style="background:{color}; width:{power_pct}%; height:6px; border-radius:4px;"></div>
                    </div>
                    <div style="font-size:11px; color:{color}; text-align:right; margin-top:2px;">{hero.power_level}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

render_sidebar()

st.title("Chat Agent e Tools")

# Iniciliaza variavel session para referência em outros pontos da aplicação
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "Olá! Como posso ajudar você hoje?"})

# Inicializa histórico LangChain
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Renderiza o histórico de mensagens
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Digite sua mensagem..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    st.session_state.chat_history.append(
        HumanMessage(content=prompt)
    )

    # Exibe a mensagem do usuário
    with st.chat_message("user"):
        st.markdown(prompt)

    # Repete Prompt
    response = agent_executor.invoke({"input": prompt, "chat_history": st.session_state.chat_history[:-1]})
    assistant_response = response["output"]
    with st.chat_message("assistant"):
        st.markdown(assistant_response)

    # Salva no histórico
    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_response}
    )

    # Salva resposta LangChain
    st.session_state.chat_history.append(
        AIMessage(content=assistant_response)
    )

    st.rerun()
