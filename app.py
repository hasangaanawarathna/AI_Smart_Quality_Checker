
import streamlit as st

st.set_page_config(
    page_title="AI Smart Quality Checker",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 AI Smart Quality Checker")
st.caption("Innodata AI Hackathon 2026")

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select Page",
    ["Dashboard", "Quality Checker", "Reports"]
)

if page == "Dashboard":
    st.header("Dashboard")
    st.success("System is running successfully!")

    col1, col2, col3 = st.columns(3)
    col1.metric("Documents Checked", 0)
    col2.metric("Errors Detected", 0)
    col3.metric("Pending Reviews", 0)

elif page == "Quality Checker":
    st.header("Document Quality Checker")

    document = st.file_uploader(
        "Upload a document",
        type=["pdf", "jpg", "jpeg", "png"]
    )

    invoice = st.text_input("Invoice Number")
    amount = st.text_input("Amount")
    customer = st.text_input("Customer Name")

    if st.button("Check Quality"):
        st.info("Document verification will be added next.")
        if document:
            st.write("Uploaded:", document.name)

elif page == "Reports":
    st.header("Quality Reports")
    st.info("No reports generated yet.")
