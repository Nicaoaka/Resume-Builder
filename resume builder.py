import re
from huggingface_hub import InferenceClient
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

client = InferenceClient(api_key="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")

def validate_email(email):
    if email == "0":
        return True
    regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.fullmatch(regex, email)

def validate_phone(phone):
    if phone == "0":
        return True
    country_codes = [
        "+1", "+7", "+20", "+27", "+30", "+31", "+32", "+33", "+34", "+36", "+39", "+40", "+41", "+43", "+44", "+45", 
        "+46", "+47", "+48", "+49", "+51", "+52", "+53", "+54", "+55", "+56", "+57", "+58", "+60", "+61", "+62", "+63", 
        "+64", "+65", "+66", "+81", "+82", "+84", "+86", "+90", "+91", "+92", "+93", "+94", "+95", "+98", "+211", "+212", 
        "+213", "+216", "+218", "+220", "+221", "+222", "+223", "+224", "+225", "+226", "+227", "+228", "+229", "+230", 
        "+231", "+232", "+233", "+234", "+235", "+236", "+237", "+238", "+239", "+240", "+241", "+242", "+243", "+244", 
        "+245", "+246", "+248", "+249", "+250", "+251", "+252", "+253", "+254", "+255", "+256", "+257", "+258", "+260", 
        "+261", "+262", "+263", "+264", "+265", "+266", "+267", "+268", "+269", "+290", "+291", "+297", "+298", "+299", 
        "+350", "+351", "+352", "+353", "+354", "+355", "+356", "+357", "+358", "+359", "+370", "+371", "+372", "+373", 
        "+374", "+375", "+376", "+377", "+378", "+379", "+380", "+381", "+382", "+383", "+385", "+386", "+387", "+389", 
        "+420", "+421", "+423", "+500", "+501", "+502", "+503", "+504", "+505", "+506", "+507", "+508", "+509", "+590", 
        "+591", "+592", "+593", "+594", "+595", "+596", "+597", "+598", "+599", "+670", "+672", "+673", "+674", "+675", 
        "+676", "+677", "+678", "+679", "+680", "+681", "+682", "+683", "+685", "+686", "+687", "+688", "+689", "+690", 
        "+691", "+692", "+850", "+852", "+853", "+855", "+856", "+880", "+886", "+960", "+961", "+962", "+963", "+964", 
        "+965", "+966", "+967", "+968", "+970", "+971", "+972", "+973", "+974", "+975", "+976", "+977", "+992", "+993", 
        "+994", "+995", "+996", "+998"
    ]
    phone = phone.strip()
    if any(phone.startswith(code) for code in country_codes):
        pattern = r'^\+\d{1,3}\s*\(?\d{3}\)?\s*\d{3}-\d{4}$'
    else:
        pattern = r'^\(?\d{3}\)?\s*\d{3}-\d{4}$'
    return re.mactch(pattern, phone)
    
def format_phone(phone):
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 10:
        return f'({digits[:3]}) {digits[3:6]}-{digits[6:]}' # Check this later
    elif len(digits) == 11:
        return f'{digits[0]} ({digits[1:4]}) {digits[4:7]}-{digits[7:]}' # Check this later
    else:
        return phone
    
