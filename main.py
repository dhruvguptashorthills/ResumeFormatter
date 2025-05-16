import streamlit as st
import json
import copy
from pdf_utils import PDFUtils  # Import the new class

# Streamlit App
st.title("Resume PDF Generator and Editor")
uploaded_file = st.file_uploader("Upload your resume JSON file", type=["json"])

# Session state init
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = None

if uploaded_file is not None:
    try:
        if st.session_state.resume_data is None:
            data = json.load(uploaded_file)
            st.success("JSON file loaded successfully!")
            st.session_state.resume_data = copy.deepcopy(data)
            st.session_state.resume_data.setdefault("education", [])
            st.session_state.resume_data.setdefault("projects", [])
            st.session_state.resume_data.setdefault("skills", [])

        pdf_display_container = st.empty()
        st.subheader("Edit Resume Fields")

        with st.form(key="resume_edit_form"):
            resume_data = st.session_state.resume_data

            # Name
            resume_data["name"] = st.text_input("Name", value=resume_data.get("name", ""))
            
            resume_data["title"] = st.text_input("Title", value=resume_data.get("title", ""))

            resume_data["summary"] = st.text_area("Summary", value=resume_data.get("summary", ""), height=100)
            # Education
            st.subheader("Education")
            for i, edu in enumerate(resume_data["education"]):
                st.markdown(f"**Education {i+1}**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    edu["institution"] = st.text_input(f"Institution {i+1}", value=edu.get("institution", ""), key=f"institution_{i}")
                with col2:
                    edu["degree"] = st.text_input(f"Degree {i+1}", value=edu.get("degree", ""), key=f"degree_{i}")
                with col3:
                    edu["year"] = st.text_input(f"Year {i+1}", value=edu.get("year", ""), key=f"year_{i}")

                c1, c2, c3 = st.columns([1, 1, 1])
                with c1:
                    if st.form_submit_button(f"⬆️ Edu {i+1}"):
                        if i > 0:
                            resume_data["education"][i - 1], resume_data["education"][i] = resume_data["education"][i], resume_data["education"][i - 1]
                            st.rerun()
                with c2:
                    if st.form_submit_button(f"⬇️ Edu {i+1}"):
                        if i < len(resume_data["education"]) - 1:
                            resume_data["education"][i + 1], resume_data["education"][i] = resume_data["education"][i], resume_data["education"][i + 1]
                            st.rerun()
                with c3:
                    if st.form_submit_button(f"🗑️ Delete Edu {i+1}"):
                        resume_data["education"].pop(i)
                        st.rerun()

            if st.form_submit_button("➕ Add Education"):
                resume_data["education"].append({"institution": "", "degree": "", "year": ""})
                st.rerun()

            # Projects
            st.subheader("Projects")
            for i, proj in enumerate(resume_data["projects"]):
                st.markdown(f"**Project {i+1}**")
                proj["title"] = st.text_input(f"Title {i+1}", value=proj.get("title", ""), key=f"title_{i}")
                proj["description"] = st.text_area(f"Description {i+1}", value=proj.get("description", ""), key=f"desc_{i}")

                c1, c2, c3 = st.columns([1, 1, 1])
                with c1:
                    if st.form_submit_button(f"⬆️ Move Up {i+1}"):
                        if i > 0:
                            resume_data["projects"][i - 1], resume_data["projects"][i] = resume_data["projects"][i], resume_data["projects"][i - 1]
                            st.rerun()
                with c2:
                    if st.form_submit_button(f"⬇️ Move Down {i+1}"):
                        if i < len(resume_data["projects"]) - 1:
                            resume_data["projects"][i + 1], resume_data["projects"][i] = resume_data["projects"][i], resume_data["projects"][i + 1]
                            st.rerun()
                with c3:
                    if st.form_submit_button(f"🗑️ Delete {i+1}"):
                        resume_data["projects"].pop(i)
                        st.rerun()

            if st.form_submit_button("➕ Add Project"):
                resume_data["projects"].append({"title": "", "description": ""})
                st.rerun()

            # Skills
            st.subheader("Skills")
            updated_skills = []
            for i, skill in enumerate(resume_data["skills"]):
                col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
                with col1:
                    skill_input = st.text_input(f"Skill {i+1}", value=skill, key=f"skill_input_{i}")
                    updated_skills.append(skill_input)
                with col2:
                    if st.form_submit_button(f"⬆️ Skill {i+1}"):
                        if i > 0:
                            resume_data["skills"][i - 1], resume_data["skills"][i] = resume_data["skills"][i], resume_data["skills"][i - 1]
                            st.rerun()
                with col3:
                    if st.form_submit_button(f"⬇️ Skill {i+1}"):
                        if i < len(resume_data["skills"]) - 1:
                            resume_data["skills"][i + 1], resume_data["skills"][i] = resume_data["skills"][i], resume_data["skills"][i + 1]
                            st.rerun()
                with col4:
                    if st.form_submit_button(f" Delete Skill {i+1}"):
                        resume_data["skills"].pop(i)
                        st.rerun()

            if st.form_submit_button("➕ Add Skill"):
                resume_data["skills"].append("")
                st.rerun()

            submit_button = st.form_submit_button("Update and Generate New PDF")

        if submit_button:
            # Clean up empty skills
            resume_data["skills"] = [s.strip() for s in updated_skills if s.strip()]

            with st.spinner("Generating PDF..."):
                pdf_file, html_out = PDFUtils.generate_pdf(resume_data)
                pdf_b64 = PDFUtils.get_base64_pdf(pdf_file)

                st.success("PDF generated successfully!")
                pdf_display = f'<iframe src="data:application/pdf;base64,{pdf_b64}" width="700" height="900" type="application/pdf"></iframe>'
                pdf_display_container.markdown(pdf_display, unsafe_allow_html=True)

                st.download_button("Download PDF", data=pdf_file, file_name="resume.pdf", mime="application/pdf")

    except json.JSONDecodeError:
        st.error("Invalid JSON file. Please upload a valid JSON file.")
else:
    st.info("Please upload a JSON file to start.")