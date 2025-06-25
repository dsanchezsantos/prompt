import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# --- Configuração da API Google Gemini ---
# Pega a chave da API do arquivo .env
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("Chave de API do Google Gemini não encontrada! Crie um arquivo .env com GOOGLE_API_KEY='SUA_CHAVE'.")
    st.stop() # Interrompe a execução se a chave não for encontrada

genai.configure(api_key=GOOGLE_API_KEY)

# Inicializa o modelo Gemini Pro
model = genai.GenerativeModel('gemini-2.5-flash')

# --- SEU CONTEXTO/PROMPT DE SISTEMA ---
# Este é o "treinamento" que você quer que o modelo siga.
# Você pode editar este texto para definir o papel da sua IA.
system_prompt = """
A partir de agora, você é um guia turístico extremamente entusiasmado e apaixonado por Arraial do Cabo, Rio de Janeiro.
Sua missão é dar dicas incríveis de praias, passeios de barco, atividades aquáticas (como mergulho e snorkeling), e pontos turísticos escondidos da região.
Sua linguagem deve ser sempre informal, amigável e acolhedora, como se estivesse conversando com um amigo que vai visitar a cidade.
Use emojis ocasionalmente para transmitir seu entusiasmo! 🎉
**Regras importantes:**
1. Nunca mencione preços de passeios, hospedagens ou qualquer custo financeiro.
2. Mantenha o foco exclusivamente em Arraial do Cabo. Se a pergunta for sobre outra cidade ou assunto, responda que seu conhecimento é exclusivo de Arraial.
3. Incentive sempre a exploração das belezas naturais e o contato com a natureza.
4. Ao final de cada resposta, sempre pergunte se o usuário tem mais alguma dúvida ou curiosidade sobre Arraial.
"""

st.set_page_config(page_title="Guia de Arraial do Cabo!", page_icon="🏖️")
st.title("Bem-vindo ao seu Guia de Arraial do Cabo! 🏖️")
st.markdown("Pergunte-me qualquer coisa sobre as maravilhas desta cidade paradisíaca!")

# --- Lógica do Chatbot ---
# Inicializa o histórico de mensagens na sessão do Streamlit
# O primeiro item é o prompt de sistema, que não será exibido, mas é enviado à API.
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "user", "parts": [system_prompt]} # 'user' é o papel que define o modelo
    ]

# Exibe o histórico de mensagens (exceto o prompt de sistema inicial)
# O modelo Gemini usa 'user' para o usuário e 'model' para as respostas da IA.
for message in st.session_state.messages:
    if message["parts"][0] != system_prompt: # Não exibe o prompt inicial
        with st.chat_message("user" if message["role"] == "user" else "assistant"):
            st.markdown(message["parts"][0])

# Campo de entrada para o usuário
if prompt := st.chat_input("Qual sua dúvida sobre Arraial do Cabo?"):
    # Adiciona a pergunta do usuário ao histórico da sessão (para exibir e enviar ao modelo)
    st.session_state.messages.append({"role": "user", "parts": [prompt]})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Buscando as melhores dicas de Arraial..."):
            try:
                # Cria a conversa com o modelo, incluindo o histórico e o prompt de sistema
                # O parâmetro 'history' garante que o contexto seja mantido.
                chat = model.start_chat(history=st.session_state.messages)
                response = chat.send_message(prompt) # Envia a última pergunta do usuário

                full_response = response.text
                st.markdown(full_response)
                # Adiciona a resposta da IA ao histórico da sessão
                st.session_state.messages.append({"role": "model", "parts": [full_response]})
            except Exception as e:
                st.error(f"Ocorreu um erro ao processar sua pergunta: {e}")
                st.markdown("Por favor, tente novamente mais tarde.")