def collect_user_info():
    user_info = {}

    # Asking for name
    user_info['full_name'] = input("What is your full name?\n>> ").strip()

    # Asking for email
    while True:
        email = input("What is your email address? Type 0 if you want to void this question and part on your resume\n>> ").strip()
        if validate_email(email):
            user_info['email'] = email if email != "0" else ""
            break
        else:
            print("Invalid email address. Please try again.")

    # Asking for phone number
    while True:
        phone = input("What is your phone number? Type 0 if you want to void this question and part on your resume\n>> ").strip()
        if validate_phone(phone):
            user_info['phone'] = format_phone(phone) if phone != "0" else ""
            break
        else:
            print("Invalid phone number. Please try again.")

    # Asking for Education Background
    education_choices = {
        "1": "High School",
        "2": "University"
    }
    print("Choose your education level (1 or 2): \n1. High School\n2. University")
    while True:
        edu_choice = input(">> ").strip()
        if edu_choice in education_choices:
            user_info['education'] = education_choices[edu_choice]
            break
        else:
            print("Invalid choice. Please select 1 or 2.")

    # Asking for Skills
    print("List your skills. Type '0' when finished")
    skills = []
    while True:
        skill = input(">> ").strip()
        if skill == "0":
            break
        skills.append(skill)
    user_info['skills'] = skills

    # Asking for Achievements
    print("List your achievements. Type '0' when finished")
    achievements = []
    while True:
        achievement = input(">> ").strip()
        if achievement == "0":
            break
        achievements.append(achievement)
        if len(achievements) >= 5:  # limit to prevent too many achievements
            print("Achievement limit reached. We will move onto the next.")
            break
    user_info['achievements'] = achievements

    # Asking for Work Experience
    user_info['work_experience'] = []
    print("Enter your past job experiences. Type '0' when finished:")
    while True:
        job_title = input(">> ").strip()
        if job_title == "0":
            break
        job = {'title': job_title}

        job['location'] = input("Where was this job located?\n>> ").strip()
        job['start_date'] = input("What was your start date? (MM/YYYY).\n>> ").strip()
        job['end_date'] = input("What was your end date? (MM/YYYY). Type 'Present' if you are still working there.\n>> ").strip()

        description = generate_job_description(job_title)
        job['description'] = description

        user_info['work_experience'].append(job)

    return user_info

def generate_job_description(job_title):
    messages = [
        {
            "role": "system",
            "content": f"""
You are a professional resume generator, specifically for this task you are generating the work experience description part of a resume for someone who is applying for a job.
Format what they did at their job with "*" as bulletpoints you are limited to only giving 3 bulletpoints.
You are generating it for {job_title}.
            """
        }
    ]
    
    stream = client.chat.completions.create(
    model="meta-llama/Llama-3.2-1B-Instruct", 
	messages=messages, 
	max_tokens=200,
    temperature=0,
	stream=True
    )
    
    output = ""
    for chunk in stream:
        output += chunk.get('choices', [{}])[0].get('delta', {}).get('content', '')

    bullet_points = [line.strip() for line in output.split('\n') if line.strip().startswith('*')]
    return bullet_points[:3]

def generate_pdf(user_info):
    c = canvas.Canvas("resume.pdf", pagesize=letter)
    width, height = letter
    y_position = height - 50
    
    # Full Name
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, y_position, user_info['full_name'])
    y_position -= 30
    
    # Contact Information
    c.setFont("Helvetica", 12)
    contact_info = ""
    if user_info['email']:
        contact_info += f"Email: {user_info['email']}"
    if user_info['phone']:
        contact_info =+ f"Phone: {user_info['phone']}"
    c.drawString(50, y_position, contact_info)
    
    # Education
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position, "Education")
    y_position -= 20
    c.setFont("Helvetica", 12)
    c.drawString(60, y_position, user_info['education'])
    y_position -= 30
    
    # Work Experience
    if user_info['work_experience']:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, "Work Experience")
        y_position -= 20
        c.setFont("Helvetica", 12)
        for job in user_info ['work_experience']:
            c.drawString(60, y_position, f"**{job['title']}**")
            y_position -= 15
            c.drawString(60, y_position, f"{job['location']} | {job['start_date']} - {job['end_date']}")
            y_position -= 15
            for bullet in job['description']:
                c.drawString(70, y_position, bullet)
                y_position -= 15
            y_position -= 10
            
    # Skills
    if user_info['skills']:
        c.setFont("Helvetica", 14)
        c.drawString(50, y_position, "Skills")
        y_position -= 20
        c.setFont("Helvetica", 12)
        skills_text = ', '.join(user_info['skills'])
        c.drawString(60, y_position, skills_text)
        y_position -= 30
        
    # Achievements
    if user_info['achievements']:
        c.setFont("Helvetica", 14)
        c.drawString(50, y_position, "Achievements")
        y_position -= 20
        c.setFont("Helvetica", 12)
        for achievement in user_info['achievements']:
            c.drawString(60, y_position, f"- {achievement}")
            y_position -= 15
        
    c.save()
    print("Resume generated.")

def main():
    user_info = collect_user_info()
    generate_pdf(user_info)
    
if __name__ == "__main__":
    main()