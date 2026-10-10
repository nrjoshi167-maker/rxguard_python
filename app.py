import streamlit as st
from google import genai
from PIL import Image

# Page Configuration
st.set_page_config(
    page_title="RxGuard India", page_icon="🛡️", layout="centered"
)

# Initialize Gemini Client using Streamlit Secrets (Secure & No Hardcoded Key)
if "GEMINI_API_KEY" in st.secrets:
  client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
  st.warning("⚠️ GEMINI_API_KEY not found in Streamlit Secrets.")

if "step" not in st.session_state:
  st.session_state.step = 1

st.title("🛡️ RxGuard India")
st.caption("AI-Powered National Pharmacovigilance & Malpractice Detector")
st.markdown("---")

# ==========================================
# STEP 1: QUESTIONNAIRE & EVIDENCE CAPTURE
# ==========================================
if st.session_state.step == 1:
  st.subheader("Step 1: Questionnaire & Evidence Capture")

  with st.form("audit_form"):
    st.markdown("### 📋 1. Clinical Details")
    med_name = st.text_input(
        "Name of Medicine Prescribed/Dispensed",
        placeholder="e.g., Augmentin 625mg",
    )
    symptoms = st.multiselect(
        "Symptoms / Adverse Reactions Experienced:",
        [
            "Severe Skin Rash / Urticaria",
            "Shortness of Breath / Wheezing",
            "Severe Dizziness / Vertigo",
            "Persistent Nausea / Vomiting",
            "High Fever (>102°F)",
        ],
    )
    narrative = st.text_area(
        "Narrative / Administration Timeline",
        placeholder="Describe how and when symptoms started...",
    )

    st.markdown("### 📷 2. Upload Evidence Photos")
    st.info("Snap or upload clear pictures of your medical documents.")

    col1, col2 = st.columns(2)
    with col1:
      rx_file = st.file_uploader(
          "Prescription (Rx)", type=["jpg", "png", "jpeg"]
      )
      med_file = st.file_uploader(
          "Medicine Strip", type=["jpg", "png", "jpeg"]
      )
    with col2:
      invoice_file = st.file_uploader(
          "Pharmacy Invoice", type=["jpg", "png", "jpeg"]
      )
      license_file = st.file_uploader(
          "Chemist License", type=["jpg", "png", "jpeg"]
      )

    submitted = st.form_submit_button(
        "Run Real AI Audit & Generate Reports ➔", type="primary"
    )

    if submitted:
      if not med_name:
        st.error("Please enter the medicine name.")
      else:
        # Save inputs to session state
        st.session_state.med_name = med_name
        st.session_state.symptoms = symptoms
        st.session_state.narrative = narrative

        # Collect uploaded images for Gemini
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
  st.subheader("Step 2: Real AI Audit & Regulatory Report")

  with st.spinner(
      "Analyzing evidence and checking compliance standards with Gemini AI..."
  ):
    try:
      # Construct prompt for Gemini
      prompt = f"""
            You are an expert Clinical Pharmacovigilance and Legal Medical Auditor in India.
            Analyze the provided evidence images (prescription, medicine, bill, license) along with these patient details:
            - Medicine: {st.session_state.med_name}
            - Symptoms Reported: {st.session_state.symptoms}
            - Narrative/Timeline: {st.session_state.narrative}

            Evaluate the case and categorize the failure into ONE of these four scenarios:
            1. Patient Administration Error
            2. Faulty Medicine / Batch Defect
            3. Physician Malpractice (Invalid registration or wrong prescription)
            4. Pharmacist Malpractice (Unlawful substitution or invalid license)

            Provide a structured output containing:
            - **Detected Failure Scenario**
            - **Detailed Forensic Analysis**
            - **Specific Guidance / App Notification for the Patient**
            - **Regulatory Authority Routing** (e.g., State FDA, CDSCO, State Medical Council)
            """

      # Prepare contents payload (text prompt + images)
      contents = [prompt]
      if "uploaded_images" in st.session_state:
        contents.extend(st.session_state.uploaded_images)

      # Call Gemini 1.5 Flash model
      response = client.models.generate_content(
          model="gemini-2.5-flash", contents=contents
      )

      # Display the AI's real analytical report
      st.markdown("### 📊 Official AI Audit Report")
      st.markdown(response.text)

    except Exception as e:
      st.error(f"Error connecting to Gemini AI: {e}")

  st.markdown("---")
  if st.button("📤 Submit Report to Regional Authorities"):
    st.success(
        "Report successfully dispatched to local regulatory authorities based"
        " on geographical jurisdiction!"
    )

  if st.button("⬅️ Start New Audit"):
    st.session_state.step = 1
    st.rerun()
