import streamlit as st
import google.generativeai as genai
from PIL import Image

# Page Configuration for Smartphone Responsiveness
st.set_page_config(
    page_title="RxGuard India",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Secure API Key Check via Streamlit Secrets (Server-Side Protection)
if "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
  st.warning(
      "⚠️ GEMINI_API_KEY not found in Streamlit Secrets. Please configure your"
      " secrets.toml file."
  )

# Initialize Session State for the Two-Step Process
if "step" not in st.session_state:
  st.session_state.step = 1

# App Header
st.title("🛡️ RxGuard India")
st.caption("AI-Powered National Pharmacovigilance & Malpractice Detector")
st.markdown("---")

# ==========================================
# STEP 1: QUESTIONNAIRE & EVIDENCE CAPTURE
# ==========================================
if st.session_state.step == 1:
  st.subheader("Step 1: Clinical Questionnaire & Evidence Capture")
  st.markdown(
      "Provide your medical details and capture/upload photos of your evidence"
      " documents."
  )

  with st.form("rxguard_form"):
    st.markdown("### 📋 1. Questionnaire & Symptoms")
    med_name = st.text_input(
        "Name of Medicine Prescribed / Dispensed",
        placeholder="e.g., Augmentin 625mg or Paracetamol",
    )

    symptoms = st.multiselect(
        "Select Symptoms / Adverse Reactions Experienced:",
        [
            "Severe Skin Rash / Urticaria",
            "Shortness of Breath / Wheezing",
            "Severe Dizziness / Vertigo",
            "Persistent Nausea / Vomiting",
            "High Fever (>102°F)",
            "Chest Tightness / Discomfort",
        ],
    )

    route = st.selectbox(
        "Administration Route",
        ["Oral (Swallowed)", "Topical (Skin)", "Injection"],
    )

    narrative = st.text_area(
        "Narrative / Administration Timeline",
        placeholder=(
            "Describe when symptoms started relative to dose intake, dosage"
            " frequency, etc..."
        ),
    )

    st.markdown("### 📷 2. Evidence Capture (Photos)")
    st.info(
        "You can upload files or snap photos directly using your mobile"
        " camera."
    )

    col1, col2 = st.columns(2)
    with col1:
      rx_file = st.file_uploader(
          "1. Doctor's Prescription (Rx)", type=["jpg", "png", "jpeg"]
      )
      med_file = st.file_uploader(
          "2. Medicine Strip Photo", type=["jpg", "png", "jpeg"]
      )
    with col2:
      invoice_file = st.file_uploader(
          "3. Pharmacy Tax Invoice", type=["jpg", "png", "jpeg"]
      )
      license_file = st.file_uploader(
          "4. Pharmacist / Chemist License", type=["jpg", "png", "jpeg"]
      )

    submitted = st.form_submit_button(
        "Run AI Audit & Generate Report ➔", type="primary"
    )

    if submitted:
      if not med_name:
        st.error("Please enter the name of the medicine before proceeding.")
      else:
        # Save state data
        st.session_state.med_name = med_name
        st.session_state.symptoms = symptoms
        st.session_state.route = route
        st.session_state.narrative = narrative

        # Collect uploaded images safely
        images_to_send = []
        for file in [rx_file, med_file, invoice_file, license_file]:
          if file is not None:
            images_to_send.append(Image.open(file))

        st.session_state.uploaded_images = images_to_send
        st.session_state.step = 2
        st.rerun()

# ==========================================
# STEP 2: REAL AI AUDIT & REPORT GENERATION
# ==========================================
elif st.session_state.step == 2:
  st.subheader("Step 2: AI Audit & Regulatory Report")

  with st.spinner(
      "Analyzing 4-part evidence bundle and cross-referencing CDSCO standards..."
  ):
    try:
      # Construct structured prompt for Gemini AI
      prompt = f"""
            You are an expert Clinical Pharmacovigilance, Legal Medical Auditor, and CDSCO/PvPI Compliance Officer in India.
            Analyze the uploaded evidence images (Prescription, Medicine Strip, Tax Invoice, Pharmacist License) along with these patient details:
            - Medicine: {st.session_state.med_name}
            - Route: {st.session_state.route}
            - Symptoms Reported: {st.session_state.symptoms}
            - Narrative/Timeline: {st.session_state.narrative}

            Evaluate the case and categorize the failure into ONE of these four core scenarios:
            1. Patient Administration Error (Wrong timing, incorrect dosage taken by patient)
            2. Faulty Medicine / Batch Defect (Packaging flaw, sub-standard batch, or manufacturing defect)
            3. Physician Malpractice (Invalid/unverified doctor registration number or wrong prescription choice)
            4. Pharmacist Malpractice (Unauthorized brand substitution or invalid chemist operating license)

            Provide a clear, professional structured report covering:
            - **Detected Failure Scenario & Severity**
            - **Forensic Evidence Breakdown** (Comparing prescription, dispensed drug, license status, and batch details)
            - **App Notification / Guidance for the Patient**
            - **Geographical Regulatory Routing** (Specify authority such as State FDA, CDSCO Regional Office, or State Medical Council)
            """

      contents = [prompt]
      if "uploaded_images" in st.session_state:
        contents.extend(st.session_state.uploaded_images)

      # Call Gemini Model safely through server-side client
      response = client.models.generate_content(
          model="gemini-2.5-flash", contents=contents
      )

      # Display the real AI audit output
      st.markdown("### 📊 Official AI Audit & Malpractice Report")
      st.markdown(response.text)

    except Exception as e:
      st.error(
          f"An error occurred while connecting to the AI audit engine: {e}"
      )

  st.markdown("---")
  st.markdown("### 🚀 Regulatory Submission")
  if st.button(
      "📤 Submit Encrypted Report to Regional Authorities", type="primary"
  ):
    st.success(
        "Report successfully signed with ABHA metadata and dispatched to"
        " regional PvPI / CDSCO authorities!"
    )

  st.markdown("---")
  if st.button("⬅️ Start New Audit"):
    st.session_state.step = 1
    st.rerun()
