import base64
import streamlit as st
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

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
st.subheader("Preencha aqui as informações do MDR (Master Document Register)")

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

header_info = {
    "Numeração": [
            ["1"],
            ["1.1"],
            ["1.2"],
            ["1.3"],
            ["1.4"],
            ["1.5"],
            ["1.6"],
            ["1.7"],
            ["1.8"],
            ["1.9"],
            ["2.1"],
            ["2.1.1"],
            ["2.1.2"],
            ["2.1.3"],
            ["2.1.4"],
            ["2.1.5"],
            ["2.1.6"],
            ["2.1.7"],
            ["2.1.8"],
            ["2.1.9"],
            ["2.1.10"],
            ["2.1.11"],
            ["2.1.12"],
            ["2.1.13"],
            ["2.1.14"],
            ["2.1.15"],
            ["2.1.16"],
            ["2.1.17"],
            ["2.1.18"],
            ["2.1.19"],
        ],
    "Pacote": [],
    "Nome do Documento": [
            ["PORTFÓLIO"],
            ["BOD - Basis of Design Preliminar"],
            ["TAP - Formulário de Análise de Oportunidade"],
            ["CRONOP - Cronograma Preliminar"],
            ["AEM - Análise de Estoque de materiais PRIO"],
            ["MPL - Master Project List Preliminar"],
            ["AFE - Approval for Expenditure"],
            ["SUBLAYP - Subsea Layout Preliminar"],
            ["BFD - Block Flow Diagram Preliminar"],
            ["STIME - Cronograma Preliminar de Operação (Subsea Time)"],
            ["PLANEJAMENTO - SYSTEM"],
            ["SCH - Project Baseline Schedule"],
            ["WBS - Work Breakdown Structure"],
            ["BoD - Basis of Design"],
            ["BFD - Block Flow Diagram"],
            ["SUBLAY - Subsea Layout"],
            ["DBD - Database Design"],
            ["SGSS - Checklist de Atendimento ao SGSS"],
            ["MDR - Master Document Register Re"],
            ["HAZID - Project HAZID"],
            ["HDS - Overall System Hydraulic Schematic"],
            ["ELS - Overall System Electrical Schematic"],
            ["BATIM - Bathimetry Report"],
            ["GEOTEC - Geotechnical Report"],
            ["SBL - Scope Battery Limit"],
            ["FASS - Flow Assurance Report"],
            ["HEA - Hydraulical and Electrical Analysis"],
            ["PRIR - Preliminary Recovery and Installation Requirements"],
            ["SCEM - Subsea Cause and Effect Matrix"],
            ["Material Compatibility Assessment | Material Selection Report"],
        ],
        "Data de Finalização": []}

footer_info = {
    "Numeração": [
        "3.",
        "3.1.",
        "3.2.",
        "3.3.",
        "3.4.",
        "3.5.",
        "3.6."
    ],
    "Pacote": [
        "",
        "",
        "",
        "",
        "",
        "",
        ""
    ],
    "Nome do Documento": [
        "FINALIZAÇÃO",
        "FLDLAY - Subsea Layout As Built",
        "BFD - Block Flow Diagram As Built",
        "SGSS - Checklist de Atendimento ao SGSS (Fase de Instalação)",
        "ICUE - Relatório Changelog do iCUE",
        "DPP - Cadastro no DPP da ANP",
        "MPL - Master Project List final de Projeto"
    ],
    "Data de Finalização": [
        "",
        "",
        "",
        "",
        "",
        "",
        ""
    ],
}

# 🔹 Seção de Baixar Tabela
with col2:
    st.subheader("Baixar Tabela")
    
    import openpyxl

    if st.button("Download Excel"):
        transformed_data = []
        pacote_counter = {}
        pacote_numero = 1

        for _, row in st.session_state.df.iterrows():
            pacote = row["Pacote"]
            if pacote not in pacote_counter:
                pacote_counter[pacote] = pacote_numero
                pacote_numero += 1
            doc_index = 1
            for col in st.session_state.df.columns:
                if col not in ["Pacote", "Sistema"] and row[col] == True:
                    numeracao = f"2.2.{pacote_counter[pacote]}.{doc_index}"
                    transformed_data.append({
                        "Numeração": numeracao,
                        "Pacote": pacote,
                        "Nome do Documento": col,
                        "Data de Finalização": ""
                    })
                    doc_index += 1

        transformed_df = pd.DataFrame(transformed_data)

        # 🔹 Corrigir "header_info" removendo listas aninhadas
        for key, value in header_info.items():
            header_info[key] = [item[0] if isinstance(item, list) else item for item in value]

        # 🔹 Ajustar tamanho das listas dentro do dicionário "header_info"
        max_length = max(len(v) for v in header_info.values())  # Obtém o tamanho máximo das listas

        for key in header_info.keys():
            while len(header_info[key]) < max_length:
                header_info[key].append("")  # Preenche as listas menores com valores vazios

        # 🔹 Criar DataFrames para "Header Info" e "Footer Info"
        header_info_df = pd.DataFrame(header_info)
        footer_info_df = pd.DataFrame(footer_info)

        # 🔹 Adicionar colunas vazias ao header_info_df caso não tenha as mesmas colunas do transformed_df
        for col in transformed_df.columns:
            if col not in header_info_df.columns:
                header_info_df[col] = ""

        # 🔹 Adicionar colunas vazias ao transformed_df caso não tenha as mesmas colunas do header_info_df
        for col in header_info_df.columns:
            if col not in transformed_df.columns:
                transformed_df[col] = ""

        # 🔹 Adicionar colunas vazias ao footer_info_df caso não tenha as mesmas colunas do transformed_df
        for col in transformed_df.columns:
            if col not in footer_info_df.columns:
                footer_info_df[col] = ""

        # 🔹 Unir os DataFrames (header_info + transformed_data + footer_info)
        final_df = pd.concat([header_info_df, transformed_df, footer_info_df], ignore_index=True)

        # 🔹 Exportar para Excel
        excel_buffer = "MDR_tabela_transformada.xlsx"
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            final_df.to_excel(writer, sheet_name="MDR_Transformado", index=False, startrow=4)  # Deixa espaço para Campo e Projeto

            # 🔹 Ajustar o workbook para adicionar informações antes da tabela
            workbook = writer.book
            worksheet = writer.sheets["MDR_Transformado"]

            # 🔹 Adicionar informações de "Campo" e "Projeto" antes da tabela
            worksheet["A1"] = "Campo:"
            worksheet["B1"] = campo_selecionado
            worksheet["A2"] = "Projeto:"
            worksheet["B2"] = projeto_nome

            # 🔹 Ajustar largura das colunas automaticamente
            for col_idx, col in enumerate(final_df.columns, 1):  # Começa do índice 1 porque no Excel as colunas começam em 'A'
                max_length = max(final_df[col].astype(str).apply(len).max(), len(col)) + 5  # Ajusta para acomodar título e dados
                worksheet.column_dimensions[openpyxl.utils.get_column_letter(col_idx)].width = max_length

        # 🔹 Botão de download
        st.download_button(
            label="Clique para baixar",
            data=open(excel_buffer, "rb"),
            file_name="MDR_tabela.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )