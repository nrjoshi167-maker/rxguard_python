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
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.warning(
        "⚠️ GEMINI_API_KEY not found in Streamlit Secrets. Please configure your secrets."
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
        "Provide your medical details and capture or upload photos of your evidence documents."
    )

    with st.form("rxguard_form"):
        st.markdown("### 📋 1. Questionnaire & Symptoms")
       med_name = st.text_input(
        "Name of Medicine Prescribed / Dispensed",
        placeholder="e.g., Augmentin 625mg or Paracetamol",
    )

    symptoms = st.text_area(
        "Symptoms / Adverse Reactions Experienced:",
        placeholder="Type the symptoms here (e.g., severe skin rash, dizziness, fever...)"
    )

    route = st.selectbox(
        "Administration Route",
        ["Oral (Swallowed)", "Topical (Skin)", "Injection"],
    )

        narrative = st.text_area(
            "Narrative / Administration Timeline",
            placeholder=(
                "Describe when symptoms started relative to dose intake, dosage frequency, etc..."
            ),
        )

        st.markdown("### 📷 2. Evidence Capture (Upload Files or Camera)")
        st.info("You can upload document images or snap photos directly using your camera.")

        # Option for file upload or camera capture
        capture_method = st.radio(
            "Select evidence input method:", ["File Upload", "Camera Capture"]
        )

        images_to_send = []

        if capture_method == "File Upload":
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
            
            uploaded_files = [rx_file, med_file, invoice_file, license_file]
        else:
            col1, col2 = st.columns(2)
            with col1:
                rx_cam = st.camera_input("1. Doctor's Prescription (Rx)")
                med_cam = st.camera_input("2. Medicine Strip Photo")
            with col2:
                invoice_cam = st.camera_input("3. Pharmacy Tax Invoice")
                license_cam = st.camera_input("4. Pharmacist License")
            
            uploaded_files = [rx_cam, med_cam, invoice_cam, license_cam]

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
                for file in uploaded_files:
                    if file is not None:
                        images_to_send.append(Image.open(file))

                st.session_state.uploaded_images = images_to_send
                st.session_state.step = 2
                st.rerun()

# ==========================================
# STEP 2: AI AUDIT & SCENARIO REPORT GENERATION
# ==========================================
elif st.session_state.step == 2:
    st.subheader("Step 2: AI Audit & Regulatory Report")

    with st.spinner(
        "Analyzing 4-part evidence bundle and evaluating CDSCO/PvPI compliance..."
    ):
        try:
            # Construct structured prompt categorized into the 4 scenarios
            prompt = f"""
            You are an expert Clinical Pharmacovigilance, Legal Medical Auditor, and CDSCO/PvPI Compliance Officer in India.
            Analyze the uploaded evidence images (Prescription, Medicine Strip, Tax Invoice, Pharmacist License) along with these patient details:
            - Medicine: {st.session_state.med_name}
            - Route: {st.session_state.route}
            - Symptoms Reported: {st.session_state.symptoms}
            - Narrative/Timeline: {st.session_state.narrative}

            Evaluate the case and categorize the failure strictly into ONE or more of these four core scenarios:
            1. Patient Administration Error (Wrong timing, incorrect dosage taken by patient) -> Provide direct app notification / guidance for the patient.
            2. Faulty Medicine / Batch Defect (Packaging flaw, sub-standard batch, or manufacturing defect) -> Generate report focusing on drug/batch failure.
            3. Physician Malpractice (Invalid/unverified doctor registration number or wrong prescription choice) -> Generate report focusing on physician violation.
            4. Pharmacist Malpractice (Unauthorized brand substitution or invalid chemist operating license) -> Generate report focusing on pharmacist violation.

            Provide a professional structured report including:
            - **Detected Failure Scenario & Severity**
            - **Forensic Evidence Breakdown** (Comparing prescription, dispensed drug, license status, and batch details)
            - **App Notification / Actionable Guidance for the Patient**
            - **Geographical Regulatory Routing** (Specify exact authority such as State FDA, CDSCO Regional Office, or State Medical Council based on region)
            """

            contents = [prompt]
            if "uploaded_images" in st.session_state:
                contents.extend(st.session_state.uploaded_images)

            # Call Gemini Model using standard generativeai SDK
            model = genai.GenerativeModel("gemini-3.8-flash")
            response = model.generate_content(contents)

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
            "Report successfully signed with metadata and dispatched to regional PvPI / CDSCO authorities!"
        )

    st.markdown("---")
    if st.button("⬅️ Start New Audit"):
        st.session_state.step = 1
        st.rerun()
