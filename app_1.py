import streamlit as st
import requests

# Title and description
st.title("KEGG KO Extractor")
st.markdown("Extract gene IDs and KO numbers for KEGG organisms.")

# Input: Number of organisms
num_organisms = st.number_input("Enter Number of Organisms:", min_value=1, max_value=10, value=1)

# Collect organism codes
organism_codes = []
for i in range(num_organisms):
    code = st.text_input(f"Enter KEGG Organism Code {i+1}:")
    if code:
        organism_codes.append(code.strip())

# Fetch and process data when the button is clicked
if st.button("Fetch KO Numbers"):
    st.info("Fetching data... Please wait.")  # Processing message
    output = ""

    for org in organism_codes:
        url = f"http://rest.kegg.jp/link/ko/{org}"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            # Format Output
            output += f"# {org} (Organism Name as per KEGG)\n"  # Header
            lines = response.text.strip().split("\n")

            for line in lines:
                parts = line.split("\t")
                if len(parts) == 2:
                    gene_id = parts[0].split(":")[-1]  # Remove 'eco:' prefix
                    ko_number = parts[1].split(":")[-1]  # Remove 'ko:' prefix
                    output += f"{gene_id}\t{ko_number}\n"

            output += "\n"

        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching data for {org}: {e}")

    # Display Output in a text area
    st.text_area("Extracted KO Data", output, height=300)

    # Save as TXT file option
    if output:
        st.download_button(
            label="Save as TXT File",
            data=output,
            file_name="kegg_ko_numbers.txt",
            mime="text/plain"
        )

# Exit Button (To Reset the UI)
if st.button("Exit"):
    st.experimental_rerun()
