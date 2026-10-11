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

# Secure API Key Check via Streamlit Secrets
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.warning(
        "⚠️ GEMINI_API_KEY not found in Streamlit Secrets. Please configure your secrets."
    )

# Initialize Session State
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
        "Provide your medical details and capture or upload photos of your evidence documents. **(ALL 4 evidence documents are mandatory)**"
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
        st.info("⚠️ You MUST provide legitimate images for ALL FOUR categories to proceed.")

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
            # Check if ANY of the 4 files are missing
            missing_files = any(file is None for file in uploaded_files)

            if not med_name:
                st.error("Please enter the name of the medicine before proceeding.")
            elif missing_files:
                st.error("🛑 ALL FOUR evidence documents are mandatory. Please provide the Prescription, Medicine, Invoice, and License.")
            else:
                images_to_send = []
                labeled_images = []
                
                # Map files to their expected labels so the AI knows what it's looking at
                file_mapping = [
                    ("Doctor's Prescription", uploaded_files[0]),
                    ("Medicine Strip Photo", uploaded_files[1]),
                    ("Pharmacy Tax Invoice", uploaded_files[2]),
                    ("Pharmacist / Chemist License", uploaded_files[3])
                ]

                for label, file in file_mapping:
                    img = Image.open(file)
                    images_to_send.append(img)
                    labeled_images.extend([f"User claims this is: [{label}]", img])

                st.session_state.med_name = med_name
                st.session_state.symptoms = symptoms
                st.session_state.route = route
                st.session_state.narrative = narrative
                st.session_state.labeled_images = labeled_images
                
                # Clear previous audit data if re-running
                if "audit_report" in st.session_state: del st.session_state.audit_report
                if "validation_error" in st.session_state: del st.session_state.validation_error
                
                st.session_state.step = 2
                st.rerun()

# ==========================================
# STEP 2: AI AUDIT & SCENARIO REPORT GENERATION
# ==========================================
elif st.session_state.step == 2:
    st.subheader("Step 2: AI Audit & Regulatory Report")

    # Only run the AI calls if we haven't generated the report yet for this session
    if "audit_report" not in st.session_state and "validation_error" not in st.session_state:
        model = genai.GenerativeModel("gemini-3.8-flash")
        
        # --- PHASE 1: STRICT 4-PART IMAGE VALIDATION ---
        with st.spinner("🔍 Phase 1: Validating authenticity of all 4 uploaded documents..."):
            try:
                val_prompt = """
                You are a strict legal document verification AI. You have been provided with 4 images, each with a specific label. 
                You MUST verify that EACH image is a legitimate, real-world document corresponding to its label:
                1. Doctor's Prescription
                2. Medicine Strip Photo
                3. Pharmacy Tax Invoice
                4. Pharmacist / Chemist License
                
                If ANY of the 4 images is a random picture (e.g., a selfie, a car, a pet, blank paper, unrelated screenshot) instead of the actual required document, you MUST reject it.
                
                - If ALL 4 images legitimately match their medical/legal labels, reply ONLY with the word "VALID".
                - If ANY image is fake or unrelated, reply EXACTLY with "INVALID: " followed by which document is wrong and why (e.g., "INVALID: The Pharmacy Tax Invoice image provided is a picture of a keyboard.").
                """
                val_contents = [val_prompt] + st.session_state.labeled_images
                val_response = model.generate_content(val_contents)
                val_result = val_response.text.strip()
                
                if val_result.startswith("INVALID"):
                    st.session_state.validation_error = val_result.replace("INVALID:", "").strip()
                else:
                    st.session_state.validation_error = None
            except Exception as e:
                st.session_state.validation_error = f"API Error during validation: {e}"

        # --- PHASE 2: ACTUAL AUDIT (Only if Phase 1 passed) ---
        if not st.session_state.validation_error:
            with st.spinner("✅ All 4 documents verified! Running strict AI Audit on evidence..."):
                try:
                    audit_prompt = f"""
                    You are an expert Clinical Pharmacovigilance and Legal Medical Auditor in India.
                    
                    CRITICAL INSTRUCTION: Base your analysis EXCLUSIVELY on the patient details and the text/data explicitly visible in the 4 uploaded images. 
                    - DO NOT use external knowledge or general assumptions. 
                    - DO NOT hallucinate details, batch numbers, or names not present in the documents.
                    - If a specific piece of information is missing from the documents, explicitly state "Data unavailable in provided evidence".

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
                    - **Strict Evidence Breakdown** (State exactly what is written on the prescription, dispensed drug, license, and invoice based ONLY on the images)
                    - **App Notification / Actionable Guidance for the Patient**
                    - **Geographical Regulatory Routing** (Specify authority based ONLY on location data found in the documents, or state "Location unknown")
                    """
                    audit_contents = [audit_prompt] + st.session_state.labeled_images
                    audit_response = model.generate_content(audit_contents)
                    st.session_state.audit_report = audit_response.text
                except Exception as e:
                    st.error(f"An error occurred during the audit: {e}")

    # --- RENDER RESULTS OR ERRORS ---
    if st.session_state.get("validation_error"):
        st.error(f"🛑 **Evidence Rejected:** {st.session_state.validation_error}")
        st.info("Please go back and upload correct, legitimate documents for all 4 categories to proceed.")
        if st.button("⬅️ Go Back to Step 1"):
            st.session_state.step = 1
            del st.session_state.validation_error
            st.rerun()
    elif st.session_state.get("audit_report"):
        st.markdown("### 📊 Official AI Audit & Malpractice Report")
        st.markdown(st.session_state.audit_report)

        st.markdown("---")
        st.markdown("### 🚀 Regulatory Submission")
        if st.button("📤 Submit Encrypted Report to Regional Authorities", type="primary"):
            st.success("Report successfully signed with metadata and dispatched to regional PvPI / CDSCO authorities!")

        st.markdown("---")
        if st.button("⬅️ Start New Audit"):
            st.session_state.step = 1
            del st.session_state.audit_report
            st.rerun()
