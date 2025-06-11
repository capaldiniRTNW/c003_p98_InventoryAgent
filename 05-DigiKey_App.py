# === INTERFACE ===

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time
from quantile_dotplot import ntile_dotplot
from sandbox_openai import search_product_category
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Inventory Dashboard",
    page_icon="assets/logo.ico",  # .ico, .png, .jpg all work
    layout="wide"
)

st.image("assets/digikey_big_logo.png", width=300)


#st.title("Digikey App")
st.subheader("Manage Your Inventory With AI to Ride the Next Wave")

st.subheader("\nProduct Search")

df = pd.read_csv('./intermediate_data/Product_Article_Matching.csv')

cat_list = df["Product Category"].unique().tolist()

with st.expander("Search Product"):
    #st.subheader("Search a Product Category")
    cat = st.selectbox(" ",
    cat_list, placeholder= "Plug Housings")

    if st.button("Search"):
        st.write("The Category Being Searched is:", cat)

    col1, col2 = st.columns(2)

    with col1:
        st.header("Quantile Dot Plot")
        st.image("figures/sfp_{}.png".format(cat.translate(str.maketrans(" /", "__"))))
 
    with col2:
        st.header("Summary")
        spinner_container = st.empty()
        with spinner_container:
            _, center_col, _ = st.columns([1, 2, 1])
            with center_col:
                with st.spinner("Generating insights...", show_time=False):
                    result = search_product_category(cat)
        
        spinner_container.empty()
        st.write(result)


      

df = pd.read_csv('./intermediate_data/Product_Article_Matching.csv')

df['Product Category'] = df.apply(
    lambda row: f'<a href="{row["Product url"]}" target="_blank">{row["Product Category"]}</a>',
    axis=1
)
df = df.drop(columns=['Product url'])
# df = df.drop(columns=['Description'])

for i in range(1, 4):  # Adjust range if you have more than 3 articles
    title_col = f'Article_{i}_Title'
    link_col = f'Article_{i}_Link'
    if title_col in df.columns and link_col in df.columns:
        df[title_col] = df.apply(
            lambda row: f'<a href="{row[link_col]}" target="_blank">{row[title_col]}</a>' 
            if pd.notna(row[link_col]) and pd.notna(row[title_col]) else '',
            axis=1
        )
        df = df.drop(columns=[link_col])

# Product Search
st.subheader("\nProduct Table")

# Create HTML table
# Create HTML table with expandable description
def render_html_table(dataframe):
    html = '''
    <style>
        .toggle-box { cursor: pointer; color: blue; text-decoration: underline; }
        .full-text { display: none; }
        .desc-cell { max-width: 400px; }
    </style>
    <script>
        function toggleDesc(id) {
            var short = document.getElementById("short_" + id);
            var full = document.getElementById("full_" + id);
            var link = document.getElementById("link_" + id);
            if (full.style.display === "none") {
                full.style.display = "inline";
                short.style.display = "none";
                link.innerText = "See less";
            } else {
                full.style.display = "none";
                short.style.display = "inline";
                link.innerText = "See more";
            }
        }
    </script>
    <div style="overflow-x: auto; width: 100%;">
        <table border="1" style="border-collapse: collapse; width: max-content; min-width: 100%;">
            <thead><tr>
    '''

    for col in dataframe.columns:
        html += f'<th style="padding: 8px; background-color: #f2f2f2;">{col}</th>'
    html += '</tr></thead><tbody>'

    for idx, row in dataframe.iterrows():
        html += '<tr>'
        for col, val in zip(dataframe.columns, row):
            if col == "Description" and isinstance(val, str) and len(val) > 60:
                short = val[:60].strip() + "..."
                full = val
                html += f'''
                <td class="desc-cell" style="padding: 8px;">
                    <span id="short_{idx}">{short}</span>
                    <span id="full_{idx}" class="full-text">{full}</span>
                    <span id="link_{idx}" class="toggle-box" onclick="toggleDesc({idx})">See more</span>
                </td>
                '''
            else:
                html += f'<td style="padding: 8px;">{val}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    return html




df = df.fillna('')
components.html(render_html_table(df), height=600, scrolling=True)


