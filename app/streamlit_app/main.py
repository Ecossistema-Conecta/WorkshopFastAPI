import streamlit as st

st.set_page_config(page_title="Chat Demo", page_icon="💬")

st.title("Chat Agent Demo")

# Iniciliaza variavel session para referência em outros pontos da aplicação
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "Olá! Como posso ajudar você hoje?"})
    
# Renderiza o histórico de mensagens
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Digite sua mensagem..."):

    st.session_state.messages.append({"role": "user", "content": prompt})

    # Exibe a mensagem do usuário
    with st.chat_message("user"):
        st.markdown(prompt)

    # Repete Prompt
    response = f"Você disse: **{prompt}**"
    with st.chat_message("assistant"):
        st.markdown(response)

    # Salva no histórico
    st.session_state.messages.append({"role": "assistant", "content": response})