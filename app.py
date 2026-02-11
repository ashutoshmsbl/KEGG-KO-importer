import streamlit as st
import requests

st.set_page_config(
    page_title="G2KO - Gene to KEGG KO Extractor",
    layout="centered"
)

st.title("G2KO - Gene to KEGG KO Extractor")
st.write("Extract Gene ID, KO Numbers, and KO Functions from KEGG.")

HEADERS = {"User-Agent": "Mozilla/5.0"}

# ------------------------------
# Function to get KO function
# ------------------------------
@st.cache_data
def get_ko_function(ko_id):
    try:
        url = f"https://rest.kegg.jp/get/ko:{ko_id}"
        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code == 200:
            for line in r.text.split("\n"):
                if line.startswith("DEFINITION"):
                    return line.replace("DEFINITION", "").strip()
        return "Function not found"
    except:
        return "Function not found"

# ------------------------------
# User Input
# ------------------------------
num = st.number_input("Number of organisms:", 1, 10, 1)

organisms = []

for i in range(num):
    col1, col2 = st.columns(2)
    with col1:
        code = st.text_input(f"KEGG Code {i+1}", key=f"code{i}")
    with col2:
        name = st.text_input(f"Name (Optional) {i+1}", key=f"name{i}")

    if code:
        if not name:
            name = f"Organism {i+1}"
        organisms.append((code.strip(), name.strip()))

# ------------------------------
# Fetch Button
# ------------------------------
if st.button("Fetch KO Numbers"):

    if not organisms:
        st.error("Please enter at least one KEGG organism code.")
        st.stop()

    output = ""
    progress = st.progress(0)

    for index, (code, name) in enumerate(organisms):

        url = f"https://rest.kegg.jp/link/ko/{code}"

        try:
            response = requests.get(url, headers=HEADERS, timeout=20)

            if response.status_code != 200:
                st.error(f"Invalid KEGG code or blocked request: {code}")
                continue

            output += f"# {name}\n"

            lines = response.text.strip().split("\n")

            for line in lines:
                parts = line.split("\t")
                if len(parts) == 2:
                    gene = parts[0].split(":")[1]
                    ko = parts[1].split(":")[1]
                    function = get_ko_function(ko)
                    output += f"{gene}\t{ko}\t{function}\n"

            output += "\n"

        except Exception as e:
            st.error(f"Error fetching {code}: {e}")

        progress.progress(int(((index + 1) / len(organisms)) * 100))

    st.success("Extraction Complete")
    st.text_area("Output", output, height=300)

    if output:
        st.download_button(
            "Download TXT",
            output,
            file_name="g2ko_output.txt"
        )
