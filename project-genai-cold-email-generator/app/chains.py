import os
import json
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

load_dotenv()

class Chain:
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0, 
            groq_api_key=os.getenv("GROQ_API_KEY"), 
            model_name="llama-3.3-70b-versatile"
        )

    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the career's page of a website.
            Your job is to extract the job postings and return them in JSON format containing the following keys: `role`, `experience`, `skills` and `description`.
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):
            """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res if isinstance(res, list) else [res]

    def write_mail(self, job, links):
        prompt_email = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}

            ### INSTRUCTION:
            You are Mohan, a business development executive at AtliQ. AtliQ is an AI & Software Consulting company dedicated to facilitating
            the seamless integration of business processes through automated tools. 
            Over our experience, we have empowered numerous enterprises with tailored solutions, fostering scalability, 
            process optimization, cost reduction, and heightened overall efficiency. 
            Your job is to write a cold email to the client regarding the job mentioned above describing the capability of AtliQ 
            in fulfilling their needs.
            Also add the most relevant ones from the following links to showcase Atliq's portfolio: {link_list}
            Remember you are Mohan, BDE at AtliQ. 
            Do not provide a preamble.
            ### EMAIL (NO PREAMBLE):

            """
        )
        chain_email = prompt_email | self.llm
        res = chain_email.invoke({"job_description": str(job), "link_list": links})
        return res.content

    def extract_resume_data(self, resume_text):
        """
        Extracts skills, experience, projects, and education from resume
        """
        prompt_resume = PromptTemplate.from_template(
            """
            ### RESUME TEXT:
            {resume_text}

            ### INSTRUCTION:
            Analyze this resume and extract the following information:
            - skills: List of technical and soft skills found
            - experience: Summary of work experience
            - projects: List of projects mentioned
            - education: Education details
            
            Return ONLY valid JSON with these keys.

            ### VALID JSON (NO PREAMBLE):
            """
        )
        chain_resume = prompt_resume | self.llm
        res = chain_resume.invoke(input={"resume_text": resume_text[:3000]})
        
        try:
            json_parser = JsonOutputParser()
            return json_parser.parse(res.content)
        except OutputParserException:
            return {"skills": [], "experience": "", "projects": [], "education": ""}

    def compare_resume_to_job(self, resume_text, job_data):
        """
        Compares resume with job requirements and returns analysis
        """
        prompt_comparison = PromptTemplate.from_template(
            """
            ### RESUME TEXT:
            {resume_text}

            ### JOB DESCRIPTION:
            {job_data}

            ### INSTRUCTION:
            Analyze the resume against this job description and provide a JSON response with:
            1. "matched_skills": List of skills from resume that match what the job wants
            2. "missing_skills": List of skills the job wants but are missing from resume
            3. "resume_suggestions": 3-5 specific suggestions to improve resume for this role

            Return ONLY valid JSON.

            ### YOUR JSON RESPONSE:
            """
        )
        chain_comparison = prompt_comparison | self.llm
        res = chain_comparison.invoke({
            "resume_text": resume_text[:4000],
            "job_data": str(job_data)[:4000]
        })
        
        try:
            # Try to parse JSON from response
            content = res.content.strip()
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = content[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return {
                    "matched_skills": [],
                    "missing_skills": [],
                    "resume_suggestions": ["Could not parse resume. Please check format."]
                }
        except Exception as e:
            print(f"Parse error: {e}")
            return {
                "matched_skills": [],
                "missing_skills": [],
                "resume_suggestions": ["Unable to analyze. Please try again."]
            }

    def write_application_email(self, job, resume_text, matched_skills, missing_skills):
        """
        Writes a student's job application email
        """
        prompt_email = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}

            ### MY RESUME:
            {resume_text}

            ### STRENGTHS (Skills I have that match):
            {matched_skills}

            ### AREAS TO IMPROVE (Skills I'm developing):
            {missing_skills}

            ### INSTRUCTION:
            Write a professional job application email as a STUDENT/CANDIDATE applying for this position.
            
            Requirements:
            - Subject line: "Application for [Job Title] - [Your Name]"
            - Show enthusiasm and mention specific matched skills (2-3)
            - Briefly mention 1-2 relevant projects from resume
            - Acknowledge missing skills with willingness to learn
            - Professional closing with contact info placeholders
            
            Do NOT write as a company. Write as an individual candidate.
            Keep the email concise (250-350 words).
            
            ### EMAIL:
            """
        )
        chain_email = prompt_email | self.llm
        res = chain_email.invoke({
            "job_description": str(job),
            "resume_text": resume_text[:3000],
            "matched_skills": str(matched_skills),
            "missing_skills": str(missing_skills)
        })
        return res.content


if __name__ == "__main__":
    print(os.getenv("GROQ_API_KEY"))