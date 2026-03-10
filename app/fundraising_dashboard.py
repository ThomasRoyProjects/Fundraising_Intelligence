import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime
from io import BytesIO

st.set_page_config(
    page_title="Fundraising Intelligence Dashboard",
    page_icon="📊",
    layout="wide"
)

LOCAL_CODES = ["local_party", "tickets", "local_event"]
HQ_CODES = ["national_party"]
TICKET_KEYWORDS = ["ticket"]
LEGAL_CAP = 1775

st.title("Fundraising Intelligence Dashboard")
st.caption("All data is processed locally in memory. No files are uploaded, stored, or transmitted externally.")

if "df" not in st.session_state:
    st.session_state.df = None

uploaded_file = st.file_uploader(
    "Upload NationBuilder Transactions CSV",
    type=["csv"],
    accept_multiple_files=False
)

if uploaded_file is not None:
    st.session_state.df = pd.read_csv(uploaded_file, low_memory=False)

df = st.session_state.df

if df is None:
    st.info("Upload a NationBuilder transactions CSV to begin.")
    st.stop()

df = df.copy()

if st.button("Clear Data"):
    st.session_state.df = None
    st.rerun()

def to_csv_download(df):
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer


df.columns = [col.strip() for col in df.columns]

# ---------- standardization ----------
column_map = {
    "email": "signup_email",
    "email_address": "signup_email",
    "e-mail": "signup_email",
    "name": "signup_full_name",
    "full_name": "signup_full_name",
    "donor_name": "signup_full_name",
    "phone": "signup_phone_number",
    "phone_number": "signup_phone_number",
    "mobile": "signup_phone_number",
    "mobile_number": "signup_phone_number",
    "date": "succeeded_at",
    "transaction_date": "succeeded_at",
    "donation_date": "succeeded_at",
    "donation_amount": "amount",
    "amount_paid": "amount",
    "total": "amount",
}

lower_cols = {col.lower(): col for col in df.columns}

for generic, standard in column_map.items():
    if generic in lower_cols and standard not in df.columns:
        df.rename(columns={lower_cols[generic]: standard}, inplace=True)

# ---------- column check (formatting) ----------
if "succeeded_at" not in df.columns:
    st.error("Missing required date column.")
    st.stop()

if "amount" not in df.columns and "amount_in_cents" not in df.columns:
    st.error("Missing required amount column.")
    st.stop()

# ---------- normalize ----------
for col in ["signup_email", "tracking_code_slug", "page_slug"]:
    if col in df.columns:
        df[col] = (
            df[col].astype(str)
            .fillna("")
            .replace("nan", "")
            .str.strip()
            .str.lower()
        )

phone_priority = [
    "signup_phone_number",
    "signup_work_phone_number",
    "signup_phone",
    "mobile_number",
    "phone_number",
    "phone"
]

phone_column = None
for col in phone_priority:
    if col in df.columns:
        phone_column = col
        break

if phone_column:
    df["phone_clean"] = (
        df[phone_column]
        .astype(str)
        .fillna("")
        .replace("nan", "")
        .str.strip()
    )
else:
    df["phone_clean"] = ""

name_cols = [
    "signup_full_name",
    "signup_first_name",
    "signup_middle_name",
    "signup_last_name"
]

for col in name_cols:
    if col in df.columns:
        df[col] = (
            df[col].astype(str)
            .fillna("")
            .replace("nan", "")
            .str.strip()
        )

df["succeeded_at"] = pd.to_datetime(
    df["succeeded_at"],
    format="%m/%d/%Y %I:%M %p",
    errors="coerce"
)

df = df[df["succeeded_at"].notna()].copy()

if "amount" in df.columns:
    df["amount_clean"] = (
        df["amount"]
        .astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
    )
    df["amount_clean"] = pd.to_numeric(df["amount_clean"], errors="coerce").fillna(0)
else:
    df["amount_clean"] = (
        pd.to_numeric(df["amount_in_cents"], errors="coerce").fillna(0) / 100
    )

df["year"] = df["succeeded_at"].dt.year
df["month"] = df["succeeded_at"].dt.month
current_year = datetime.now().year

