import streamlit as st
from groq import Groq
import json
import re

# Configuração da página
st.set_page_config(page_title="Isekai RPG: O Herói Renascido", page_icon="🐉", layout="centered")

# --- CONEXÃO COM A IA (GROQ) ---
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except:
    st.error("Ops! A chave do Groq não foi encontrada no cofre.")
    st.stop()

# --- INICIALIZAÇÃO DA MEMÓRIA ---
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

if "fichas" not in st.session_state:
    st.session_state.fichas = """=== HERÓI PRINCIPAL ===
Nome: ?
Raça: ?
Classe: ? | Nível: 1
XP: 0/300
HP: ? | CA: ?

ATRIBUTOS:
FOR: ? | DES: ? | CON: ?
INT: ? | SAB: ? | CAR: ?

ATAQUES E MAGIAS:
- ?

=== COMPANHEIROS ===
(Vazio)
"""

if "escudo_mestre" not in st.session_state:
    st.session_state.escudo_mestre = """[TABELAS RÁPIDAS E REGRAS DA CASA]
- Regra da Casa: Poções de cura como Ação Bônus curam metade, como Ação curam o máximo.
(Cole aqui tabelas do seu Escudo do Mestre)"""

# --- BARRA LATERAL: CONFIGURAÇÕES, ESCUDO, FICHAS E SAVE ---
with st.sidebar:
    st.header("🌍 Gerador de Mundos")
    tipo_aventura = st.selectbox(
        "Duração da Aventura:",
        ["Campanha Longa (Épica)", "One-Shot (Aventura Rápida)", "Missão de Guilda (Curta)"]
    )
    tom_historia = st.selectbox(
        "Tom do Isekai:",
        ["Clássico (Fantasia Heroica)", "Dark Fantasy (Sombrio e Perigoso)", "Comédia (Absurdo e Engraçado)"]
    )
    
    st.divider()
    
    st.header("🛡️ Escudo do Mestre")
    novo_escudo = st.text_area("Tabelas e Regras Rápidas:", value=st.session_state.escudo_mestre, height=150)
    if novo_escudo != st.session_state.escudo_mestre:
        st.session_state.escudo_mestre = novo_escudo

    st.divider()

    st.header("📜 Ficha do Personagem")
    nova_ficha_manual = st.text_area("Seu Pergaminho:", value=st.session_state.fichas, height=250)
    if nova_ficha_manual != st.session_state.fichas:
        st.session_state.fichas = nova_ficha_manual
    
    st.divider()
    st.header("💾 Progresso")
    
    # SALVAR JOGO
    if len(st.session_state.mensagens) > 0:
        save_dict = {
            "mensagens": st.session_state.mensagens,
            "fichas": st.session_state.fichas,
            "escudo": st.session_state.escudo_mestre
        }
        save_data = json.dumps(save_dict, indent=4)
        st.download_button(
            label="⬇️ Salvar Cristal (.json)",
            data=save_data,
            file_name="isekai_save.json",
            mime="application/json",
            use_container_width=True
        )
    
    # CARREGAR JOGO
    arquivo_upload = st.file_uploader("📂 Carregar Cristal", type=["json"])
    if arquivo_upload is not None:
        try:
            dados_carregados = json.load(arquivo_upload)
            if st.button("✨ Confirmar Carregamento", use_container_width=True):
                if isinstance(dados_carregados, dict) and "mensagens" in dados_carregados:
                    st.session_state.mensagens = dados_carregados["mensagens"]
                    st.session_state.fichas = dados_carregados.get("fichas", st.session_state.fichas)
                    st.session_state.escudo_mestre = dados_carregados.get("escudo", st.session_state.escudo_mestre)
                else:
                    st.session_state.mensagens = dados_carregados
                st.success("Aventura carregada!")
                st.rerun()
        except:
            st.error("Arquivo inválido!")

    if st.button("🔄 Nova Aventura"):
        st.session_state.mensagens = []
        st.session_state.fichas = "=== HERÓI PRINCIPAL ===\n(Crie seu personagem com a Deusa)"
        st.rerun()

