# ============================================================
#  AUTO JOB APPLY - YOUR PERSONAL CONFIGURATION
#  Fill in your details below before running the script
# ============================================================

# --- YOUR LOGIN CREDENTIALS ---
LINKEDIN_EMAIL = "YOUR MAIL HERE"
LINKEDIN_PASSWORD = "YOUR PASSWORD HERE"

STEPSTONE_EMAIL = "YOUR MAIL HERE"
STEPSTONE_PASSWORD = "YOUR PASSWORD HERE"

# --- YOUR PERSONAL INFO (used to fill application forms) ---
FIRST_NAME = "XXXX"
LAST_NAME  = "XXXX"
PHONE      = "+49 1XXXXXXXXX"   # include country code
CITY       = "Berlin"             # or your city
COUNTRY    = "Germany"

# --- YOUR CV / RESUME ---
# Full path to your CV file on your Mac, e.g.:
# "/Users/yourname/Documents/CV_John_Doe.pdf"
CV_PATH = "/Users/USERNAME/Downloads/CV.pdf"

# --- JOB SEARCH SETTINGS ---
JOB_TITLE    = "Frontend Developer"
LOCATION     = "Berlin,Germany"           # city or country
MAX_APPLIES  = 20                 # max applications per run (safety limit)
EXPERIENCE_LEVEL = "Entry Level"   # used to filter results

# --- LINKEDIN SPECIFIC ---
# Extra keywords to add to the search (optional)
LINKEDIN_KEYWORDS = "React JavaScript HTML CSS"

# --- STEPSTONE SPECIFIC ---
STEPSTONE_KEYWORDS = "Frontend Developer Junior React"
STEPSTONE_LOCATION = "Deutschland"  # German spelling for Germany

# --- COVER LETTER (optional, leave blank to skip) ---
# A short default cover letter. {job_title} and {company} will be
# automatically replaced with the real job title and company name.
COVER_LETTER = """
Subject: {job_title} Application | {full_name} | Frontend Developer

Dear {company_name} hiring team,

I am writing to apply for the {job_title} position at {company_name}. As a Frontend Developer specialized in React, JavaScript (ES6+), and Responsive Design, I focus on building clean, performant user interfaces that scale.

Technical Stack & Value:

Modern Frontend: Proficient in React (Hooks, Context API) and state management.

Styling & UI: Expert in CSS3, Tailwind, or Sass with a "mobile-first" approach.

Professional Workflow: Experience with Git/GitHub, NPM, and writing maintainable code.

I have followed {company_name}’s growth in the {company_industry} space and am eager to bring my problem-solving mindset to your engineering team. I am a fast learner, a clear communicator, and I'm ready to contribute to production-ready code from day one.

My portfolio and CV are attached for your review. I look forward to the possibility of discussing how my skills align with your team's goals.

Best regards,

{full_name}
""".strip()
