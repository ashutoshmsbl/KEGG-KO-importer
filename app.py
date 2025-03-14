import streamlit as st
import requests

st.title("KEGG KO Extractor")
st.markdown("Extract gene ID and KO numbers for KEGG organisms.")

num_organisms = st.number_input("Enter Number of Organisms:", min_value=1, max_value=10, value=1)

organism_codes = []
for i in range(num_organisms):
    code = st.text_input(f"Organism {i+1} KEGG Code:")
    if code:
        organism_codes.append(code)

if st.button("Fetch Data"):
    output = ""
    for org in organism_codes:
        url = f"http://rest.kegg.jp/link/ko/{org}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            output += f"### {org} KO Numbers\n"
            output += response.text + "\n\n"
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching {org}: {e}")

    st.text_area("Results", output, height=300)