# --- PROMPT MESTRE CRIADOR ---
prompt_base = f"""
Você é o Mestre de Jogo (DM) e o AUTOR PRINCIPAL de uma aventura RPG Anime Isekai (Regras D&D 5e).
O formato da aventura atual é: {tipo_aventura}.
O tom da história atual é: {tom_historia}.

O SEU PAPEL COMO AUTOR:
1. O JOGADOR NÃO CRIA A HISTÓRIA, ELE APENAS REAGE. VOCÊ DEVE CRIAR O MUNDO, OS MISTÉRIOS, OS VILÕES E AS MISSÕES.
2. Após a criação do personagem pela Deusa, jogue o herói no mundo e APRESENTE UM GANCHO DE AVENTURA CLARO (um ataque à vila, um cartaz de procurado, um NPC pedindo ajuda urgente).
3. Seja proativo: não pergunte apenas "o que você faz?", descreva eventos acontecendo ao redor do jogador para forçá-lo a agir.
4. Crie NPCs memoráveis e Companheiros de Grupo que interajam com o herói.

REGRAS DE SISTEMA (D&D 5e):
1. Narre a aventura, role os dados (d20) secretamente e aplique os resultados com base na ficha do jogador.
2. Guie a criação da ficha no início e ofereça as opções exatas de classe quando houver Level Up.
3. ATUALIZAÇÃO DA FICHA: SEMPRE que a ficha mudar, envie a Ficha Atualizada NO FINAL da mensagem, escondida dentro das tags <FICHAS> e </FICHAS>.
4. Consulte sempre as regras no DADOS DO ESCUDO DO MESTRE abaixo antes de agir.
"""

# --- PREPARAÇÃO DO CÉREBRO DA IA ---
mensagem_sistema_final = prompt_base + f"\n\n--- DADOS DO ESCUDO DO MESTRE ---\n{st.session_state.escudo_mestre}\n\n--- FICHAS ATUAIS DO SISTEMA ---\n{st.session_state.fichas}\n------------------------------"
mensagens_para_api = [{"role": "system", "content": mensagem_sistema_final}] + st.session_state.mensagens

# --- INTERFACE VISUAL PRINCIPAL ---
st.title("⚔️ Isekai RPG: D&D 5e")

for msg in st.session_state.mensagens:
    avatar = "🧙‍♂️" if msg["role"] == "assistant" else "🤺"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

acao_jogador = st.chat_input("O que você faz ou diz?")

def processar_resposta_ia(mensagens_enviadas):
    resposta_ia = client.chat.completions.create(
        messages=mensagens_enviadas,
        model="llama-3.3-70b-versatile",
        temperature=0.8, # Aumentado levemente para dar mais criatividade narrativa ao DM
        max_tokens=1000,
    )
    texto_bruto = resposta_ia.choices[0].message.content
    
    padrao_fichas = r"<FICHAS>(.*?)</FICHAS>"
    match = re.search(padrao_fichas, texto_bruto, re.DOTALL | re.IGNORECASE)
    
    texto_limpo = texto_bruto
    if match:
        novas_fichas = match.group(1).strip()
        st.session_state.fichas = novas_fichas
        texto_limpo = re.sub(padrao_fichas, "", texto_bruto, flags=re.DOTALL | re.IGNORECASE).strip()
        
    return texto_limpo

if len(st.session_state.mensagens) == 0 and not acao_jogador:
    with st.spinner("A Deusa da Reencarnação está falando..."):
        try:
            texto_dm_limpo = processar_resposta_ia(mensagens_para_api)
            st.session_state.mensagens.append({"role": "assistant", "content": texto_dm_limpo})
            st.rerun()
        except Exception as e:
            st.error(f"Erro do Mestre: {e}")

if acao_jogador:
    st.session_state.mensagens.append({"role": "user", "content": acao_jogador})
    mensagens_para_api.append({"role": "user", "content": acao_jogador}) 
    
    with st.chat_message("user", avatar="🤺"):
        st.markdown(acao_jogador)
        
    with st.chat_message("assistant", avatar="🧙‍♂️"):
        caixa_resposta = st.empty()
        caixa_resposta.markdown("🎲 *O Mestre está construindo o mundo e rolando os dados...*")
        
        try:
            texto_dm_limpo = processar_resposta_ia(mensagens_para_api)
            caixa_resposta.markdown(texto_dm_limpo)
            st.session_state.mensagens.append({"role": "assistant", "content": texto_dm_limpo})
            st.rerun()
            
        except Exception as e:
            caixa_resposta.error(f"O Mestre deixou o escudo cair: {e}")
