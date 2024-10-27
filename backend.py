import re
import os
from huggingface_hub import InferenceClient
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime

# Optional: Register a standard font if needed
# Note: 'Helvetica' is a standard font in ReportLab and does not require registration.
# If you wish to use a custom font, uncomment the following lines and ensure the font file is accessible.
# pdfmetrics.registerFont(TTFont('Helvetica', 'Helvetica.ttf'))

# Initialize the Inference Client with your API key
# It's safer to load the API key from an environment variable or a secure config
API_KEY = os.getenv("HF_API_KEY", "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")  # Replace with your method of loading API keys
client = InferenceClient(api_key=API_KEY)

def validate_email(email):
    if email == "0":
        return True
    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
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
    
    # Check if phone starts with a country code
    if any(phone.startswith(code) for code in country_codes):
        pattern = r'^\+\d{1,3}\s*\(?\d{3}\)?\s*\d{3}-\d{4}$'
    else:
        # Pattern options:
        # 1. Exactly 10 digits: 1234567890
        # 2. (123) 456-7890
        # 3. 123-456-7890
        # 4. 123 456 7890
        pattern = r'^(\d{10}|\(\d{3}\)\s*\d{3}-\d{4}|\d{3}-\d{3}-\d{4}|\d{3}\s\d{3}\s\d{4})$'
    
    return re.match(pattern, phone) is not None

def format_phone(phone):
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 10:
        return f'({digits[:3]}) {digits[3:6]}-{digits[6:]}'
    elif len(digits) == 11:
        return f'{digits[0]} ({digits[1:4]}) {digits[4:7]}-{digits[7:]}'
    else:
        return phone

def validate_date(date_str):
    if date_str == "0":
        return True
    regex = r'^(0[1-9]|1[0-2])/(\d{4})$'  # Matches MM/YYYY
    return re.fullmatch(regex, date_str) is not None

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%m/%Y")
    except ValueError:
        return None

