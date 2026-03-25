import os
import streamlit as st
import boto3
from dotenv import load_dotenv

load_dotenv()

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Asistente NSR-10", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800&family=Barlow:wght@300;400;500&display=swap');

    :root {
        --yellow:     #F5C400;
        --yellow-dark:#D4A900;
        --gray-900:   #1A1A1A;
        --gray-800:   #2C2C2C;
        --gray-700:   #3D3D3D;
        --gray-500:   #6B6B6B;
        --gray-300:   #B0B0B0;
        --gray-100:   #F0F0F0;
        --white:      #FFFFFF;
        --stripe:     repeating-linear-gradient(
                        -45deg,
                        transparent,
                        transparent 6px,
                        rgba(245,196,0,0.15) 6px,
                        rgba(245,196,0,0.15) 12px
                      );
    }

    html, body, [data-testid="stAppViewContainer"] {
        background-color: var(--gray-900) !important;
        font-family: 'Barlow', sans-serif;
        color: var(--white);
    }

    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        inset: 0;
        background-image: radial-gradient(circle, rgba(255,255,255,0.03) 1px, transparent 1px);
        background-size: 28px 28px;
        pointer-events: none;
        z-index: 0;
    }

    [data-testid="stMain"] {
        background: transparent !important;
        padding-top: 0 !important;
    }

    .main-banner {
        background: var(--gray-800);
        border-bottom: 4px solid var(--yellow);
        padding: 28px 40px 22px;
        margin: -1rem -1rem 2rem -1rem;
        display: flex;
        align-items: center;
        gap: 20px;
        position: relative;
        overflow: hidden;
    }
    .main-banner::after {
        content: "";
        position: absolute;
        top: 0; right: 0;
        width: 260px; height: 100%;
        background: var(--stripe);
        opacity: 0.6;
    }
    .banner-text h1 {
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 2.4rem;
        font-weight: 800;
        color: var(--yellow);
        margin: 0;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .banner-text p {
        font-size: 0.95rem;
        color: var(--gray-300);
        margin: 4px 0 0;
        font-weight: 300;
        letter-spacing: 0.3px;
    }
    .badge {
        display: inline-block;
        background: var(--yellow);
        color: var(--gray-900);
        font-family: 'Barlow Condensed', sans-serif;
        font-weight: 700;
        font-size: 0.7rem;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        padding: 2px 10px;
        border-radius: 2px;
        margin-bottom: 6px;
    }

    [data-testid="stSidebar"] {
        background: var(--gray-800) !important;
        border-right: 3px solid var(--yellow) !important;
    }
    [data-testid="stSidebar"] * {
        color: var(--white) !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        font-family: 'Barlow Condensed', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        color: var(--yellow) !important;
        text-transform: uppercase;
    }
    [data-testid="stSidebar"] .stInfo {
        background: rgba(245,196,0,0.1) !important;
        border-left: 3px solid var(--yellow) !important;
        border-radius: 4px;
    }
    .sidebar-section-label {
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: var(--yellow) !important;
        margin: 16px 0 6px;
        border-bottom: 1px solid var(--gray-700);
        padding-bottom: 4px;
    }
    .example-chip {
        background: var(--gray-700);
        border-left: 3px solid var(--yellow);
        padding: 7px 12px;
        border-radius: 0 4px 4px 0;
        margin-bottom: 7px;
        font-size: 0.85rem;
        color: var(--gray-100) !important;
        font-style: italic;
    }

    /* Texto blanco en todos los mensajes del chat */
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li,
    [data-testid="stChatMessage"] span,
    [data-testid="stChatMessage"] strong,
    [data-testid="stChatMessage"] em {
        color: var(--white) !important;
    }
    [data-testid="stChatMessage"] {
        background: var(--gray-800) !important;
        border: 1px solid var(--gray-700) !important;
        border-radius: 6px !important;
        margin-bottom: 12px !important;
        padding: 14px 18px !important;
    }
    .stChatMessage:has([data-testid="chatAvatarIcon-user"]) {
        border-left: 4px solid var(--yellow) !important;
    }
    .stChatMessage:has([data-testid="chatAvatarIcon-assistant"]) {
        border-left: 4px solid var(--gray-500) !important;
    }

    [data-testid="stChatInputContainer"] {
        background: var(--gray-800) !important;
        border: 2px solid var(--gray-700) !important;
        border-radius: 8px !important;
        padding: 4px 8px !important;
    }
    [data-testid="stChatInputContainer"]:focus-within {
        border-color: var(--yellow) !important;
        box-shadow: 0 0 0 3px rgba(245,196,0,0.15) !important;
    }
    [data-testid="stChatInputContainer"] textarea {
        color: var(--white) !important;
        background: transparent !important;
        font-family: 'Barlow', sans-serif !important;
    }
    [data-testid="stChatInputContainer"] textarea::placeholder {
        color: var(--gray-500) !important;
    }
    [data-testid="stChatInputContainer"] button {
        background: var(--yellow) !important;
        color: var(--gray-900) !important;
        border-radius: 6px !important;
    }

    [data-testid="stExpander"] {
        background: var(--gray-800) !important;
        border: 1px solid var(--gray-700) !important;
        border-top: 3px solid var(--yellow) !important;
        border-radius: 6px !important;
    }
    [data-testid="stExpander"] summary {
        color: var(--yellow) !important;
        font-family: 'Barlow Condensed', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    [data-testid="stExpander"] code {
        background: var(--gray-700) !important;
        color: var(--yellow) !important;
        border-radius: 3px !important;
        padding: 2px 6px !important;
    }

    [data-testid="stSidebar"] button {
        background: var(--gray-700) !important;
        color: var(--white) !important;
        border: 1px solid var(--gray-500) !important;
        border-radius: 5px !important;
        font-family: 'Barlow Condensed', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        transition: all 0.2s !important;
    }
    [data-testid="stSidebar"] button:hover {
        background: var(--yellow) !important;
        color: var(--gray-900) !important;
        border-color: var(--yellow) !important;
    }

    [data-testid="stSpinner"] p {
        color: var(--yellow) !important;
        font-family: 'Barlow Condensed', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
    }

    hr { border-color: var(--gray-700) !important; }

    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: var(--gray-800); }
    ::-webkit-scrollbar-thumb { background: var(--gray-700); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--yellow); }

    [data-testid="stAlert"] {
        background: rgba(245,196,0,0.08) !important;
        border-left: 4px solid var(--yellow) !important;
        border-radius: 4px !important;
        color: var(--white) !important;
    }
