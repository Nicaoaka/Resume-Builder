import re
import os
from huggingface_hub import InferenceClient
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime

API_KEY = os.getenv("HF_API_KEY", "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")
client = InferenceClient(api_key=API_KEY)

def capitalize_words(text, exceptions=None):
    if exceptions is None:
        exceptions = []
    words = text.split()
    capitalized_words = [word.capitalize() if word.lower() not in exceptions else word.lower() for word in words]
    return ' '.join(capitalized_words)

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
    if date_str.lower() == "0":
        return True
    regex = r'^(0[1-9]|1[0-2])/(\d{4})$'
    return re.fullmatch(regex, date_str) is not None

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%m/%Y")
    except ValueError:
        return None

def format_date(date_str):
    """Converts MM/YYYY to 'Month Year'."""
    try:
        date_obj = datetime.strptime(date_str, "%m/%Y")
        return date_obj.strftime("%B %Y")
    except ValueError:
        return date_str

def collect_user_info():
    user_info = {}
    current_date = datetime.now()

    # Asking for name
    user_info['full_name'] = input("What Is Your Full Name?\n>> ").strip()

    # Asking for email
    while True:
        email = input("\nWhat Is Your Email Address? Type '0' If You Want To Void This Question And Omit It On Your Resume\n>> ").strip()
        if validate_email(email):
            user_info['email'] = email if email.lower() != "0" else ""
            break
        else:
            print("Invalid email address. Please try again.")

    # Asking for phone number
    while True:
        phone = input("\nWhat Is Your Phone Number? Type '0' If You Want To Void This Question And Omit It On Your Resume\n>> ").strip()
        if validate_phone(phone):
            user_info['phone'] = format_phone(phone) if phone.lower() != "0" else ""
            break
        else:
            print("Invalid phone number. Please try again.")

    # Asking for Education Background
    print("\nEnter Your Education Details.")

    # High School
    high_school = input("What Is The Name Of Your High School?\n>> ").strip()
    if high_school != "":
        user_info['high_school'] = capitalize_words(high_school)
        # Prompt for High School Graduation Date with Validation
        while True:
            high_school_grad = input("What Is Your High School Graduation Date? (MM/YYYY)\n>> ").strip()
            if validate_date(high_school_grad):
                parsed_date = parse_date(high_school_grad)
                if parsed_date:
                    if parsed_date > current_date:
                        label = "Expected Graduation Date"
                    else:
                        label = "Graduation Date"
                    user_info['high_school_grad_date'] = format_date(high_school_grad)
                    user_info['high_school_grad_label'] = label
                    break
                else:
                    print("Invalid date. Please enter a valid date in MM/YYYY format.")
            else:
                print("Invalid date format. Please enter in MM/YYYY format.")

        # Check if High School Graduation Date has not passed
        if parsed_date and parsed_date > current_date:
            print("\nHigh School Graduation Date Has Not Yet Passed. Skipping University Questions.")
            user_info['university'] = ""
            user_info['university_grad_date'] = ""
            user_info['university_grad_label'] = ""
            user_info['university_degree'] = ""
            user_info['university_gpa'] = ""
        else:
            # University
            university = input("\nWhat Is The Name Of Your University?\n>> ").strip()
            if university != "":
                user_info['university'] = capitalize_words(university, exceptions=["of"])
                while True:
                    university_grad = input("What Is Your University Graduation Date Or Expected Graduation Date? (MM/YYYY)\n>> ").strip()
                    if validate_date(university_grad):
                        parsed_uni_grad = parse_date(university_grad)
                        if parsed_uni_grad:
                            if parsed_uni_grad > current_date:
                                label = "Expected Graduation Date"
                            else:
                                label = "Graduation Date"
                            user_info['university_grad_date'] = format_date(university_grad)
                            user_info['university_grad_label'] = label
                            break
                        else:
                            print("Invalid date. Please enter a valid date in MM/YYYY format.")
                    else:
                        print("Invalid date format. Please enter in MM/YYYY format.")

                # Asking for Degree
                while True:
                    degree = input("What Is Your Degree? (e.g., Bachelor of Science in Computer Science)\n>> ").strip()
                    if degree == "":
                        print("Degree cannot be empty. Please enter your degree.")
                        continue
                    else:
                        user_info['university_degree'] = degree
                        break

                # Asking for GPA
                while True:
                    gpa = input("What Is Your GPA?\n>> ").strip()
                    # Validate GPA format
                    try:
                        gpa_float = float(gpa)
                        if 0.0 <= gpa_float <= 5.0:
                            if gpa_float.is_integer():
                                gpa_formatted = f"{int(gpa_float)}.0 GPA"
                            else:
                                gpa_formatted = f"{gpa_float} GPA"
                            user_info['university_gpa'] = gpa_formatted
                            break
                        else:
                            print("GPA Must Be Between 0.0 And 5.0. Please Try Again.")
                    except ValueError:
                        print("Invalid GPA Format. Please Enter A Numeric Value (e.g., 3.7).")
            else:
                user_info['university'] = ""
                user_info['university_grad_date'] = ""
                user_info['university_grad_label'] = ""
                user_info['university_degree'] = ""
                user_info['university_gpa'] = ""
    else:
        user_info['high_school'] = ""
        user_info['high_school_grad_date'] = ""
        user_info['high_school_grad_label'] = ""
        user_info['university'] = ""
        user_info['university_grad_date'] = ""
        user_info['university_grad_label'] = ""
        user_info['university_degree'] = ""
        user_info['university_gpa'] = ""
        
    # Asking for Skills
    print("\nList Your Skills. You must list at least 1. Type '0' When Finished")
    skills = []
    while True:
        skill = input(">> ").strip()
        if skill.lower() == "0":
            if len(skills) == 0:
                print("You Must Enter At Least One Skill.")
                continue
            else:
                break
        else:
            if skill == "":
                print("Skill Cannot Be Empty. Please Enter A Valid Skill Or Type '0' To Finish.")
                continue
            skills.append(skill)
    user_info['skills'] = skills

    # Asking for Achievements
    print("\nList Your Achievements. You must list at least 1. Type '0' When Finished")
    achievements = []
    while True:
        achievement = input(">> ").strip()
        if achievement.lower() == "0":
            if len(achievements) == 0:
                print("You Must Enter At Least One Achievement.")
                continue
            else:
                break
        else:
            if achievement == "":
                print("Achievement Cannot Be Empty. Please Enter A Valid Achievement Or Type '0' To Finish.")
                continue
            achievements.append(achievement)
            if len(achievements) >= 5:  # limit to prevent too many achievements, maybe we will change this later
                print("Achievement Limit Reached. We Will Move Onto The Next.")
                break
    user_info['achievements'] = achievements

    # Asking for Work Experience
    user_info['work_experience'] = []
    while True:
        print("\nEnter Your Past Job Experiences. Type '0' When Finished:")
        job_title = input(">> ").strip()
        if job_title.lower() == "0":
            break
        job = {'title': job_title}

        job_location_input = input("Where Was This Job Located?\n>> ").strip()
        job['location'] = ' '.join(word.capitalize() for word in job_location_input.split())
        
        # Validate Job Start Date is not in the future
        while True:
            job_start = input("What Was Your Start Date? (MM/YYYY).\n>> ").strip()
            if validate_date(job_start):
                parsed_start = parse_date(job_start)
                if parsed_start:
                    if parsed_start > current_date:
                        print("Start Date Cannot Be In The Future. Please Enter A Valid Start Date.")
                        continue
                    else:
                        job['start_date'] = format_date(job_start)
                        break
                else:
                    print("Invalid date. Please enter a valid date in MM/YYYY format.")
            else:
                print("Invalid date format. Please enter in MM/YYYY format.")
        
        # End Date Handling
        while True:
            job_end = input("What Was Your End Date? (MM/YYYY). Type 'Present' If You Are Still Working There.\n>> ").strip()
            if job_end.lower() == "present":
                job['end_date'] = "Present"
                break
            elif validate_date(job_end):
                parsed_end = parse_date(job_end)
                if parsed_end:
                    job['end_date'] = format_date(job_end)
                    break
                else:
                    print("Invalid date. Please enter a valid date in MM/YYYY format or type 'Present' to indicate ongoing employment.")
            else:
                print("Invalid input. Please enter a valid date in MM/YYYY format or type 'Present'.")

        description = generate_job_description(job_title)
        job['description'] = description

        user_info['work_experience'].append(job)

    return user_info

