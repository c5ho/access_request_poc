import streamlit as st
from pathlib import Path
from .pipeline import process_file
from . import ocr
from .reviewer_store import save_review, list_reviews
from .ui_helpers import render_highlighted_image
from .reviewer_auth import list_reviewer_names, validate_reviewer


DATA_DIR = Path(__file__).parents[2] / "data" / "samples"


def display_pdf(path: Path):
    st.write(f"PDF: {path.name}")
    try:
        with open(path, "rb") as f:
            data = f.read()
        st.download_button("Download PDF", data, file_name=path.name)
    except Exception:
        st.text("Unable to display PDF in this environment")


def main():
    st.title("Access Request Reviewer")

    samples = sorted(list(DATA_DIR.glob("*.txt")) + list(DATA_DIR.glob("*.pdf")))
    choice = st.sidebar.selectbox("Sample file", [str(p.name) for p in samples])
    
    # Reviewer authentication
    reviewer_names = list_reviewer_names()
    if reviewer_names:
        reviewer = st.sidebar.selectbox("Reviewer", reviewer_names)
    else:
        reviewer = st.sidebar.text_input("Reviewer name", value="")
    token = st.sidebar.text_input("Auth token", type="password")
    auth_info = None
    if reviewer and token:
        auth_info = validate_reviewer(reviewer, token)
    if auth_info:
        st.sidebar.success(f"Authenticated as {auth_info.get('name')} ({auth_info.get('role')})")
    else:
        if token:
            st.sidebar.error("Invalid reviewer or token")
    file_path = DATA_DIR / choice
    st.sidebar.write("Path:", str(file_path))

    meta_path = file_path.with_suffix(".meta.json")

    if file_path.suffix.lower() == ".txt":
        text = file_path.read_text(encoding="utf-8")
        st.subheader("Source Text")
        st.text_area("source", text, height=200)
        result = process_file(str(file_path))
    else:
        display_pdf(file_path)
        st.subheader("OCR Text (if available)")
        text = ocr.ocr_pdf(str(file_path))
        if not text:
            st.warning("OCR not available or failed for this PDF.")
        st.text_area("ocr", text or "", height=200)
        result = process_file(str(file_path))

    # Attempt to display highlighted image if annotations exist
    if meta_path.exists():
        try:
            import json

            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            ann = meta.get("annotations", [])
            img = render_highlighted_image(str(file_path), ann)
            if img is not None:
                st.subheader("Highlighted fields")
                st.image(img)
        except Exception:
            pass

    st.subheader("Extracted Fields")
    req = result.get("request", {})
    cols = st.columns(2)
    with cols[0]:
        employee_id = st.text_input("Employee ID", value=req.get("employee_id") or "")
        first_name = st.text_input("First Name", value=req.get("first_name") or "")
        last_name = st.text_input("Last Name", value=req.get("last_name") or "")
        department = st.text_input("Department", value=req.get("department") or "")
    with cols[1]:
        job_title = st.text_input("Job Title", value=req.get("job_title") or "")
        requested_role = st.text_input("Requested Role", value=req.get("requested_role") or "")
        manager_approved = st.checkbox("Manager Approved", value=bool(req.get("manager_approved")))
        start_date = st.text_input("Start Date", value=req.get("start_date") or "")

    st.subheader("Decision")
    decision = result.get("decision", {})
    status = decision.get("status")
    status_label = f"{status} ({decision.get('reason', 'n/a')})"
    if status == "APPROVE":
        st.success(status_label)
    elif status == "REJECT":
        st.error(status_label)
    else:
        st.warning(status_label)
    st.write(f"Confidence: {result.get('confidence')}")
    st.write(f"Needs human review: {result.get('needs_human_review')}")

    st.subheader("Reviewer Action")
    action = st.radio("Action", ["APPROVE", "REJECT", "ESCALATE"], index=0)
    comment = st.text_area("Reviewer comment")

    if st.button("Save Review"):
        if not auth_info:
            st.error("Reviewer not authenticated. Provide valid token.")
        else:
            review = {
                "file": choice,
                "reviewer": reviewer,
                "reviewer_role": auth_info.get("role"),
                "action": action,
                "comment": comment,
                "extracted": {
                    "employee_id": employee_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "department": department,
                    "job_title": job_title,
                    "requested_role": requested_role,
                    "manager_approved": manager_approved,
                    "start_date": start_date,
                },
                "pipeline_decision": result.get("decision"),
                "confidence": result.get("confidence"),
            }
            save_review(review)
            st.success("Saved review")

    st.subheader("Past Reviews")
    reviews = list_reviews()
    for r in reversed(reviews[-10:]):
        st.json(r)


if __name__ == "__main__":
    main()
