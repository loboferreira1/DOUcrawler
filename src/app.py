import streamlit as st
import pandas as pd
import json
import glob
import os
from datetime import datetime, date
import logging
from typing import List

# Local project imports
from src import main as main_scrapper
from src.models import Config, AdvancedMatchRule, ScheduleConfig, LoggingConfig, StorageConfig, MatchEntry

# Configure logging for Streamlit
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Monitor DOU - Dashboard",
    page_icon="🗞️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better readability
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A; 
        text-align: center;
        margin-bottom: 2rem;
    }
    .card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 5px solid #2563EB;
    }
    .match-highlight {
        background-color: #FEF3C7;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-weight: bold;
        color: #92400E;
    }
    .metadata {
        font-size: 0.9em;
        color: #6B7280;
        margin-bottom: 0.5rem;
    }
    .context-box {
        font-family: monospace; 
        font-size: 0.95em; 
        background-color: #f8f9fa; 
        padding: 12px; 
        border-radius: 5px;
        border: 1px solid #E5E7EB;
        white-space: pre-wrap;
    }
    a {
        text-decoration: none;
        color: #2563EB;
    }
    a:hover {
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

def load_data(data_dir="data"):
    """
    Loads all JSONL files from the data directory and aggregates them.
    Returns:
        pd.DataFrame: DataFrame containing all unique matches.
    """
    all_matches = []
    
    # Find all jsonl files
    files = glob.glob(os.path.join(data_dir, "*.jsonl"))
    
    for file_path in files:
        filename = os.path.basename(file_path)
        keyword_group = filename.replace(".jsonl", "")
        
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    entry["source_file"] = filename
                    entry["keyword_group"] = keyword_group
                    all_matches.append(entry)
                except json.JSONDecodeError:
                    continue
                    
    if not all_matches:
        return pd.DataFrame()
        
    df = pd.DataFrame(all_matches)
    # Convert date string to datetime objects for sorting
    if "date" in df.columns:
        # Some dates might be DD/MM/YYYY or YYYY-MM-DD depending on source, let's try to normalize
        # Assuming ISO format from matcher.py (date.isoformat())
        df["date_obj"] = pd.to_datetime(df["date"], errors='coerce').dt.date
        df = df.sort_values(by=["date_obj", "section"], ascending=[False, True])
    
    return df

def render_match_card(row):
    """Renders a single match as a card."""
    with st.container():
        st.markdown(f"""
        <div class="card">
            <h4><a href="{row['url']}" target="_blank">{row.get('title', 'Sem Título')} 🔗</a></h4>
            <div class="metadata">
                📅 <strong>Data:</strong> {row.get('date')} &nbsp;|&nbsp; 
                📑 <strong>Seção:</strong> {str(row.get('section', 'N/A')).upper()} &nbsp;|&nbsp; 
                🔑 <strong>Termo:</strong> <span class="match-highlight">{row.get('keyword')}</span>
            </div>
            <div class="context-box">...{row.get('context', '').strip()}...</div>
        </div>
        """, unsafe_allow_html=True)

def run_daily_report_view():
    st.markdown('<h1 class="main-header">📅 Relatório Diário</h1>', unsafe_allow_html=True)
    
    if not os.path.exists("data"):
        st.info("📭 Nenhum dado encontrado. A pasta 'data' ainda não existe.")
        return

    df = load_data()
    
    if df.empty:
        st.info("📭 Nenhum dado encontrado nos arquivos JSONL.")
        return

    # Sidebar Filters
    st.sidebar.header("Filtros")
    
    all_dates = sorted([str(d) for d in df['date'].unique()], reverse=True) if 'date' in df.columns else []
    all_keywords = sorted(df['keyword_group'].unique()) if 'keyword_group' in df.columns else []
    
    selected_date = st.sidebar.selectbox("Filtrar por Data", ["Todas"] + list(all_dates))
    selected_keywords = st.sidebar.multiselect("Filtrar por Grupo de Termo", all_keywords)
    
    # Apply filters
    filtered_df = df.copy()
    if selected_date != "Todas":
        filtered_df = filtered_df[filtered_df['date'] == selected_date]
    if selected_keywords:
        filtered_df = filtered_df[filtered_df['keyword_group'].isin(selected_keywords)]
    
    # Display metrics
    c1, c2 = st.columns(2)
    c1.metric("Total de Ocorrências", len(filtered_df))
    c2.metric("Artigos Únicos", filtered_df['url'].nunique() if not filtered_df.empty else 0)
    
    st.markdown("---")
    
    if filtered_df.empty:
        st.warning("Nenhum resultado para os filtros selecionados.")
    else:
        # Group by date for cleaner display
        dates = filtered_df['date'].unique()
        for d in dates:
            st.subheader(f"🗓️ {d}")
            date_df = filtered_df[filtered_df['date'] == d]
            for _, row in date_df.iterrows():
                render_match_card(row)

def run_custom_search_view():
    st.markdown('<h1 class="main-header">🔍 Busca Personalizada</h1>', unsafe_allow_html=True)
    st.markdown("Execute uma busca em tempo real no DOU. **Os resultados não são salvos.**")

    with st.form("custom_search_form"):
        col1, col2 = st.columns(2)
        with col1:
            search_date = st.date_input("Data da Edição", value=date.today())
        with col2:
            search_sections = st.multiselect(
                "Seções do DOU", 
                ["dou1", "dou2", "dou3", "dou1e", "dou2e", "dou3e"], 
                default=["dou1", "dou2", "dou3"]
            )
        
        st.write("---")
        st.subheader("Critérios de Busca")
        st.caption("Preencha pelo menos um dos campos abaixo (termos separados por vírgula).")

        title_input = st.text_input(
            "Termos no Título", 
            placeholder="Ex: PORTARIA, DECRETO",
            help="Busca termos específicos apenas no título do artigo."
        )

        body_input = st.text_area(
            "Termos no Corpo do Texto", 
            placeholder="Ex: licitação, contratação, nomeação",
            help="Busca termos no conteúdo completo do artigo."
        )
        
        submitted = st.form_submit_button("🚀 Executar Busca", type="primary")
    
    if submitted:
        title_terms = [t.strip() for t in title_input.split(",") if t.strip()]
        body_terms = [t.strip() for t in body_input.split(",") if t.strip()]

        if not title_terms and not body_terms:
            st.error("⚠️ Por favor, insira pelo menos um termo de busca (Título ou Corpo).")
            return
            
        if not search_sections:
            st.error("⚠️ Selecione pelo menos uma seção.")
            return

        # Create a rule for this search
        search_rule = AdvancedMatchRule(
            name="Busca Personalizada",
            title_terms=title_terms,
            body_terms=body_terms
        )
        
        # Create temporary config using the rule
        # The scraper will use this rule to match content
        temp_config = Config(
            schedule=ScheduleConfig(time="00:00"), # Dummy
            keywords=[], # Empty, we use rules
            storage=StorageConfig(output_dir="temp_data"), # Dummy
            logging=LoggingConfig(level="INFO"),
            sections=search_sections,
            rules=[search_rule]
        )
        
        with st.spinner(f"Buscando em {len(search_sections)} seções de {search_date}..."):
            try:
                # Call scraper with save_results=False
                # Note: main.run_scraper returns List[MatchEntry]
                results = main_scrapper.run_scraper(temp_config, search_date, save_results=False)
                
                if results:
                    # Count unique documents
                    unique_docs = set(m.url for m in results)
                    st.success(f"✅ Encontradas {len(results)} ocorrências em {len(unique_docs)} documentos!")
                    
                    # Convert match objects to dicts for display compatibility with render_match_card
                    results_data = []
                    for match in results:
                        results_data.append({
                            "title": match.title,
                            "url": match.url,
                            "date": match.date,
                            "section": match.section,
                            "keyword": match.keyword,
                            "context": match.context
                        })
                    
                    results_df = pd.DataFrame(results_data)
                    
                    for _, row in results_df.iterrows():
                        render_match_card(row)
                else:
                    st.warning("📭 Nenhuma ocorrência encontrada para os critérios informados.")
                    
            except Exception as e:
                st.error(f"❌ Erro durante a busca: {str(e)}")
                # Log exception to console/file
                logger.error(f"Custom search failed: {e}", exc_info=True)

def main():
    st.sidebar.title("App Navigation")
    
    # Stylish sidebar navigation
    page = st.sidebar.radio(
        "Selecione o Módulo", 
        ["Relatório Diário", "Busca Personalizada"],
        index=0
    )
    
    if page == "Relatório Diário":
        run_daily_report_view()
    else:
        run_custom_search_view()
        
    st.sidebar.markdown("---")
    st.sidebar.info(
        "**Monitor DOU v1.0**\n\n"
        "Ferramenta para monitoramento diário do Diário Oficial da União.\n"
    )

if __name__ == "__main__":
    main()

