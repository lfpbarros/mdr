import base64
import streamlit as st
import pandas as pd
from io import BytesIO

# ✩ Configurações da página
st.set_page_config(page_title="Gerador de MDR", page_icon="📄", layout="wide")

# ✩ Função para converter imagem em base64
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# ✩ Aplica imagem de fundo
background_image_path = "background.png"
base64_bg = get_base64_image(background_image_path)

st.markdown(f"""
    <style>
    .stApp {{
        background: url("data:image/png;base64,{base64_bg}") no-repeat center center fixed;
        background-size: cover;
    }}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    [data-testid="stSidebarNav"] {{
        display: flex;
        align-items: center;
        justify-content: flex-start;
    }}
    </style>
    """, unsafe_allow_html=True)

# ✩ Exibe logo
st.image("logo.png", width=150)

# ✩ Título da aplicação
st.title("Gerador de MDR")

# ✩ Listas de opções
sistema_options = [
    "DLG - Diligenciamento / Expediting", "GEN - General", "SUR - Survey", "FAS - Flow Assurance",
    "XTE - XT & Tools", "TCS - Topside Control Systems", "SCS - Subsea Control Systems", "FLY - Flying Lead",
    "HUB - Hubs & Conectors", "UTA - UTA", "PLT - PLET", "PLM - Manifold & PLEM", "ILS - ILS & ILT",
    "PIG - PIG Launcher Receiver", "CIV - CIMV Valve", "BOO - Boosting System (Pump)", "FLB - Flexible",
    "RID - Rigid", "UMB - Umbilical", "GIE - Gas Import / Export", "VES - Vessel", "LOG - Logistics",
    "INS - Installation Item", "ITG - Integrity", "OPS - Operation"
]

campo_options = ["ABL", "TBMT", "FPA", "POL", "WAH"]

checkbox_columns = [
    "MEL - Master Equipment List", "DSGR - Design Report (Especificação Técnica)", "GA - General Arrangement",
    "CC - Cathodic & Corrosion Report", "FAT - FAT & SIT Procedure", "OMM - Manual de Operação & Manutenção",
    "PSM - Procedimento de Preservação e Manutenção", "RFAT - Relatório de FAT - SIT",
    "DTBK - Data Book de Fabricação ou Manutenção", "ASB - Desenhos As-Built de Equipamentos",
    "RREC - Relatório de Recebimento de Equipamento", "RTR - Reutilization Technical Report",
    "IPR - Inspection Procedure & Reports", "TESP - Test Procedure", "MTPR - Maintenance Procedure & Reports",
    "DFIO - Updated DFIO dossier", "UDTB - Updated Databook"
]

# ✩ Inputs do usuário
st.subheader("Selecione o Campo")
campo_selecionado = st.selectbox("Campo:", campo_options)

st.subheader("Informe o Projeto")
projeto_nome = st.text_input("Projeto:")

# ✩ Inicializa DataFrame
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "Pacote": ["Umbilical", "Conectores", "ANM"],
        "Sistema": ["UMB - Umbilical", "HUB - Hubs & Conectors", "PLM - Manifold & PLEM"]
    })
    for col in checkbox_columns:
        st.session_state.df[col] = False

st.session_state.df.dropna(how="all", inplace=True)
st.session_state.df = st.session_state.df[st.session_state.df["Pacote"].str.strip() != ""]
st.session_state.df.reset_index(drop=True, inplace=True)

# ✩ Editor de tabela
st.subheader("Preencha aqui as informações do MDR (Master Document Register)")
edited_df = st.data_editor(
    st.session_state.df,
    key="editable_table",
    use_container_width=True,
    height=300,
    hide_index=True,
    num_rows="dynamic",
    column_order=["Pacote", "Sistema"] + [col for col in st.session_state.df.columns if col not in ["Pacote", "Sistema"]],
    column_config={
        "Pacote": st.column_config.Column("Pacote", pinned=True),
        "Sistema": st.column_config.SelectboxColumn("Sistema", options=sistema_options, pinned=True)
    }
)

# ✩ Botão para salvar alterações
if st.button("Salvar Alterações", key="save_changes"):
    edited_df.dropna(how="all", inplace=True)
    edited_df = edited_df[edited_df["Pacote"].str.strip() != ""]
    edited_df.reset_index(drop=True, inplace=True)
    st.session_state.df = edited_df
    st.success("Alterações salvas!")
    st.rerun()

# ✩ Adicionar nova coluna ou baixar
col1, col2 = st.columns(2)

with col1:
    st.subheader("Adicionar Nova Coluna")
    st.write("Sempre salve as suas alterações antes de adicionar uma nova coluna!")
    new_column = st.text_input("Nome da nova coluna:")
    if st.button("Adicionar Coluna", key="add_column"):
        if new_column:
            new_column = new_column.strip()
            if new_column not in st.session_state.df.columns:
                st.session_state.df[new_column] = False
                st.success(f"Coluna '{new_column}' adicionada!")
                st.rerun()
            else:
                st.warning("Essa coluna já existe!")
        else:
            st.warning("Insira um nome válido.")

