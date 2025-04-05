print("✅ generate_contract.py is being read!")

from docxtpl import DocxTemplate
from datetime import datetime
import os

from models import db
from models.provider import Provider

# Standard Imaging Rates (replace or load from DB as needed)
IMAGING_RATES = {
    "Basic_MRI": 300,
    "MRI_w_": 400,
    "MRI_w__wo": 450,
    "Basic_CT": 200,
    "CT_w": 275,
    "CT_w__wo": 350,
    "X_RAY": 25,
    "Arthrograms": 570
}

# Create Exhibit A table as subdoc
def build_exhibit_table(doc, states, rates):
    subdoc = doc.new_subdoc()
    table = subdoc.add_table(rows=1, cols=3)
    table.style = "Table Grid"

    # Header
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "State"
    hdr_cells[1].text = "Procedure"
    hdr_cells[2].text = "Rate ($)"

    for state in states:
        for procedure, rate in rates.items():
            row_cells = table.add_row().cells
            row_cells[0].text = state
            row_cells[1].text = procedure.replace("_", " ")
            row_cells[2].text = f"${rate:.2f}"

    return subdoc

def generate_contract(provider_id):
    provider = Provider.query.get(provider_id)
    if not provider:
        raise ValueError("Provider not found")

    # Split state list - handle None case
    if provider.states_in_contract:
        states = [s.strip() for s in provider.states_in_contract.split(",") if s.strip()]
    else:
        states = ["CA"]  # Default to California if no states specified

    # Determine rates
    if provider.rate_type == "wcfs" and provider.wcfs_percentage:
        rates = {code: round(rate * (provider.wcfs_percentage / 100), 2) for code, rate in IMAGING_RATES.items()}
    else:
        rates = IMAGING_RATES

    # Load template
    template_path = "templates/contracts/contract_imaging.docx"
    doc = DocxTemplate(template_path)

    # Build Exhibit A table
    exhibit_a_table = build_exhibit_table(doc, states, rates)

    # Create a dictionary with all provider attributes for the template
    provider_dict = {
        "name": provider.name,
        "dba_name": provider.dba_name or "",
        "address": provider.address or "",
        "provider_type": provider.provider_type or "",
        "npi": provider.npi or "",
        "specialty": provider.specialty or "",
        "rate_type": provider.rate_type or "standard",
        "wcfs_percentage": provider.wcfs_percentage or 0
    }

    context = {
        "provider": provider_dict,
        "rates": rates,
        "states": states,
        "exhibit_a": exhibit_a_table,
        "date": datetime.now().strftime("%B %d, %Y")
    }

    doc.render(context)

    # Output paths
    output_folder = "contracts"
    os.makedirs(output_folder, exist_ok=True)
    docx_path = os.path.join(output_folder, f"contract_{provider_id}.docx")
    pdf_path = docx_path.replace(".docx", ".pdf")

    # Save DOCX
    doc.save(docx_path)

    # Convert to PDF (optional)
    try:
        from docx2pdf import convert
        convert(docx_path, pdf_path)
    except Exception as e:
        print(f"[WARN] PDF conversion failed: {e}")

    return docx_path, pdf_path
