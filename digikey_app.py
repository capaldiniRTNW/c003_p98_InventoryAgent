import streamlit as st
import pandas as pd

st.title("Digikey App")
st.write("Manage Your Inventory With AI")

df = pd.read_csv('./intermediate_data/product_article_matches_flat.csv')

st.subheader("Ride the Next Wave")


st.dataframe(df)
