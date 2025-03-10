import base64
import streamlit as st
import pandas as pd

# 🔹 Define o nome da página e o favicon
st.set_page_config(page_title="Gerador de MDR", page_icon="📄", layout="wide")

# Função para converter imagem local em base64
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Caminho da imagem de fundo
background_image_path = "background.png"  # Substitua pelo nome correto do arquivo

# Converter para base64
base64_bg = get_base64_image(background_image_path)

# Adiciona imagem de fundo usando CSS
st.markdown(
    f"""
    <style>
    .stApp {{
        background: url("data:image/png;base64,{base64_bg}") no-repeat center center fixed;
        background-size: cover;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Exibe a logo no topo esquerdo
st.image("logo.png", width=150)  # Substitua "logo.png" pelo nome do seu arquivo de logo

st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] {
        display: flex;
        align-items: center;
        justify-content: flex-start;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
        /* Remove o header padrão do Streamlit */
        header {visibility: hidden;}

        /* Remove o rodapé padrão do Streamlit */
        footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)


# Título da aplicação
st.title("Gerador de MDR")

# Lista de opções do dropdown
sistema_options = [
    "DLG - Diligenciamento / Expediting", "GEN - General", "SUR - Survey", "FAS - Flow Assurance", 
    "XTE - XT & Tools", "TCS - Topside Control Systems", "SCS - Subsea Control Systems", "FLY - Flying Lead", 
    "HUB - Hubs & Conectors", "UTA - UTA", "PLT - PLET", "PLM - Manifold & PLEM", "ILS - ILS & ILT", 
    "PIG - PIG Launcher Receiver", "CIV - CIMV Valve", "BOO - Boosting System (Pump)", "FLB - Flexible", 
    "RID - Rigid", "UMB - Umbilical", "GIE - Gas Import / Export", "VES - Vessel", "LOG - Logistics", 
    "INS - Installation Item", "ITG - Integrity", "OPS - Operation"
]

# Lista de opções do dropdown para "Campo"
campo_options = ["ABL", "TBMT", "FPA", "POL", "WAH"]

# Campo de seleção fora da tabela
st.subheader("Selecione o Campo")
campo_selecionado = st.selectbox("Campo:", campo_options)

# Campo de texto para "Projeto"
st.subheader("Informe o Projeto")
projeto_nome = st.text_input("Projeto:")

# Lista de novas colunas (checkbox)
checkbox_columns = [
    "MEL - Master Equipment List", 
    "DSGR - Design Report (Especificação Técnica)", 
    "GA - General Arrangement", 
    "CC - Cathodic & Corrosion Report", 
    "FAT - FAT & SIT Procedure", 
    "OMM - Manual de Operação & Manutenção", 
    "PSM - Procedimento de Preservação e Manutenção", 
    "RFAT - Relatório de FAT - SIT", 
    "DTBK - Data Book de Fabricação ou Manutenção", 
    "ASB - Desenhos As-Built de Equipamentos", 
    "RREC - Relatório de Recebimento de Equipamento", 
    "RTR - Reutilization Technical Report", 
    "IPR - Inspection Procedure & Reports", 
    "TESP - Test Procedure", 
    "MTPR - Maintenance Procedure & Reports", 
    "DFIO - Updated DFIO dossier", 
    "UDTB - Updated Databook"
]

# 🔹 Inicializa a tabela no estado da sessão se não existir ainda
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "Pacote": ["Umbilical", "Conectores", "ANM"],
        "Sistema": ["UMB - Umbilical", "HUB - Hubs & Conectors", "PLM - Manifold & PLEM"]
    })
    for col in checkbox_columns:
        st.session_state.df[col] = False

# 🔹 Removendo linhas vazias antes de exibir a tabela
st.session_state.df.dropna(how="all", inplace=True)
st.session_state.df = st.session_state.df[st.session_state.df["Pacote"].str.strip() != ""]

# 🔹 Resetar indexação para evitar criação automática de linhas
st.session_state.df.reset_index(drop=True, inplace=True)

# 🔹 Exibir a tabela editável sem permitir novas linhas vazias
st.subheader("Preencha aqui as informações do MDR")

edited_df = st.data_editor(
    st.session_state.df,
    key="editable_table",
    use_container_width=True,
    height=300,  # 🔹 Define altura para não gerar espaço extra
    hide_index=True,
    num_rows="dynamic",  # 🔹 Agora permite adicionar linha apenas quando necessário!
    column_order=["Pacote", "Sistema"] + [col for col in st.session_state.df.columns if col not in ["Pacote", "Sistema"]],
    column_config={
        "Pacote": st.column_config.Column("Pacote", pinned=True),
        "Sistema": st.column_config.SelectboxColumn("Sistema", options=sistema_options, pinned=True)
    }
)

# 🔹 Botão para salvar alterações sem manter linhas vazias
if st.button("Salvar Alterações", key="save_changes"):
    edited_df.dropna(how="all", inplace=True)  # Remove NaN
    edited_df = edited_df[edited_df["Pacote"].str.strip() != ""]
    edited_df.reset_index(drop=True, inplace=True)  # 🔹 Mantém índice fixo
    st.session_state.df = edited_df
    st.success("Alterações salvas!")
    st.rerun()

# 🔹 Criar colunas lado a lado para "Adicionar Nova Coluna" e "Baixar Tabela"
col1, col2 = st.columns(2)

# 🔹 Seção de Adicionar Nova Coluna
with col1:
    st.subheader("Adicionar Nova Coluna")
    st.write("Sempre salve as suas alterações antes de adicionar uma nova coluna!")
    new_column = st.text_input("Nome da nova coluna:")

    if st.button("Adicionar Coluna", key="add_column"):
        if new_column:
            new_column = new_column.strip()  # Remove espaços extras
            if new_column not in st.session_state.df.columns:
                # 🔹 Salvar a tabela antes de adicionar a nova coluna
                st.session_state.df[new_column] = False  # Adiciona uma nova coluna de checkbox
                st.success(f"Coluna '{new_column}' adicionada!")
                st.rerun()
            else:
                st.warning("Essa coluna já existe!")
        else:
            st.warning("Por favor, insira um nome válido para a coluna.")

# 🔹 Seção de Baixar Tabela
with col2:
    st.subheader("Baixar Tabela")
    
    if st.button("Download Excel"):
        # Criar uma nova estrutura de dados para armazenar os valores transformados
        transformed_data = []

        # Criar um dicionário para rastrear a numeração de cada pacote
        pacote_counter = {}
        pacote_numero = 1  # Começa a contagem dos pacotes

        # Percorrer cada linha da tabela original
        for _, row in st.session_state.df.iterrows():
            pacote = row["Pacote"]

            # Se o pacote for novo, definir um novo número para ele
            if pacote not in pacote_counter:
                pacote_counter[pacote] = pacote_numero
                pacote_numero += 1  # Incrementar para o próximo pacote

            # Para cada coluna de documento, verificar se está marcada como True
            doc_index = 1  # Contador interno para o documento dentro do pacote
            for col in st.session_state.df.columns:
                if col not in ["Pacote", "Sistema"] and row[col] == True:
                    numeracao = f"2.2.{pacote_counter[pacote]}.{doc_index}"  # Formato X.Y
                    transformed_data.append({
                        "Numeração": numeracao,
                        "Pacote": pacote,
                        "Nome do Documento": col,
                        "Data de Finalização": ""
                    })
                    doc_index += 1  # Incrementa a numeração dentro do pacote

        # Criar um novo DataFrame com o formato desejado
        transformed_df = pd.DataFrame(transformed_data)

        if not transformed_df.empty:
            # Criar um buffer para o Excel
            excel_buffer = "MDR_tabela_transformada.xlsx"

            # Criar o arquivo Excel e ajustar as colunas
            with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
                transformed_df.to_excel(writer, index=False, sheet_name="MDR_Transformado")

                # Ajustar largura das colunas
                workbook = writer.book
                worksheet = writer.sheets["MDR_Transformado"]
                worksheet.set_column("A:A", 10)  # Numeração
                worksheet.set_column("B:B", 20)  # Pacote
                worksheet.set_column("C:C", 40)  # Nome do Documento
                worksheet.set_column("D:D", 20)  # Data de Finalização (espaço extra)

            # Botão para baixar o arquivo
            st.download_button(
                label="Clique para baixar",
                data=open(excel_buffer, "rb"),
                file_name="MDR_tabela.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("Nenhum dado marcado para exportação.")
