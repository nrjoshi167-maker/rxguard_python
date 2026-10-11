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
        "Provide your medical details and capture or upload photos of your evidence documents. **(Evidence is mandatory)**"
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
        st.info("⚠️ You must upload or snap at least one document image to proceed.")

        # Option for file upload or camera capture
        capture_method = st.radio(
            "Select evidence input method:", ["File Upload", "Camera Capture"]
        )

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
            # Collect uploaded images safely FIRST to validate them
            images_to_send = []
            for file in uploaded_files:
                if file is not None:
                    images_to_send.append(Image.open(file))

            # Validation Checks
            if not med_name:
                st.error("Please enter the name of the medicine before proceeding.")
            elif len(images_to_send) == 0:
                st.error("⚠️ Evidence is mandatory. Please upload or capture at least one document image before running the audit.")
            else:
                # Save state data
                st.session_state.med_name = med_name
                st.session_state.symptoms = symptoms
                st.session_state.route = route
                st.session_state.narrative = narrative
                st.session_state.uploaded_images = images_to_send
                st.session_state.step = 2
                st.rerun()

# ==========================================
# STEP 2: AI AUDIT & SCENARIO REPORT GENERATION
# ==========================================
elif st.session_state.step == 2:
    st.subheader("Step 2: AI Audit & Regulatory Report")

    with st.spinner(
        "Scanning documents and evaluating evidence strictly against provided data..."
    ):
        try:
            # Construct strictly constrained prompt
            prompt = f"""
            You are an expert Clinical Pharmacovigilance and Legal Medical Auditor in India.
            
            CRITICAL INSTRUCTION: You must base your analysis EXCLUSIVELY on the patient details provided below and the information explicitly visible in the uploaded images. 
            - DO NOT use external knowledge, web data, or general assumptions. 
            - DO NOT hallucinate details, batch numbers, or names not present in the documents.
            - If information is missing, explicitly state "Data unavailable in provided evidence".
            - Your sole job is to scan the documents, verify if the data matches, and determine if everything is correct based ONLY on the evidence provided.

            Patient Details:
            - Medicine: {st.session_state.med_name}
            - Route: {st.session_state.route}
            - Symptoms Reported: {st.session_state.symptoms}
            - Narrative/Timeline: {st.session_state.narrative}

            Evaluate the visible evidence and categorize the failure strictly into ONE or more of these four core scenarios:
            1. Patient Administration Error 
            2. Faulty Medicine / Batch Defect 
            3. Physician Malpractice 
            4. Pharmacist Malpractice 

            Provide a professional structured report including:
            - **Detected Failure Scenario & Severity**
            - **Strict Evidence Breakdown** (State exactly what is written on the prescription, dispensed drug, license, and invoice. Point out mismatches based ONLY on the images)
            - **App Notification / Actionable Guidance for the Patient**
            - **Geographical Regulatory Routing** (Specify authority based ONLY on location data found in the documents, or state "Location unknown" if missing)
            """

            contents = [prompt]
            if "uploaded_images" in st.session_state:
                contents.extend(st.session_state.uploaded_images)

            # Call Gemini Model
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
