import streamlit as st
import pandas as pd
import json
import glob
import os
from datetime import datetime

st.set_page_config(
    page_title="DOU Monitor Report",
    page_icon="🗞️",
    layout="wide"
)

def load_data(data_dir="data"):
    """
    Loads all JSONL files from the data directory and aggregates them by Article URL.
    Returns:
        list[dict]: List of unique articles with their matches.
    """
    articles_map = {}
    
    # Find all jsonl files
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
                            "title": entry.get("title", "No Title"),
                            "url": url,
                            "date": entry.get("date"),
                            "section": entry.get("section"),
                            "matches": []
                        }
                    
                    # Add match details
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
    st.title("🗞️ DOU Monitor: Daily Report")
    
    # --- Sidebar ---
    st.sidebar.header("Filters")
    
    # Load Data
    if not os.path.exists("data"):
        st.error("Data directory not found. Please run the scraper first.")
        return

    all_articles = load_data()
    
    if not all_articles:
        st.info("No data found.")
        return

    # Convert to DF for easier filtering of metadata
    df_meta = pd.DataFrame([
        {
            "url": a["url"], 
            "date": a["date"], 
            "section": a["section"], 
            "match_count": len(a["matches"])
        } 
        for a in all_articles
    ])
    
    # Filter: Date
    available_dates = sorted(df_meta["date"].unique(), reverse=True)
    selected_date = st.sidebar.selectbox("Select Date", available_dates)
    
    # Filter: Section
    available_sections = sorted(df_meta["section"].unique())
    selected_sections = st.sidebar.multiselect(
        "Select Sections", 
        available_sections, 
        default=available_sections
    )
    
    # Apply Filters
    filtered_articles = [
        a for a in all_articles 
        if a["date"] == selected_date and a["section"] in selected_sections
    ]
    
    # Metrics
    total_articles = len(filtered_articles)
    total_matches = sum(len(a["matches"]) for a in filtered_articles)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Date", selected_date)
    c2.metric("Articles Found", total_articles)
    c3.metric("Total Keyword Matches", total_matches)
    
    st.markdown("---")
    
    # --- Main Content ---
    for article in filtered_articles:
        with st.container():
            # Header with Title and Badges
            col_title, col_badges = st.columns([5, 2])
            
            with col_title:
                st.subheader(article["title"])
                st.markdown(f"[{article['url']}]({article['url']})")
                
            with col_badges:
                st.caption(f"Section: {article['section']}")
                matches_count = len(article['matches'])
                # Using markdown badge equivalent since st.badge might change signatures or not exist in this version
                color = "red" if matches_count > 0 else "grey"
                st.markdown(f":{color}[Matches: {matches_count}]")

            # Expander for Contexts
            with st.expander("View Matches Context"):
                for i, match in enumerate(article["matches"]):
                    st.markdown(f"**Match #{i+1}** - Keyword: `{match['keyword']}`")
                    # Highlight keyword in context (simple bolding)
                    context = match['context']
                    keyword = match['keyword']
                    
                    # Case insensitive replace for highlighting
                    # Note: accurate highlighting can be complex due to regex/normalization
                    # We'll just display the blockquote for now.
                    st.markdown(f"> {context}")
                    st.divider()
                    
            st.divider()

if __name__ == "__main__":
    main()