with col2:
    st.subheader("Baixar Tabela")
    if st.button("Download Excel"):

        # 🔹 Gera inicio_df
        inicio_data = {
            "Numeração": [
                "1", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "1.9",
                "2.1", "2.1.1", "2.1.2", "2.1.3", "2.1.4", "2.1.5", "2.1.6", "2.1.7",
                "2.1.8", "2.1.9", "2.1.10", "2.1.11", "2.1.12", "2.1.13", "2.1.14",
                "2.1.15", "2.1.16", "2.1.17", "2.1.18", "2.1.19"
            ],
            "Pacote": ["" for _ in range(30)],
            "Nome do Documento": [
                "PORTFÓLIO", "BOD - Basis of Design Preliminar", "TAP - Formulário de Análise de Oportunidade",
                "CRONOP - Cronograma Preliminar", "AEM - Análise de Estoque de materiais PRIO", "MPL - Master Project List Preliminar",
                "AFE - Approval for Expenditure", "SUBLAYP - Subsea Layout Preliminar", "BFD - Block Flow Diagram Preliminar",
                "STIME - Cronograma Preliminar de Operação", "PLANEJAMENTO - SYSTEM", "SCH - Project Baseline Schedule",
                "WBS - Work Breakdown Structure", "BoD - Basis of Design", "BFD - Block Flow Diagram",
                "SUBLAY - Subsea Layout", "DBD - Database Design", "SGSS - Checklist de Atendimento ao SGSS",
                "MDR - Master Document Register Re", "HAZID - Project HAZID", "HDS - Overall System Hydraulic Schematic",
                "ELS - Overall System Electrical Schematic", "BATIM - Bathimetry Report", "GEOTEC - Geotechnical Report",
                "SBL - Scope Battery Limit", "FASS - Flow Assurance Report", "HEA - Hydraulical and Electrical Analysis",
                "PRIR - Preliminary Recovery and Installation Requirements", "SCEM - Subsea Cause and Effect Matrix",
                "Material Compatibility Assessment | Material Selection Report"
            ],
            "Data de Finalização": ["" for _ in range(30)]
        }
        inicio_df = pd.DataFrame(inicio_data)

        # 🔹 Gera transformed_df
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

        # 🔹 Cria final_df
        final_data = {
            "Numeração": [
                "3.", "3.1.", "3.2.", "3.3.", "3.4.", "3.5.", "3.6."
            ],
            "Pacote": [""] * 7,
            "Nome do Documento": [
                "FINALIZAÇÃO",
                "FLDLAY - Subsea Layout As Built",
                "BFD - Block Flow Diagram As Built",
                "SGSS - Checklist de Atendimento ao SGSS (Fase de Instalação)",
                "ICUE - Relatório Changelog do iCUE",
                "DPP - Cadastro no DPP da ANP",
                "MPL - Master Project List final de Projeto"
            ],
            "Data de Finalização": [""] * 7
        }
        final_df = pd.DataFrame(final_data)

        # 🔹 Junta tudo: inicio_df + transformed_df + final_df
        df_final = pd.concat([inicio_df, transformed_df, final_df], ignore_index=True)

        # Define o nome da aba, baseado no projeto
        nome_aba = projeto_nome.strip() if projeto_nome.strip() else "MDR_Projeto"

        # Excel não permite mais que 31 caracteres no nome da aba
        if len(nome_aba) > 31:
            nome_aba = nome_aba[:31]

        # Remove caracteres inválidos (Excel não aceita: \ / ? * [ ])
        invalid_chars = ['\\', '/', '?', '*', '[', ']']
        for char in invalid_chars:
            nome_aba = nome_aba.replace(char, '')


        # 🔹 Salva Excel direto na memória
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df_final.to_excel(writer, index=False, sheet_name=nome_aba, startrow=1)

            workbook = writer.book
            worksheet = writer.sheets[nome_aba]

            worksheet.merge_range('A1:D1', projeto_nome, workbook.add_format({
                'font_name': 'Aptos Narrow', 'font_size': 20, 'bold': True,
                'align': 'center', 'valign': 'center', 'font_color': '#FFFFFF',
                'bg_color': '#A6A6A6', 'border': 1
            }))

            header_format = workbook.add_format({
                'bold': True, 'text_wrap': True, 'valign': 'center', 'align': 'center',
                'fg_color': '#61CBF3', 'font_color': '#363636', 'font_name': 'Segoe UI', 'font_size': 12, 'border': 2
            })

            for idx, col in enumerate(df_final.columns):
                # Pega o tamanho máximo de cada coluna
                max_length = max(
                    df_final[col].astype(str).map(len).max(),   # maior valor da coluna
                    len(col)                                    # ou o nome da coluna
                ) + 2  # adiciona uma margem extra para não ficar muito justo

                worksheet.set_column(idx, idx, max_length)  # aplica a largura ajustada
                worksheet.write(1, idx, col, header_format)  # escreve o cabeçalho formatado

            worksheet.freeze_panes(2, 2)
            worksheet.autofilter(1, 0, len(df_final)+1, len(df_final.columns)-1)

        output.seek(0)

        st.download_button(
            label="Clique para baixar o MDR",
            data=output,
            file_name=f"MDR_{projeto_nome}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