def generate_job_description(job_title):
    messages = [
        {
            "role": "system",
            "content": f"""
You Are A Professional Resume Generator. Your Task Is To Generate The Work Experience Description Part Of A Resume For Someone Who Is Applying For A Job.
Format What They Did At Their Job With "*" As Bullet Points. You Are Limited To Only Giving 3 Bullet Points.
You Are Generating It For {job_title}.
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

def add_divider(c, y_position, width, thickness=1):
    """
    Draws a horizontal line (divider) across the PDF.
    """
    c.setLineWidth(thickness)
    c.line(50, y_position, width - 50, y_position)
    return y_position - 11

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
        y_position -= 10
        y_position = add_divider(c, y_position, width)
        c.setFont("Helvetica", 12)
        if user_info.get('university'):
            uni_info = f"University: {user_info['university']}"
            if user_info.get('university_degree'):
                uni_info += f", {user_info['university_degree']}"
            if user_info.get('university_gpa'):
                uni_info += f", {user_info['university_gpa']}"
            if user_info.get('university_grad_date') and user_info.get('university_grad_label'):
                uni_info += f" ({user_info['university_grad_label']}: {user_info['university_grad_date']})"
            wrapped_uni_info = split_text(uni_info, width - 100, "Helvetica", 12)
            for line in wrapped_uni_info:
                if y_position < 50:
                    c.showPage()
                    y_position = height - 50
                c.drawString(60, y_position, line)
                y_position -= 15
        if user_info.get('high_school'):
            hs_info = f"High School: {user_info['high_school']}"
            if user_info.get('high_school_grad_date') and user_info.get('high_school_grad_label'):
                hs_info += f" ({user_info['high_school_grad_label']}: {user_info['high_school_grad_date']})"
            wrapped_hs_info = split_text(hs_info, width - 100, "Helvetica", 12)
            for line in wrapped_hs_info:
                if y_position < 50:
                    c.showPage()
                    y_position = height - 50
                c.drawString(60, y_position, line)
                y_position -= 15
        y_position -= 15

    # Work Experience
    if user_info['work_experience']:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, "Work Experience")
        y_position -= 10
        y_position = add_divider(c, y_position, width)
        for job in user_info['work_experience']:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(60, y_position, job['title'])
            y_position -= 15
            c.setFont("Helvetica", 12)
            job_dates = f"{job['location']} | {job['start_date']} - {job['end_date']}"
            wrapped_job_dates = split_text(job_dates, width - 120, "Helvetica", 12)
            for line in wrapped_job_dates:
                if y_position < 50:
                    c.showPage()
                    y_position = height - 50
                    c.setFont("Helvetica-Bold", 14)
                    c.drawString(50, y_position, "Work Experience")
                    y_position -= 10
                    y_position = add_divider(c, y_position, width)
                    c.setFont("Helvetica", 12)
                c.drawString(60, y_position, line)
                y_position -= 15
            c.setFont("Helvetica", 12)
            max_bullet_width = width - 100
            for bullet in job['description']:
                if y_position < 50:
                    c.showPage()
                    y_position = height - 50
                    c.setFont("Helvetica-Bold", 14)
                    c.drawString(50, y_position, "Work Experience")
                    y_position -= 10
                    y_position = add_divider(c, y_position, width)
                    c.setFont("Helvetica", 12)
                bullet_text = bullet.lstrip('* ').strip()
                wrapped_lines = split_text(bullet_text, max_bullet_width, "Helvetica", 12)
                if wrapped_lines:
                    # Use '-' for bullet points instead of *
                    c.drawString(70, y_position, f"- {wrapped_lines[0]}")
                    y_position -= 15
                    for line in wrapped_lines[1:]:
                        c.drawString(90, y_position, line)
                        y_position -= 15
            y_position -= 10

    # Skills
    if user_info['skills']:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, "Skills")
        y_position -= 10
        y_position = add_divider(c, y_position, width)
        c.setFont("Helvetica", 12)
        skills_text = ', '.join(user_info['skills'])
        wrapped_skills = split_text(skills_text, width - 100, "Helvetica", 12)
        for line in wrapped_skills:
            if y_position < 50:
                c.showPage()
                y_position = height - 50
                c.setFont("Helvetica-Bold", 14)
                c.drawString(50, y_position, "Skills")
                y_position -= 10
                y_position = add_divider(c, y_position, width)
                c.setFont("Helvetica", 12)
            c.drawString(60, y_position, line)
            y_position -= 15
        y_position -= 15

    # Achievements
    if user_info['achievements']:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, "Achievements")
        y_position -= 10
        y_position = add_divider(c, y_position, width)
        c.setFont("Helvetica", 12)
        for achievement in user_info['achievements']:
            if y_position < 50:
                c.showPage()
                y_position = height - 50
                c.setFont("Helvetica-Bold", 14)
                c.drawString(50, y_position, "Achievements")
                y_position -= 10
                y_position = add_divider(c, y_position, width)
                c.setFont("Helvetica", 12)
            wrapped_achievement = split_text(achievement, width - 100, "Helvetica", 12)
            if wrapped_achievement:
                c.drawString(60, y_position, f"- {wrapped_achievement[0]}")
                y_position -= 15
                for line in wrapped_achievement[1:]:
                    c.drawString(80, y_position, line)
                    y_position -= 15
        y_position -= 10

    # Save the PDF
    c.save()
    print("\nResume Generated Successfully As 'resume.pdf'.")

def main():
    user_info = collect_user_info()
    generate_pdf(user_info)

if __name__ == "__main__":
    main()
