import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from portfolio import Portfolio
from utils import clean_text
import PyPDF2
import io

def extract_text_from_pdf(uploaded_file):
    """Extract text from uploaded PDF file"""
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def create_streamlit_app(llm, portfolio, clean_text):
    st.title("📧 Job Application Assistant")
    
    tab1, tab2 = st.tabs(["Cold Email Generator", "Job Application Assistant"])
    
    with tab1:
        st.header("📧 Cold Email for Business Development")
        url_input = st.text_input("Enter Career Page URL:", value="https://jobs.nike.com/job/R-33460")
        submit_button = st.button("Generate Cold Email")
        
        if submit_button:
            try:
                loader = WebBaseLoader([url_input])
                data = clean_text(loader.load().pop().page_content)
                portfolio.load_portfolio()
                jobs = llm.extract_jobs(data)
                for job in jobs:
                    skills = job.get('skills', [])
                    links = portfolio.query_links(skills)
                    email = llm.write_mail(job, links)
                    st.code(email, language='markdown')
            except Exception as e:
                st.error(f"An Error Occurred: {e}")
    
    with tab2:
        st.header("🎓 Job Application Assistant")
        
        # Resume upload
        st.subheader("Step 1: Upload Your Resume")
        uploaded_file = st.file_uploader(
            "Choose your resume (PDF or TXT)", 
            type=['pdf', 'txt'],
            help="Upload your resume in PDF or TXT format"
        )
        
        resume_text = ""
        if uploaded_file is not None:
            if uploaded_file.type == "application/pdf":
                with st.spinner("Extracting text from PDF..."):
                    resume_text = extract_text_from_pdf(uploaded_file)
            else:
                resume_text = uploaded_file.getvalue().decode("utf-8")
            
            st.success(f"✅ Resume loaded: {uploaded_file.name}")
            
            with st.expander("Preview Resume Text"):
                st.text(resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text)
        
        # Job URL input
        st.subheader("Step 2: Enter Job URL")
        job_url = st.text_input(
            "Job posting URL:", 
            value="https://jobs.lever.co/shopback-2/12ad282d-bab1-4b02-8d16-5028ce42c9b9"
        )
        
        apply_button = st.button("Generate Application", type="primary")
        
        if apply_button:
            if not uploaded_file:
                st.error("Please upload your resume first!")
            elif not job_url:
                st.error("Please enter a job posting URL!")
            else:
                try:
                    # Load job posting
                    with st.spinner("📋 Analyzing job posting..."):
                        loader = WebBaseLoader([job_url])
                        job_data = clean_text(loader.load().pop().page_content)
                        jobs = llm.extract_jobs(job_data)
                    
                    if jobs:
                        job = jobs[0]
                        
                        # FIX 2: Extracted job details - all in left side (no columns)
                        st.subheader("📌 Extracted Job Details")
                        st.markdown(f"**Role:** {job.get('role', 'N/A')}")
                        st.markdown(f"**Experience:** {job.get('experience', 'N/A')}")
                        st.markdown(f"**Skills:** {', '.join(job.get('skills', []))}")
                        st.divider()
                        
                        # Compare resume with job
                        with st.spinner("🔍 Comparing your resume with job requirements..."):
                            comparison = llm.compare_resume_to_job(resume_text, job)
                        
                        # Display results
                        st.success("✅ Analysis complete!")
                        
                        # Show matched skills
                        st.subheader("✅ Skills That Match")
                        matched = comparison.get('matched_skills', [])
                        if matched:
                            for skill in matched:
                                st.markdown(f"- {skill}")
                        else:
                            st.info("No direct skill matches found. Highlight relevant projects instead.")
                        
                        # Show missing skills
                        st.subheader("⚠️ Skills to Develop")
                        missing = comparison.get('missing_skills', [])
                        if missing:
                            for skill in missing:
                                st.markdown(f"- {skill}")
                        else:
                            st.success("You have all the required skills! Great match!")
                        
                        # Show resume suggestions
                        st.subheader("📝 Resume Improvement Suggestions")
                        suggestions = comparison.get('resume_suggestions', [])
                        if suggestions:
                            for suggestion in suggestions:
                                st.markdown(f"- {suggestion}")
                        
                        # Generate application email
                        with st.spinner("✍️ Writing your application email..."):
                            email = llm.write_application_email(
                                job, 
                                resume_text,
                                comparison.get('matched_skills', []),
                                comparison.get('missing_skills', [])
                            )
                        
                        # FIX 1: Email displayed in full width without horizontal scroll
                        st.subheader("📧 Application Email")
                        
                        # Use text_area with height to show full email (no horizontal scroll)
                        st.text_area(
                            "Your Application Email (Copy below)", 
                            value=email, 
                            height=400, 
                            key="application_email",
                            label_visibility="collapsed"
                        )
                        
                        # FIX 3: Working copy button using JavaScript
                        st.markdown("""
                            <script>
                            function copyEmail() {
                                const emailText = document.querySelector('textarea[key="application_email"]').value;
                                navigator.clipboard.writeText(emailText);
                                alert('Email copied to clipboard!');
                            }
                            </script>
                        """, unsafe_allow_html=True)
                        
                        # Simple working copy button
                        if st.button("📋 Copy Email to Clipboard", key="copy_btn"):
                            st.write(f'<script>navigator.clipboard.writeText(`{email}`); alert("Email copied!");</script>', unsafe_allow_html=True)
                            st.success("✅ Email copied to clipboard!")
                        
                    else:
                        st.error("Could not extract job details from the URL. Please check if it's a valid job posting.")
                        
                except Exception as e:
                    st.error(f"An Error Occurred: {str(e)}")
                    st.info("Try pasting the job description directly if URL extraction fails.")


if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    st.set_page_config(layout="wide", page_title="Job Application Assistant", page_icon="📧")
    create_streamlit_app(chain, portfolio, clean_text)