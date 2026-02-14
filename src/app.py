import streamlit as st
import pandas as pd
import json
import glob
import os
from datetime import datetime, date

# Importações locais do projeto
from src import main as main_scrapper
from src.models import Config, AdvancedMatchRule, ScheduleConfig, LoggingConfig, StorageConfig
from src import config

st.set_page_config(
    page_title="Relatório do Monitor DOU",
    page_icon="🗞️",
    layout="wide"
)

def load_data(data_dir="data"):
    """
    Carrega todos os arquivos JSONL do diretório de dados e os agrega por URL do artigo.
    Retorna:
        list[dict]: Lista de artigos únicos com suas correspondências.
    """
    articles_map = {}
    
    # Encontra todos os arquivos jsonl
    files = glob.glob(os.path.join(data_dir, "*.jsonl"))
    
    for file_path in files:
        filename = os.path.basename(file_path)
        keyword_slug = filename.replace(".jsonl", "")
        
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    url = entry.get("url")
                    
                    if not url:
                        continue
                        
                    if url not in articles_map:
                        articles_map[url] = {
                            "title": entry.get("title", "Sem Título"),
                            "url": url,
                            "date": entry.get("date"),
                            "section": entry.get("section"),
                            "matches": []
                        }
                    
                    # Adiciona detalhes da correspondência
                    match_info = {
                        "keyword": entry.get("keyword"),
                        "context": entry.get("context"),
                        "source_file": filename
                    }
                    articles_map[url]["matches"].append(match_info)
                    
                except json.JSONDecodeError:
                    continue
                    
    return list(articles_map.values())

def run_custom_search_view():
    st.title("🔍 Busca Personalizada no DOU")
    
    with st.form("search_form"):
        col1, col2 = st.columns(2)
        with col1:
            search_date = st.date_input("Data da Busca", value=date.today())
        with col2:
            search_sections = st.multiselect("Seções", ["dou1", "dou2", "dou3"], default=["dou3"])
        
        # Advanced Rules inputs
        st.subheader("Critérios de Busca")
        st.info("Preencha pelo menos um campo de termos.")
        
        title_terms_str = st.text_input("Termos no Título (separados por vírgula)")
        body_terms_str = st.text_input("Termos no Corpo (separados por vírgula)")
        
        submitted = st.form_submit_button("Executar Busca")
    
    if submitted:
        if not title_terms_str and not body_terms_str:
            st.error("Por favor adicione termos de busca para Título ou Corpo.")
            return
        
        # Construct Config
        title_terms = [t.strip() for t in title_terms_str.split(",") if t.strip()]
        body_terms = [t.strip() for t in body_terms_str.split(",") if t.strip()]
        
        rule = AdvancedMatchRule(
            name="Busca Manual",
            title_terms=title_terms,
            body_terms=body_terms
        )
        
        # Create a temporary config
        # We use dummy values for logging/schedule as they are not used in search directly
        temp_config = Config(
            schedule=ScheduleConfig(time="00:00"),
            logging=LoggingConfig(),
            storage=StorageConfig(),
            keywords=[], # No simple keywords, using rules
            rules=[rule],
            sections=search_sections
        )
        
        with st.spinner("Executando raspagem... isso pode levar alguns segundos."):
            try:
                matches = main_scrapper.run_scraper(temp_config, search_date)
                
                if not matches:
                    st.warning("Nenhuma correspondência encontrada com os critérios informados.")
                else:
                    # Agrega correspondências por URL para evitar duplicatas visuais
                    unique_articles = {}
                    for match in matches:
                        if match.url not in unique_articles:
                            unique_articles[match.url] = {
                                "title": match.title,
                                "section": match.section,
                                "url": match.url,
                                "contexts": []
                            }
                        unique_articles[match.url]["contexts"].append(match.context)
                    
                    st.success(f"Encontradas {len(matches)} correspondências em {len(unique_articles)} publicações!")

                    # Exibe resultados por artigo único
                    st.divider()
                    for url, article in unique_articles.items():
                        with st.container():
                            st.subheader(f"{article['title']} (Seção {article['section']})")
                            st.markdown(f"[{article['url']}]({article['url']})")
                            
                            with st.expander(f"Ver {len(article['contexts'])} trecho(s) encontrado(s)", expanded=True):
                                for ctx in article['contexts']:
                                    st.markdown(f"> {ctx}")
                                    st.markdown("---")
                            st.divider()
                            
            except Exception as e:
                st.error(f"Erro ao executar a busca: {str(e)}")


def run_daily_report_view():
    st.title("🗞️ Monitor DOU: Relatório Diário")
    
    # --- Barra Lateral ---
    st.sidebar.header("Filtros")
    
    # Carrega Dados
    if not os.path.exists("data"):
        st.error("Diretório de dados não encontrado. Por favor, execute o raspador primeiro.")
        return

    all_articles = load_data()
    
    if not all_articles:
        st.info("Nenhum dado encontrado.")
        return

    # Converte para DF para filtrar metadados mais facilmente
    df_meta = pd.DataFrame([
        {
            "url": a["url"], 
            "date": a["date"], 
            "section": a["section"], 
            "match_count": len(a["matches"])
        } 
        for a in all_articles
    ])
    
    if df_meta.empty:
        st.info("Nenhum dado encontrado nos arquivos.")
        return
    
    # Filtro: Data
    available_dates = sorted(df_meta["date"].unique(), reverse=True)
    if not available_dates:
         st.warning("Sem datas disponíveis.")
         return

    selected_date = st.sidebar.selectbox("Selecionar Data", available_dates)
    
    # Filtro: Seção
    available_sections = sorted(df_meta["section"].unique())
    selected_sections = st.sidebar.multiselect(
        "Selecionar Seções", 
        available_sections, 
        default=available_sections
    )
    
    # Aplica Filtros
    filtered_articles = [
        a for a in all_articles 
        if a["date"] == selected_date and a["section"] in selected_sections
    ]
    
    # Métricas
    total_articles = len(filtered_articles)
    total_matches = sum(len(a["matches"]) for a in filtered_articles)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Data", selected_date)
    c2.metric("Artigos Encontrados", total_articles)
    c3.metric("Total de Correspondências", total_matches)
    
    st.markdown("---")
    
    # --- Conteúdo Principal ---
    for article in filtered_articles:
        with st.container():
            # Cabeçalho com Título e Emblemas
            col_title, col_badges = st.columns([5, 2])
            
            with col_title:
                st.subheader(article["title"])
                st.markdown(f"[{article['url']}]({article['url']})")
                
            with col_badges:
                st.caption(f"Seção: {article['section']}")
                matches_count = len(article['matches'])
                color = "red" if matches_count > 0 else "grey"
                st.markdown(f":{color}[Correspondências: {matches_count}]")

            # Expansor para Contextos
            with st.expander("Ver Contexto das Correspondências"):
                for i, match in enumerate(article["matches"]):
                    st.markdown(f"**Correspondência #{i+1}** - Palavra-chave: `{match['keyword']}`")
                    context = match['context']
                    st.markdown(f"> {context}")
                    st.divider()

def main():
    st.sidebar.title("Navegação")
    # Usa radio ou selectbox para navegação
    page = st.sidebar.radio("Ir para", ["Relatório Diário", "Busca Personalizada"])
    
    if page == "Relatório Diário":
        run_daily_report_view()
    elif page == "Busca Personalizada":
        run_custom_search_view()

if __name__ == "__main__":
    main()