# ---------- IDs ----------
if "signup_nationbuilder_id" in df.columns:
    df["person_id"] = df["signup_nationbuilder_id"].astype(str).fillna("").str.strip()
else:
    df["person_id"] = ""

df["person_id"] = np.where(
    (df["person_id"] == "") | (df["person_id"].isna()),
    df.get("signup_email", ""),
    df["person_id"]
)

df["person_id"] = np.where(
    (df["person_id"] == "") | (df["person_id"].isna()),
    df.get("signup_full_name", ""),
    df["person_id"]
)

# ---------- resolve names ----------
def resolve_name(row):
    if row.get("signup_full_name"):
        return row["signup_full_name"]
    if row.get("signup_first_name") and row.get("signup_last_name"):
        return f"{row['signup_first_name']} {row['signup_last_name']}"
    if row.get("signup_email"):
        return row["signup_email"]
    return "Unidentified Donor"

df["best_name"] = df.apply(resolve_name, axis=1)

df["is_ticket"] = df["tracking_code_slug"].str.contains("ticket", na=False)

def classify(row):
    tracking = row.get("tracking_code_slug", "")
    page = row.get("page_slug", "")

    if tracking in HQ_CODES:
        return "HQ"
    if row["is_ticket"]:
        return "TICKETS"
    if tracking in LOCAL_CODES:
        return "LOCAL"
    if "local" in page and ("donate" in page or "event" in page):
        return "LOCAL"
    return "OTHER"

df["source_type"] = df.apply(classify, axis=1)

# ---------- donor aggregate ----------
donor = (
    df.groupby("person_id", as_index=False)
    .agg(
        Name=("best_name", "first"),
        Email=("signup_email", "first"),
        Phone=("phone_clean", "first"),
        Total_Donated_All=("amount_clean", "sum"),
        Donation_Count=("amount_clean", "count"),
        Last_Gift=("succeeded_at", "max")
    )
)

local_by_person = df[df["source_type"] == "LOCAL"].groupby("person_id")["amount_clean"].sum()
hq_by_person = df[df["source_type"] == "HQ"].groupby("person_id")["amount_clean"].sum()
ticket_by_person = df[df["source_type"] == "TICKETS"].groupby("person_id")["amount_clean"].sum()

donor["Local_Total"] = donor["person_id"].map(local_by_person).fillna(0)
donor["HQ_Total"] = donor["person_id"].map(hq_by_person).fillna(0)
donor["Ticket_Total"] = donor["person_id"].map(ticket_by_person).fillna(0)

# ---------- yearly cap ----------
local_this_year = df[(df["year"] == current_year) & (df["source_type"] == "LOCAL")].groupby("person_id")["amount_clean"].sum()
hq_this_year = df[(df["year"] == current_year) & (df["source_type"] == "HQ")].groupby("person_id")["amount_clean"].sum()

donor["Local_Total_This_Year"] = donor["person_id"].map(local_this_year).fillna(0)
donor["HQ_Total_This_Year"] = donor["person_id"].map(hq_this_year).fillna(0)

donor["Cap_Eligible_This_Year"] = donor["Local_Total_This_Year"] + donor["HQ_Total_This_Year"]
donor["Remaining_Cap"] = (LEGAL_CAP - donor["Cap_Eligible_This_Year"]).clip(lower=0)

# ---------- scoring ----------
donor["Local_Loyalty_%"] = np.where(
    donor["Total_Donated_All"] > 0,
    (donor["Local_Total"] / donor["Total_Donated_All"]) * 100,
    0
)

today = pd.Timestamp.today()
donor["Days_Since_Last_Gift"] = (today - donor["Last_Gift"]).dt.days.fillna(9999)
donor["Recency_Score"] = np.clip(100 - (donor["Days_Since_Last_Gift"] / 10), 0, 100)
donor["Frequency_Score"] = np.clip(donor["Donation_Count"] * 5, 0, 100)

donor["Local_Conversion_Score"] = np.where(
    donor["Total_Donated_All"] > 0,
    (donor["Local_Total"] / (donor["Total_Donated_All"] + 1)) * 100,
    0
)

