import streamlit as st
import random
import requests
from fpdf import FPDF
import base64

# Set up Streamlit page
st.set_page_config(page_title="AI Expansion Toolkit", layout="centered")

# ====== Helper Functions ======
def get_country_info(country_name):
    url = f"https://restcountries.com/v3.1/name/{country_name}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()[0]
        return {
            "official_name": data["name"]["official"],
            "capital": data["capital"][0],
            "region": data["region"],
            "languages": list(data["languages"].values()),
            "population": data["population"]
        }
    else:
        return {"error": f"Could not retrieve data for {country_name}"}

def get_gdp_per_capita(country_code):
    url = f"http://api.worldbank.org/v2/country/{country_code}/indicator/NY.GDP.PCAP.CD?format=json&per_page=1&date=2022"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if len(data) > 1 and data[1] and data[1][0]["value"]:
            return round(data[1][0]["value"], 2)
    return None

def generate_pdf_report(data):
    class ExpansionReportPDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 14)
            self.cell(0, 10, "AI Expansion Toolkit Report", 0, 1, "C")
            self.ln(10)
        def footer(self):
            self.set_y(-15)
            self.set_font("Arial", "I", 8)
            self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")
        def add_report_section(self, title, content):
            self.set_font("Arial", "B", 12)
            self.cell(0, 10, title, 0, 1)
            self.set_font("Arial", "", 11)
            self.multi_cell(0, 10, content)
            self.ln(5)

    pdf = ExpansionReportPDF()
    pdf.add_page()
    for key, value in data.items():
        pdf.add_report_section(key, str(value))
    return pdf.output(dest='S').encode('latin-1')

# Country code map for World Bank API
country_code_map = {
    "Germany": "DE",
    "India": "IN",
    "Japan": "JP",
    "Brazil": "BR",
    "Canada": "CA"
}

# ====== Streamlit UI ======
st.title("AI Expansion Toolkit for Global Automotive Markets")
st.markdown("Helping automotive companies explore international expansion with AI-powered insights.")

# Inputs
st.subheader("Enter Expansion Parameters")
vehicle_type = st.text_input("Vehicle Type (e.g., electric SUV, compact sedan)")
target_country = st.selectbox("Target Country", list(country_code_map.keys()))
business_goal = st.selectbox("Expansion Goal", ["Launch Sales", "Establish Service Network", "Build Supply Chain", "Open Manufacturing Plant"])

# Generate report
if st.button("Generate Expansion Report"):
    with st.spinner("Analyzing international market data..."):
        st.subheader("🌐 Expansion Summary")

        # Country Info
        country_info = get_country_info(target_country)
        if "error" not in country_info:
            st.write("**📊 Country Overview:**")
            st.write(f"- Official Name: {country_info['official_name']}")
            st.write(f"- Capital: {country_info['capital']}")
            st.write(f"- Region: {country_info['region']}")
            st.write(f"- Languages: {', '.join(country_info['languages'])}")
            st.write(f"- Population: {country_info['population']:,}")
        else:
            st.warning(country_info["error"])

        # GDP
        wb_code = country_code_map.get(target_country)
        gdp = get_gdp_per_capita(wb_code) if wb_code else None
        if gdp:
            st.write(f"**💰 GDP per Capita (2022):** ${gdp:,}")
        else:
            st.warning("Could not retrieve GDP data.")

        # Market Fit
        fit_score = random.randint(60, 95)
        st.metric(label="Market Fit Score", value=f"{fit_score}/100")

        # Regulations
        regulations = f"{target_country} requires localized emission testing and homologation for all {vehicle_type} imports."
        st.write("**Regulatory Overview:**")
        st.success(regulations)

        # Cultural Insights
        if target_country == "Japan":
            culture = "Consumers value compact design, advanced tech, and efficiency."
        elif target_country == "Germany":
            culture = "Engineering quality and performance are critical."
        elif target_country == "India":
            culture = "Focus on affordability, road durability, and low-maintenance EVs."
        else:
            culture = f"Customize for local preferences in {target_country}."
        st.write("**Cultural & Localization Tips:**")
        st.info(culture)

        # Strategy Tip
        strategy_tip = "Partner with local distributors or infrastructure companies."
        st.write("**Strategic Recommendation:**")
        st.warning(strategy_tip)

        # PDF Export
        st.markdown("---")
        st.subheader("📄 Download PDF Report")
        report_data = {
            "Vehicle Type": vehicle_type,
            "Target Country": target_country,
            "Business Goal": business_goal,
            "Official Country Name": country_info.get('official_name', 'N/A'),
            "Capital": country_info.get('capital', 'N/A'),
            "Region": country_info.get('region', 'N/A'),
            "Languages": ', '.join(country_info.get('languages', [])),
            "Population": f"{country_info.get('population', 0):,}",
            "GDP per Capita": f"${gdp:,}" if gdp else "N/A",
            "Market Fit Score": f"{fit_score}/100",
            "Regulatory Overview": regulations,
            "Cultural Insights": culture,
            "Strategic Tip": strategy_tip
        }
        pdf_bytes = generate_pdf_report(report_data)
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="expansion_report.pdf">📥 Click here to download your report</a>'
        st.markdown(href, unsafe_allow_html=True)