</style>
""", unsafe_allow_html=True)

# Banner principal
st.markdown("""
<div class="main-banner">
    <div class="banner-text">
        <div class="badge">Colombia · NSR-10</div>
        <h1>Asistente Experto NSR-10</h1>
        <p>Consulta rapida, precisa y con referencias al Reglamento Colombiano de Construccion Sismo Resistente.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 2. CONFIGURACIÓN TÉCNICA (variables de entorno) ---
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
KB_ID = os.environ.get("KB_ID")
MODEL_ID = os.environ.get("MODEL_ID")

if not KB_ID or not MODEL_ID:
    st.error("Faltan variables de entorno obligatorias (KB_ID y/o MODEL_ID). "
             "Crea un archivo `.env` con las variables requeridas. Consulta el README.md.")
    st.stop()

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.image("bot.JPG", use_container_width=True)
    st.markdown("<h2 style='margin-top:12px;'>Sobre el Asistente</h2>", unsafe_allow_html=True)
    st.info("Este bot utiliza IA para buscar respuestas dentro de los documentos oficiales de la **NSR-10**.")
    st.markdown("<div class='sidebar-section-label'>Ejemplos de consultas</div>", unsafe_allow_html=True)
    st.markdown("<div class='example-chip'>Cual es el recubrimiento minimo para vigas?</div>", unsafe_allow_html=True)
    st.markdown("<div class='example-chip'>Requisitos para mamposteria estructural.</div>", unsafe_allow_html=True)
    st.markdown("<div class='example-chip'>Que ensayos se exigen para el concreto?</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-section-label'>Herramientas</div>", unsafe_allow_html=True)
    if st.button("Limpiar Historial de Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.bedrock_session_id = None
        st.rerun()

# --- 4. CLIENTE BEDROCK ---
@st.cache_resource
def get_bedrock_client(region):
    return boto3.client('bedrock-agent-runtime', region_name=region)

bedrock_kb_client = get_bedrock_client(AWS_REGION)

# --- 5. HISTORIAL DE CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hola! Soy tu asistente normativo. En que te puedo ayudar hoy con la NSR-10?"
    })

if "bedrock_session_id" not in st.session_state:
    st.session_state.bedrock_session_id = None

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 6. ENTRADA Y RESPUESTA ---
if prompt := st.chat_input("Escribe tu consulta sobre la norma aqui..."):

    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        with st.spinner("Analizando documentos de la norma..."):
            try:
                request_payload = {
                    "input": {"text": prompt},
                    "retrieveAndGenerateConfiguration": {
                        "type": "KNOWLEDGE_BASE",
                        "knowledgeBaseConfiguration": {
                            "knowledgeBaseId": KB_ID,
                            "modelArn": MODEL_ID,
                            "retrievalConfiguration": {
                                "vectorSearchConfiguration": {
                                    "numberOfResults": 5,
                                    "overrideSearchType": "SEMANTIC"
                                }
                            }
                        }
                    }
                }

                if st.session_state.bedrock_session_id:
                    request_payload["sessionId"] = st.session_state.bedrock_session_id

                response = bedrock_kb_client.retrieve_and_generate(**request_payload)

                generated_text = response['output']['text']
                st.session_state.bedrock_session_id = response.get('sessionId')

                message_placeholder.markdown(generated_text)
                st.session_state.messages.append({"role": "assistant", "content": generated_text})

                if 'citations' in response and response['citations']:
                    with st.expander("Ver fuentes normativas consultadas"):
                        for i, citation in enumerate(response['citations']):
                            for ref in citation.get('retrievedReferences', []):
                                raw_uri = ref['location']['s3Location']['uri']
                                clean_file_name = raw_uri.split('/')[-1].replace('%20', ' ')
                                st.markdown(f"**Documento:** `{clean_file_name}`")
                                st.caption(f"_{ref['content']['text'][:200]}..._")
                                st.divider()

            except Exception as e:
                print(f"[ERROR Bedrock] {e}")  # Log interno del servidor
                message_placeholder.error("Lo siento, hubo un problema técnico de conexión. Intenta de nuevo más tarde.")