# === INTERFACE ===

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from quantile_dotplot import ntile_dotplot

st.set_page_config(layout="wide")
st.title("Digikey App")
st.subheader("Manage Your Inventory With AI to Ride the Next Wave")

st.subheader("\nProduct Search")

df = pd.read_csv('./intermediate_data/Product_Article_Matching.csv')

cat_list = df["Product Category"].unique().tolist()


with st.expander("Search Product"):
    st.subheader("Search a Product Category")
    cat = st.selectbox(
    "How would you like to be contacted?",
    cat_list, placeholder= "Plug Housings")



    if st.button("Search"):
        st.write("The Category Being Searched is:", cat)

    col1, col2 = st.columns(2)

    with col1:
        st.header("Quantile Dot Plot")
        st.image("figures/sfp_{}.png".format(cat.translate(str.maketrans(" /", "__"))))

    with col2:
        st.header("Summary")
        st.text("This is text\n This is where a summary for the product will go.")

df = pd.read_csv('./intermediate_data/Product_Article_Matching.csv')
df['Product_Category'] = df.apply(
    lambda row: f'<a href="{row["Product url"]}" target="_blank">{row["Product Category"]}</a>',
    axis=1
)
df = df.drop(columns=['Product url'])

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
def render_html_table(dataframe):
    html = '''
    <div style="overflow-x: auto; width: 100%;">
        <table border="1" style="border-collapse: collapse; width: max-content; min-width: 100%;">
            <thead><tr>
    '''
    for col in dataframe.columns:
        html += f'<th style="padding: 8px; background-color: #ffffff;">{col}</th>'
    html += '</tr></thead><tbody>'
    for _, row in dataframe.iterrows():
        html += '<tr>'
        for val in row:
            html += f'<td style="padding: 8px;">{val}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    return html

df = df.fillna('')
st.markdown(render_html_table(df), unsafe_allow_html=True)