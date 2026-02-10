import streamlit as st
import pandas as pd
import json
import glob
import os
from datetime import datetime

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

def main():
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
    
    # Filtro: Data
    available_dates = sorted(df_meta["date"].unique(), reverse=True)
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
                # Usando equivalente de emblema markdown pois st.badge pode mudar assinaturas ou não existir nesta versão
                color = "red" if matches_count > 0 else "grey"
                st.markdown(f":{color}[Correspondências: {matches_count}]")

            # Expansor para Contextos
            with st.expander("Ver Contexto das Correspondências"):
                for i, match in enumerate(article["matches"]):
                    st.markdown(f"**Correspondência #{i+1}** - Palavra-chave: `{match['keyword']}`")
                    # Destaca palavra-chave no contexto (negrito simples)
                    context = match['context']
                    keyword = match['keyword']
                    
                    # Substituição insensível a maiúsculas/minúsculas para destaque
                    # Nota: destaque preciso pode ser complexo devido a regex/normalização
                    # Vamos apenas exibir o blockquote por enquanto.
                    st.markdown(f"> {context}")
                    st.divider()
                    
            st.divider()

if __name__ == "__main__":
    main()
