import streamlit as st

from app.agent.agent import agent_executor

st.set_page_config(page_title="Chat Demo", page_icon="💬")

st.title("Chat Agent e Tools")

# Iniciliaza variavel session para referência em outros pontos da aplicação
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "Olá! Como posso ajudar você hoje?"})

# Renderiza o histórico de mensagens
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Digite sua mensagem..."):
    chat_history = []
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Exibe a mensagem do usuário
    with st.chat_message("user"):
        st.markdown(prompt)

    # Repete Prompt
    response = agent_executor.invoke({"input": prompt, "chat_history": chat_history})
    assistant_response = response["output"]
    with st.chat_message("assistant"):
        st.markdown(assistant_response)

    # Salva no histórico
    st.session_state.messages.append({"role": "assistant", "content": response})
