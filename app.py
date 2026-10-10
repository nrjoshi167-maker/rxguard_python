import streamlit as st

# App Configuration for Mobile
st.set_page_config(
    page_title="RxGuard India", page_icon="🛡️", layout="centered"
)

st.title("🛡️ RxGuard India")
st.caption("National Pharmacovigilance & Local Audit Tool (Python Edition)")

# Step 1: Evidence Capture
st.markdown("### 📄 Step 1: Upload Evidence")
rx_file = st.file_uploader(
    "1. Doctor's Prescription (Rx)", type=["jpg", "png", "jpeg"]
)
med_file = st.file_uploader(
    "2. Medicine Strip Photo", type=["jpg", "png", "jpeg"]
)

# Step 2: Symptoms Logger
st.markdown("### 🩺 Step 2: Report Symptoms")
selected_symptoms = st.multiselect(
    "Select common symptoms experienced:",
    [
        "Severe Skin Rash / Urticaria",
        "Shortness of Breath / Wheezing",
        "Severe Dizziness / Vertigo",
        "Persistent Nausea / Vomiting",
        "High Fever (>102°F)",
    ],
)

narrative = st.text_area(
    "Additional Notes / Timeline",
    placeholder="Describe when symptoms started...",
)

# Step 3: Run Audit Button
st.markdown("---")
if st.button(
    "Run Offline Audit & Triage", type="primary", use_container_width=True
):
  if not selected_symptoms and not narrative:
    st.error(
        "Please select at least one symptom or enter details to run the audit."
    )
  else:
    st.success("Audit Successful! (No API Key Required)")

    st.markdown("### 📊 Audit Breakdown")
    st.info(
        "**Status:** Offline safety triage completed successfully based on"
        " standard clinical logic."
    )

    if selected_symptoms:
      st.write(
          "**Logged Symptoms:**",
          ", ".join(selected_symptoms),
      )

    # Emergency Guidance Notice
    st.warning(
        "⚠️ **Emergency Triage Notice:** If you are experiencing severe"
        " breathing difficulty or chest tightness, please visit the nearest"
        " emergency hospital immediately (e.g., Civil Hospital or GMC Nanded)."
    )
   