donor["Propensity_to_Local_%"] = (
    donor["Local_Conversion_Score"] * 0.6 +
    donor["Recency_Score"] * 0.25 +
    donor["Frequency_Score"] * 0.15
).clip(0, 100).round(1)

total_raised = df["amount_clean"].sum()
total_local = df[df["source_type"] == "LOCAL"]["amount_clean"].sum()
total_hq = df[df["source_type"] == "HQ"]["amount_clean"].sum()
total_tickets = df[df["source_type"] == "TICKETS"]["amount_clean"].sum()

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("Total Raised", f"${total_raised:,.0f}")
k2.metric("Local Revenue", f"${total_local:,.0f}")
k3.metric("HQ Revenue", f"${total_hq:,.0f}")
k4.metric("Ticket Revenue", f"${total_tickets:,.0f}")
k5.metric("Unique Donors Identified", f"{donor.shape[0]:,}")

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Executive Overview",
    "Revenue Breakdown",
    "Donor Intelligence",
    "Conversion Targeting",
    "Data Audit",
    "Monthly National Donors",
    "$400+ Relationship List"
])

#Overview
with tab1:
    st.subheader("Revenue Mix (Executive View)")
    mix_df = df.groupby("source_type")["amount_clean"].sum().reset_index()

    st.markdown("#### Revenue by Source Type")
    chart_df = mix_df.set_index("source_type")["amount_clean"]
    st.bar_chart(chart_df, width="stretch")

    st.dataframe(mix_df, width="stretch")


#Rev breakdown
with tab2:
    st.subheader("Top Tracking Codes by Revenue (Ranked)")

    tracking_rank = (
        df.groupby("tracking_code_slug")["amount_clean"]
        .sum()
        .reset_index()
        .sort_values("amount_clean", ascending=False)
        .head(20)
    )

    st.markdown("#### Top Revenue Sources (Bar Chart)")
    chart_df = tracking_rank.set_index("tracking_code_slug")["amount_clean"]
    st.bar_chart(chart_df, width="stretch")

    st.dataframe(tracking_rank, width="stretch")


#Donor support
with tab3:
    st.subheader("Who These Donors Actually Support (Local vs HQ Behaviour)")
    st.caption(
        "This section groups donors by real behaviour: Local Party loyal, HQ-only (conversion targets), "
        "mixed donors, and event-only supporters. Use this to decide who to call, thank, or convert."
    )

    def classify_donor_type(row):
        if row["HQ_Total"] > 0 and row["Local_Total"] == 0:
            return "National Party only — Conversion Target"
        elif row["Local_Total"] > 0 and row["HQ_Total"] == 0:
            return "Local Party Only — Core Base"
        elif row["Local_Total"] > 0 and row["HQ_Total"] > 0:
            return "Mixed Donor — Persuadable"
        elif row["Ticket_Total"] > 0 and row["Total_Donated_All"] == row["Ticket_Total"]:
            return "Event-Only Supporter"
        else:
            return "Other / Low Data"

    donor["Donor_Type"] = donor.apply(classify_donor_type, axis=1)

    st.markdown("### Donor Base Composition (People)")

    type_counts = donor["Donor_Type"].value_counts().reset_index()
    type_counts.columns = ["Donor Type", "Number of Donors"]

    chart_df = type_counts.set_index("Donor Type")["Number of Donors"]
    st.bar_chart(chart_df, width="stretch")
    st.dataframe(type_counts, width="stretch")

    st.markdown("### Revenue by Donor Type")

    type_revenue = (
        donor.groupby("Donor_Type")["Total_Donated_All"]
        .sum()
        .sort_values(ascending=True)
        .reset_index()
    )

    revenue_chart_df = type_revenue.set_index("Donor_Type")["Total_Donated_All"]
    st.bar_chart(revenue_chart_df, width="stretch")

    st.dataframe(
        type_revenue.sort_values("Total_Donated_All", ascending=False),
        width="stretch"
    )

    st.markdown("### Top Loyal Donors (Core Base)")

    core_base_donors = donor[
        donor["Donor_Type"] == "Local Party Only — Core Base"
    ].sort_values("Local_Total", ascending=False).head(100)

    st.dataframe(core_base_donors, width="stretch")

    csv_buffer = to_csv_download(core_base_donors)
    st.download_button(
        label="Download Loyal Donors CSV",
        data=csv_buffer,
        file_name="loyal_donors.csv",
        mime="text/csv",
        width="stretch"
    )

    st.markdown("### Mixed Donors")

    mixed_donors = donor[
        donor["Donor_Type"] == "Mixed Donor — Persuadable"
    ].sort_values("Total_Donated_All", ascending=False)

    st.dataframe(mixed_donors, width="stretch")

    csv_buffer = to_csv_download(mixed_donors)
    st.download_button(
        label="Download Mixed Donors CSV",
        data=csv_buffer,
        file_name="mixed_donors.csv",
        mime="text/csv",
        width="stretch"
    )


