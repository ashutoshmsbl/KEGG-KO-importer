import streamlit as st
import requests

# -------------------------------------------------
# Page Configuration
# -------------------------------------------------
st.set_page_config(
    page_title="G2KO - Gene to KEGG KO Extractor",
    layout="centered"
)

# -------------------------------------------------
# Styling
# -------------------------------------------------
st.markdown(
    """
    <style>
    .stTextInput>div>div>input {
        background-color: #f5f5f5 !important;
        border-radius: 8px !important;
        font-size: 16px !important;
    }
    .kegg-link {
        margin-top: 20px;
        padding: 12px;
        background-color: #eef7ff;
        border-radius: 8px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------
# Title
# -------------------------------------------------
st.title("G2KO - Gene to KEGG KO Extractor")
st.markdown("Extract **Gene ID, KO Numbers, and KO Function Descriptions** from KEGG.")

# -------------------------------------------------
# Headers for KEGG requests
# -------------------------------------------------
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# -------------------------------------------------
# Cache KO Function Database (HTTPS + Headers)
# -------------------------------------------------
@st.cache_data(show_spinner=False)
def load_ko_functions():
    try:
        response = requests.get(
            "https://rest.kegg.jp/list/ko",
            headers=HEADERS,
            timeout=25
        )
        response.raise_for_status()

        ko_dict = {}
        for line in response.text.strip().split("\n"):
            parts = line.split("\t")
            if len(parts) >= 2:
                ko_id = parts[0].split(":")[-1]
                ko_desc = parts[1]
                ko_dict[ko_id] = ko_desc

        return ko_dict

    except requests.exceptions.RequestException as e:
        return {}

ko_function_dict = load_ko_functions()

# -------------------------------------------------
# User Input
# -------------------------------------------------
num_organisms = st.number_input(
    "Enter Number of Organisms:",
    min_value=1,
    max_value=10,
    value=1
)

organisms = []

for i in range(num_organisms):
    col1, col2 = st.columns(2)

    with col1:
        code = st.text_input(
            f"Enter KEGG Organism Code {i+1}:",
            key=f"code_{i}"
        ).strip()

    with col2:
        name = st.text_input(
            f"Enter Name for Organism {i+1} (Optional):",
            key=f"name_{i}"
        ).strip()

    if code:
        if not name:
            name = f"Organism {i+1}"
        organisms.append((code, name))

# -------------------------------------------------
# Fetch Data
# -------------------------------------------------
if st.button("Fetch KO Numbers"):

    if not organisms:
        st.error("Please enter at least one valid KEGG organism code.")
    else:
        progress_bar = st.progress(0)
        output = ""
        total = len(organisms)

        for index, (org_code, org_name) in enumerate(organisms):

            url = f"https://rest.kegg.jp/link/ko/{org_code}"

            try:
                response = requests.get(
                    url,
                    headers=HEADERS,
                    timeout=20
                )
                response.raise_for_status()

                output += f"# {org_name}\n"

                lines = response.text.strip().split("\n")

                for line in lines:
                    parts = line.split("\t")
                    if len(parts) == 2:
                        gene_id = parts[0].split(":")[-1]
                        ko_id = parts[1].split(":")[-1]
                        ko_function = ko_function_dict.get(
                            ko_id,
                            "Function not found"
                        )

                        output += f"{gene_id}\t{ko_id}\t{ko_function}\n"

                output += "\n"

            except requests.exceptions.RequestException as e:
                st.error(f"Error fetching data for {org_name}: {e}")

            progress = int(((index + 1) / total) * 100)
            progress_bar.progress(progress)

        progress_bar.progress(100)
        st.success("Data extraction complete ✅")

        st.text_area(
            "Extracted KO Data",
            output,
            height=350
        )

        if output:
            st.download_button(
                label="Download KO Data as TXT",
                data=output,
                file_name="g2ko_output.txt",
                mime="text/plain"
            )

            st.markdown(
                """
                <div class="kegg-link">
                ➡️ After downloading your file, open  
                <a href="https://www.genome.jp/kegg/mapper/reconstruct.html" 
                   target="_blank">
                   KEGG Reconstruct Pathway Mapper
                </a>  
                (Opens in new tab)
                </div>
                """,
                unsafe_allow_html=True,
            )

# -------------------------------------------------
# Reset Tool
# -------------------------------------------------
if st.button("Reset Tool"):
    st.experimental_rerun()
