
# Fundraising Intelligence

<p align="center"> <img src="docs/dashboard_preview.png" width="900"> </p>

A local analytics dashboard for **NationBuilder transaction exports** used by political campaigns and EDAs.

It analyzes donation history to identify donor behaviour, revenue sources, and outreach targets.

All processing happens locally — no data is uploaded or stored.

----------

# What It Does

Given a NationBuilder transactions export, the dashboard can:

-   Break down revenue by source (local, national, events)
    
-   Identify **core local donors**
    
-   Identify **national donors who may convert locally**
    
-   Detect **recurring national donors**
    
-   Generate **call lists and outreach targets**
    
-   Track **annual donation limits**
    

Results can be exported to CSV for campaign use.

----------

# Quick Start

Clone the repo:

git clone https://github.com/ThomasRoyProjects/Fundraising_Intelligence  
cd Fundraising_Intelligence

Generate demo data:

python app/generate_demo_data.py

Run the dashboard:

streamlit run app/fundraising_dashboard.py

Upload the generated CSV to explore the dashboard.

----------

# Desktop Build

To build the desktop version:

npm install  
npm run dump  
npm run dist

The compiled app will appear in:

dist/

----------

# Demo Data

If you don't have a NationBuilder export, generate sample data:

python app/generate_demo_data.py

This creates:

app/fake_nationbuilder_transactions.csv

You can upload this file into the dashboard.

----------

# Data Privacy

All analysis runs locally.

The application:

-   does not upload donor data
    
-   does not store files
    
-   does not connect to external services
    

CSV files are processed entirely in memory.

----------

# Project Structure

app/  
 fundraising_dashboard.py  
 generate_demo_data.py  
 requirements.txt  
  
docs/  
 dashboard_preview.png

----------

# Future Improvements

-   UI improvements
    
-   direct NationBuilder API integration
    
-   additional CRM import formats
    

----------

# Disclaimer

This tool assists campaigns in analyzing fundraising data.  
Users remain responsible for ensuring compliance with campaign finance laws.