#Conversion Targeting
with tab4:
    st.subheader("Conversion Targeting — Strategic Priority Targets")

    st.markdown("### High-Propensity National Party Donors")

    hq_conversion_targets = donor[
        (donor["HQ_Total"] > 0) &
        (donor["Local_Total"] == 0)
    ].sort_values(
        ["Propensity_to_Local_%", "HQ_Total"],
        ascending=[False, False]
    )

    st.dataframe(hq_conversion_targets, width="stretch")

    csv_buffer = to_csv_download(hq_conversion_targets)
    st.download_button(
        label="Download HQ High Propensity CSV",
        data=csv_buffer,
        file_name="hq_conversion_targets.csv",
        mime="text/csv",
        width="stretch"
    )


#Data Audit
with tab5:
    st.subheader("Data Audit — Tracking Codes")

    audit = (
        df.groupby(["tracking_code_slug", "source_type"])
        .agg(
            Transactions=("amount_clean", "count"),
            Total_Raised=("amount_clean", "sum")
        )
        .reset_index()
        .sort_values("Total_Raised", ascending=False)
    )

    st.dataframe(audit, width="stretch")

    csv_buffer = to_csv_download(audit)
    st.download_button(
        label="Download Data Audit CSV",
        data=csv_buffer,
        file_name="data_audit.csv",
        mime="text/csv",
        width="stretch"
    )


#Recurring monthly national donors
with tab6:
    st.subheader("Monthly National Donors — Recurring Detection")

    hq_df = df[df["source_type"] == "HQ"].copy()

    if not hq_df.empty:

        hq_df["month_period"] = hq_df["succeeded_at"].dt.to_period("M")

        monthly_pattern = (
            hq_df.groupby(["person_id", "month_period"])["amount_clean"]
            .sum()
            .reset_index()
        )

        monthly_freq = monthly_pattern.groupby("person_id")["month_period"].nunique()

        donor["HQ_Months_Active"] = donor["person_id"].map(monthly_freq).fillna(0)

        monthly_hq = donor[
            (donor["HQ_Total"] > 0) &
            (donor["HQ_Months_Active"] >= 2)
        ]

        st.dataframe(monthly_hq, width="stretch")

        csv_buffer = to_csv_download(monthly_hq)
        st.download_button(
            label="Download Monthly National Donors CSV",
            data=csv_buffer,
            file_name="monthly_national_donors.csv",
            mime="text/csv",
            width="stretch"
        )


#400+ Relationship donor
with tab7:
    st.subheader("Donors $400+ (Relationship List)")

    local_df = df[df["source_type"] == "LOCAL"].copy()

    yearly_local = (
        local_df.groupby(["person_id", "year"])["amount_clean"]
        .sum()
        .reset_index()
    )

    yearly_400 = yearly_local[yearly_local["amount_clean"] >= 400]

    coffee_list = donor.merge(
        yearly_400,
        on="person_id",
        how="inner"
    )

    st.dataframe(coffee_list, width="stretch")

    csv_buffer = to_csv_download(coffee_list)
    st.download_button(
        label="Download $400+ Donors CSV",
        data=csv_buffer,
        file_name="400_plus_donors.csv",
        mime="text/csv",
        width="stretch"
    )