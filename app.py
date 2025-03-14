import streamlit as st
import requests
import time

# Set page layout and styling
st.set_page_config(page_title="G2KO - Gene to KEGG KO Extractor", layout="centered")

# Custom CSS for styling input boxes
st.markdown(
    """
    <style>
    .stTextInput>div>div>input {
        background-color: #f5f5f5 !important;  /* Light grey input box */
        border-radius: 8px !important;
        font-size: 16px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title and description
st.title("KEGG KO Extractor")
st.markdown("Extract **Gene ID, KO Numbers, and KO Function Descriptions** from KEGG.")

# Input: Number of organisms
num_organisms = st.number_input("Enter Number of Organisms:", min_value=1, max_value=10, value=1)

# Collect organism codes and user-defined names
organisms = []
for i in range(num_organisms):
    col1, col2 = st.columns(2)  # Side-by-side input fields
    with col1:
        code = st.text_input(f"Enter KEGG Organism Code {i+1}:").strip()
    with col2:
        name = st.text_input(f"Enter Name for Organism {i+1}:").strip()

    if code and name:
        organisms.append((code, name))

# Fetch KO functions (to store and use later)
try:
    ko_function_response = requests.get("http://rest.kegg.jp/list/ko", timeout=15)
    ko_function_response.raise_for_status()

    # Store KO function descriptions in a dictionary
    ko_function_dict = {}
    for line in ko_function_response.text.strip().split("\n"):
        parts = line.split("\t")
        ko_id = parts[0].split(":")[-1]  # Remove 'ko:' prefix
        ko_desc = parts[1] if len(parts) > 1 else "Unknown function"
        ko_function_dict[ko_id] = ko_desc

except requests.exceptions.RequestException as e:
    st.error(f"Error fetching KO functions: {e}")
    ko_function_dict = {}

# Fetch and process data when the button is clicked
if st.button("Fetch KO Numbers"):
    st.info("Fetching gene-to-KO mapping...")  # Initial message
    progress_bar = st.progress(0)  # Initialize progress bar
    output = ""

    total_organisms = len(organisms)
    
    for index, (org_code, org_name) in enumerate(organisms):
        url = f"http://rest.kegg.jp/link/ko/{org_code}"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            # Format Output
            output += f"# {org_name}\n"  # Use user-provided organism name
            lines = response.text.strip().split("\n")

            for line in lines:
                parts = line.split("\t")
                if len(parts) == 2:
                    gene_code = parts[0].split(":")[-1]  # Extract only Gene ID
                    ko_number = parts[1].split(":")[-1]  # Remove 'ko:' prefix
                    ko_function = ko_function_dict.get(ko_number, "Function not found")
                    output += f"{gene_code}\t{ko_number}\t{ko_function}\n"

            output += "\n"

        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching data for {org_name}: {e}")

        # Update progress bar
        progress = int(((index + 1) / total_organisms) * 100)
        progress_bar.progress(progress)
        time.sleep(0.5)  # Simulating delay for smooth transition

    # Display Output in a text area
    progress_bar.progress(100)  # Ensure it reaches 100%
    st.success("Data extraction complete! ✅")
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
