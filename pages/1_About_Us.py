from pathlib import Path

import streamlit as st

from app_auth import require_authentication

st.set_page_config(page_title="Get or Not? — About Us", page_icon="ℹ️")
require_authentication()

REFERENCE_PDF_DIR = Path(__file__).resolve().parent.parent / "reference_docs"
REFERENCE_URLS = {
    "Assurance Package _ Govbenefits.pdf": "https://www.govbenefits.gov.sg/government-benefits-schemes/assurance-package/",
    "Budget 2026 Measures _ Govbenefits.pdf": "https://www.govbenefits.gov.sg/government-benefits-schemes/budget-2026-measures/",
    "GST Voucher _ Govbenefits.pdf": "https://www.govbenefits.gov.sg/government-benefits-schemes/gst-voucher/",
    "Majulah Package _ Govbenefits.pdf": "https://www.govbenefits.gov.sg/government-benefits-schemes/majulah-package/",
}

st.title("Get or Not?")
st.subheader("About this chatbot")
st.write(
    "**Get or Not?** helps users explore government benefits and support schemes available "
    "in Singapore based on information from **govbenefits.gov.sg**."
)

st.subheader("What you can do")
st.markdown(
    "- Describe your age, housing situation, income level, household size, or life stage.\n"
    "- Ask whether you may be eligible for a government benefit or support scheme.\n"
    "- Ask for payment amounts, eligibility criteria, application steps, or important dates.\n"
    "- Compare benefits mentioned in the available reference documents.\n"
    "- Ask follow-up questions in the same conversation."
)

st.subheader("Information we use")
reference_files = sorted(REFERENCE_PDF_DIR.glob("*.pdf"))
if reference_files:
    st.markdown("The chatbot uses the following local reference files:")
    for path in reference_files:
        file_link = f"- `{path.name}`"
        # Add a clickable URL for the reference filenames
        if path.name in REFERENCE_URLS:
            file_link += f" ([source]({REFERENCE_URLS[path.name]}))"
        st.markdown(file_link)
else:
    st.info("No reference PDFs are currently present in `reference_docs/`.")

st.subheader("How to ask a useful question")
st.markdown(
    "Include the details that may affect eligibility, for example:\n\n"
    "- Your age or age range\n"
    "- Residential or citizenship status\n"
    "- Monthly household income\n"
    "- Number of household members\n"
    "- Housing type or employment situation"
)

st.info(
    "Example: \"I am a 68-year-old Singapore Citizen. Which benefits in these documents "
    "might be relevant to me? Please show eligibility criteria and payment amounts.\""
)

st.markdown(
    "**Other prompts to try:**\n"
    "- \"Tell me more about the Budget 2026 measures.\"\n"
    "- \"What is the GST Voucher, and who may be eligible?\"\n"
    "- \"Summarise the main benefits and eligibility criteria in the Majulah Package.\""
)

st.subheader("Important limitations")
st.warning(
    "The chatbot provides information from reference documents for educational purposes only. "
    "It does not guarantee eligibility, make final decisions, or replace official advice. "
    "Eligibility rules, amounts, and application processes may change; verify important details "
    "with the relevant government agency or an official professional."
)

st.info(
    "**Confirm your eligibility:** Log in to the official GovPayouts portal "
    "to check available benefits and confirm eligibility: "
    "[Open GovPayouts](https://www.govpayouts.gov.sg/cds/main/login)"
)