def collect_user_info():
    user_info = {}

    # Asking for name
    user_info['full_name'] = input("What is your full name?\n>> ").strip()

    # Asking for email
    while True:
        email = input("\nWhat is your email address? Type '0' if you want to void this question and omit it on your resume\n>> ").strip()
        if validate_email(email):
            user_info['email'] = email if email != "0" else ""
            break
        else:
            print("Invalid email address. Please try again.")

    # Asking for phone number
    while True:
        phone = input("\nWhat is your phone number? Type '0' if you want to void this question and omit it on your resume\n>> ").strip()
        if validate_phone(phone):
            user_info['phone'] = format_phone(phone) if phone != "0" else ""
            break
        else:
            print("Invalid phone number. Please try again.")

    # Asking for Education Background
    print("\nEnter your education details. Type '0' to skip any section.")

    # High School
    high_school = input("What is the name of your High School?\n>> ").strip()
    if high_school != "0" and high_school != "":
        user_info['high_school'] = high_school
        # Prompt for High School Graduation Date with Validation
        while True:
            high_school_grad = input("What is your High School Graduation Date? (MM/YYYY) or type '0' to skip\n>> ").strip()
            if validate_date(high_school_grad):
                if high_school_grad == "0" or high_school_grad == "":
                    user_info['high_school_grad_date'] = ""
                    user_info['high_school_grad_label'] = ""
                else:
                    parsed_date = parse_date(high_school_grad)
                    if parsed_date:
                        current_date = datetime.now()
                        if parsed_date > current_date:
                            label = "Expected Graduation Date"
                        else:
                            label = "Graduation Date"
                        user_info['high_school_grad_date'] = high_school_grad
                        user_info['high_school_grad_label'] = label
                    else:
                        print("Invalid date. Please enter a valid date in MM/YYYY format or type '0' to skip.")
                        continue
                break
            else:
                print("Invalid date format. Please enter in MM/YYYY format or type '0' to skip.")
    else:
        user_info['high_school'] = ""
        user_info['high_school_grad_date'] = ""
        user_info['high_school_grad_label'] = ""

    # University
    university = input("\nWhat is the name of your University?\n>> ").strip()
    if university != "0" and university != "":
        user_info['university'] = university
        # Prompt for University Graduation Date with Validation
        while True:
            university_grad = input("What is your University Graduation Date or Expected Graduation Date? (MM/YYYY) or type '0' to skip\n>> ").strip()
            if validate_date(university_grad):
                if university_grad == "0" or university_grad == "":
                    user_info['university_grad_date'] = ""
                    user_info['university_grad_label'] = ""
                else:
                    parsed_date = parse_date(university_grad)
                    if parsed_date:
                        current_date = datetime.now()
                        if parsed_date > current_date:
                            label = "Expected Graduation Date"
                        else:
                            label = "Graduation Date"
                        user_info['university_grad_date'] = university_grad
                        user_info['university_grad_label'] = label
                    else:
                        print("Invalid date. Please enter a valid date in MM/YYYY format or type '0' to skip.")
                        continue
                break
            else:
                print("Invalid date format. Please enter in MM/YYYY format or type '0' to skip.")
    else:
        user_info['university'] = ""
        user_info['university_grad_date'] = ""
        user_info['university_grad_label'] = ""

    # Asking for Skills
    print("\nList your skills. Type '0' when finished")
    skills = []
    while True:
        skill = input(">> ").strip()
        if skill == "0":
            break
        skills.append(skill)
    user_info['skills'] = skills

    # Asking for Achievements
    print("\nList your achievements. Type '0' when finished")
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
    while True:
        print("\nEnter your past job experiences. Type '0' when finished:")
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
You are a professional resume generator. Your task is to generate the work experience description part of a resume for someone who is applying for a job.
Format what they did at their job with "*" as bullet points. You are limited to only giving 3 bullet points.
You are generating it for {job_title}.
            """
        }
    ]
    
    try:
        stream = client.chat.completions.create(
            model="meta-llama/Llama-3.2-1B-Instruct", 
            messages=messages, 
            max_tokens=200,
            temperature=0,
            stream=True
        )
        
        output = ""
        for chunk in stream:
            # Debugging: Print each chunk received
            # print(chunk)  # Uncomment this line for debugging
            output += chunk.get('choices', [{}])[0].get('delta', {}).get('content', '')

        bullet_points = [line.strip() for line in output.split('\n') if line.strip().startswith('*')]
        return bullet_points[:3]
    except Exception as e:
        print(f"Error generating job description: {e}")
        return ["* Description not available."]

def split_text(text, max_width, font_name, font_size):
    """
    Splits the text into multiple lines so that each line does not exceed max_width.
    """
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        # Check the width of the current line plus the next word
        test_line = f"{current_line} {word}".strip()
        if pdfmetrics.stringWidth(test_line, font_name, font_size) <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

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
        contact_info += f"Email: {user_info['email']}  "
    if user_info['phone']:
        contact_info += f"Phone: {user_info['phone']}"
    c.drawString(50, y_position, contact_info)
    y_position -= 30

    # Education
    if user_info.get('high_school') or user_info.get('university'):
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, "Education")
        y_position -= 20
        c.setFont("Helvetica", 12)
        if user_info.get('university'):
            uni_info = f"University: {user_info['university']}"
            if user_info.get('university_grad_date') and user_info.get('university_grad_label'):
                uni_info += f" ({user_info['university_grad_label']}: {user_info['university_grad_date']})"
            c.drawString(60, y_position, uni_info)
            y_position -= 15
        if user_info.get('high_school'):
            hs_info = f"High School: {user_info['high_school']}"
            if user_info.get('high_school_grad_date') and user_info.get('high_school_grad_label'):
                hs_info += f" ({user_info['high_school_grad_label']}: {user_info['high_school_grad_date']})"
            c.drawString(60, y_position, hs_info)
            y_position -= 15
        y_position -= 15  # Extra space after education section

    # Work Experience
    if user_info['work_experience']:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, "Work Experience")
        y_position -= 20
        for job in user_info['work_experience']:
            # Job Title in Bold
            c.setFont("Helvetica-Bold", 12)
            c.drawString(60, y_position, job['title'])
            y_position -= 15
            # Location and Dates
            c.setFont("Helvetica", 12)
            c.drawString(60, y_position, f"{job['location']} | {job['start_date']} - {job['end_date']}")
            y_position -= 15
            # Bullet Points with Wrapping
            c.setFont("Helvetica", 12)
            max_bullet_width = width - 80  # Adjusted for margins and bullet indentation
            for bullet in job['description']:
                if y_position < 50:
                    c.showPage()
                    y_position = height - 50
                    # Reapply section headers after new page
                    c.setFont("Helvetica-Bold", 14)
                    c.drawString(50, y_position, "Work Experience")
                    y_position -= 20
                    c.setFont("Helvetica", 12)
                # Split the bullet text into multiple lines if necessary
                bullet_text = bullet.lstrip('* ').strip()
                wrapped_lines = split_text(bullet_text, max_bullet_width, "Helvetica", 12)
                if wrapped_lines:
                    # **Modified Line**: Use '-' instead of '*' for bullet points
                    c.drawString(70, y_position, f"- {wrapped_lines[0]}")
                    y_position -= 15
                    # Draw the remaining lines with indentation
                    for line in wrapped_lines[1:]:
                        c.drawString(90, y_position, line)
                        y_position -= 15
            y_position -= 10  # Space after each job

    # Skills
    if user_info['skills']:
        if y_position < 80:
            c.showPage()
            y_position = height - 50
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, "Skills")
        y_position -= 20
        c.setFont("Helvetica", 12)
        skills_text = ', '.join(user_info['skills'])
        wrapped_skills = split_text(skills_text, width - 100, "Helvetica", 12)
        for line in wrapped_skills:
            if y_position < 50:
                c.showPage()
                y_position = height - 50
                c.setFont("Helvetica-Bold", 14)
                c.drawString(50, y_position, "Skills")
                y_position -= 20
                c.setFont("Helvetica", 12)
            c.drawString(60, y_position, line)
            y_position -= 15
        y_position -= 15

    # Achievements
    if user_info['achievements']:
        if y_position < 80:
            c.showPage()
            y_position = height - 50
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, "Achievements")
        y_position -= 20
        c.setFont("Helvetica", 12)
        for achievement in user_info['achievements']:
            if y_position < 50:
                c.showPage()
                y_position = height - 50
                c.setFont("Helvetica-Bold", 14)
                c.drawString(50, y_position, "Achievements")
                y_position -= 20
                c.setFont("Helvetica", 12)
            # Split achievement text if necessary
            wrapped_achievement = split_text(achievement, width - 100, "Helvetica", 12)
            if wrapped_achievement:
                # **Modified Line**: Use '-' instead of '*' for bullet points
                c.drawString(60, y_position, f"- {wrapped_achievement[0]}")
                y_position -= 15
                for line in wrapped_achievement[1:]:
                    c.drawString(80, y_position, line)
                    y_position -= 15
        y_position -= 10

    # Save the PDF
    c.save()
    print("\nResume generated successfully as 'resume.pdf'.")

def main():
    user_info = collect_user_info()
    generate_pdf(user_info)

if __name__ == "__main__":
    main()
