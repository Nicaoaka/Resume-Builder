import re
import os
from huggingface_hub import InferenceClient
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
from flask import Flask, request, jsonify, session, send_file, send_from_directory
from flask_session import Session

app = Flask(__name__, static_folder='static', static_url_path='/static')

app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Initialize Inference Client
API_KEY = os.getenv("HF_API_KEY", "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")
client = InferenceClient(api_key=API_KEY)

# Helper Functions

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

def generate_job_description(job_title):
    messages = [
        {
            "role": "system",
            "content": f"""
You are a professional Resume Generator. Your task is to generate the work experience description part of a resume for someone who held the position of {job_title}.
Format the responsibilities and achievements with "*" as bullet points. Limit to only giving 3 bullet points.
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
    if user_info.get('email'):
        contact_info += f"Email: {user_info['email']}  "
    if user_info.get('phone'):
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
    if user_info.get('work_experience'):
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
            for bullet in job.get('description', []):
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
    if user_info.get('skills'):
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
    if user_info.get('achievements'):
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

# Conversation Steps Definition
CONVERSATION_STEPS = [
    "full_name",
    "email",
    "phone",
    "high_school",
    "high_school_grad_date",
    "university",
    "university_grad_date",
    "university_degree",
    "university_gpa",
    "skills",
    "achievements",
    "work_experience"
]

def initialize_user_session():
    session['step'] = 0
    session['user_info'] = {}
    session['work_experience'] = []
    session['skills'] = []
    session['achievements'] = []

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

@app.route('/chat', methods=['POST'])
def chat():
    if 'step' not in session:
        initialize_user_session()
    
    data = request.get_json()
    user_message = data.get('message', '').strip()
    
    # Current step
    step = session.get('step', 0)
    user_info = session.get('user_info', {})
    
    response = ""
    
    try:
        if step == 0:
            # Greeting and ask for full name
            response = "Hello! I'm your Resume Builder AI. Let's get started. What's your full name?"
            session['step'] = 1
        elif step == 1:
            # Receive full name
            user_info['full_name'] = user_message
            response = "Great! What's your email address? (Type '0' to skip)"
            session['step'] = 2
        elif step == 2:
            # Receive email
            if validate_email(user_message):
                user_info['email'] = user_message if user_message != "0" else ""
                response = "Got it. What's your phone number? (Type '0' to skip)"
                session['step'] = 3
            else:
                response = "That doesn't look like a valid email. Please enter a valid email address or type '0' to skip."
        elif step == 3:
            # Receive phone number
            if validate_phone(user_message):
                user_info['phone'] = format_phone(user_message) if user_message != "0" else ""
                response = "Please enter the name of your high school:"
                session['step'] = 4
            else:
                response = "That doesn't look like a valid phone number. Please enter a valid phone number or type '0' to skip."
        elif step == 4:
            # Receive high school name
            user_info['high_school'] = capitalize_words(user_message) if user_message != "" else ""
            if user_info['high_school']:
                response = "What's your high school graduation date? (MM/YYYY)"
                session['step'] = 5
            else:
                # Skip to university if high school is skipped
                response = "Skipping high school information. Please enter the name of your university:"
                session['step'] = 6
        elif step == 5:
            # Receive high school graduation date
            if validate_date(user_message):
                user_info['high_school_grad_date'] = format_date(user_message)
                user_info['high_school_grad_label'] = "Graduation Date" if parse_date(user_message) <= datetime.now() else "Expected Graduation Date"
                response = "Please enter the name of your university (or type '0' to skip):"
                session['step'] = 6
            else:
                response = "Invalid date format. Please enter the graduation date in MM/YYYY format."
        elif step == 6:
            # Receive university name
            if user_message != "0":
                user_info['university'] = capitalize_words(user_message, exceptions=["of"])
                response = "What's your university graduation date? (MM/YYYY or type '0' to skip)"
                session['step'] = 7
            else:
                user_info['university'] = ""
                user_info['university_grad_date'] = ""
                user_info['university_grad_label'] = ""
                user_info['university_degree'] = ""
                user_info['university_gpa'] = ""
                response = "Please list one of your skills (type 'done' when finished):"
                session['step'] = 9
        elif step == 7:
            # Receive university graduation date
            if user_message.lower() == '0':
                user_info['university_grad_date'] = ""
                user_info['university_grad_label'] = ""
                response = "Please enter your degree (e.g., Bachelor of Science in Computer Science):"
                session['step'] = 8
            elif validate_date(user_message):
                user_info['university_grad_date'] = format_date(user_message)
                user_info['university_grad_label'] = "Graduation Date" if parse_date(user_message) <= datetime.now() else "Expected Graduation Date"
                response = "Please enter your degree (e.g., Bachelor of Science in Computer Science):"
                session['step'] = 8
            else:
                response = "Invalid date format. Please enter the graduation date in MM/YYYY format or type '0' to skip."
        elif step == 8:
            # Receive degree
            if user_message != "":
                user_info['university_degree'] = user_message
                response = "What's your GPA? (Type '0' to skip)"
                session['step'] = 9
            else:
                response = "Degree cannot be empty. Please enter your degree:"
        elif step == 9:
            # Receive GPA
            if user_message == "0":
                user_info['university_gpa'] = ""
            else:
                try:
                    gpa_float = float(user_message)
                    if 0.0 <= gpa_float <= 5.0:
                        user_info['university_gpa'] = f"{gpa_float} GPA" if not gpa_float.is_integer() else f"{int(gpa_float)}.0 GPA"
                    else:
                        response = "GPA must be between 0.0 and 5.0. Please enter a valid GPA or type '0' to skip."
                        return jsonify({"message": response})
                except ValueError:
                    response = "Invalid GPA format. Please enter a numeric value (e.g., 3.7) or type '0' to skip."
                    return jsonify({"message": response})
            
            # Proceed to skills
            response = "Please list one of your skills (type 'done' when finished):"
            session['step'] = 10
        elif step == 10:
            # Receive skills
            if user_message.lower() == 'done':
                if not session['skills']:
                    response = "You must enter at least one skill. Please enter a skill:"
                else:
                    user_info['skills'] = session['skills']
                    response = "Please list one of your achievements (type 'done' when finished):"
                    session['step'] = 11
            else:
                session['skills'].append(user_message)
                response = "Skill added. Please enter another skill or type 'done' to finish:"
        elif step == 11:
            # Receive achievements
            if user_message.lower() == 'done':
                if not session['achievements']:
                    response = "You must enter at least one achievement. Please enter an achievement:"
                else:
                    response = "Let's add your work experience. Please enter your job title (or type 'done' to finish):"
                    session['step'] = 12
            else:
                session['achievements'].append(user_message)
                response = "Achievement added. Please enter another achievement or type 'done' to finish:"
        elif step == 12:
            # Receive work experience
            if user_message.lower() == 'done':
                # All information collected, generate resume
                user_info['skills'] = session['skills']
                user_info['achievements'] = session['achievements']
                user_info['work_experience'] = session['work_experience']
                
                # Generate PDF
                generate_pdf(user_info)
                
                response = "Your resume has been generated successfully! You can download it <a href='/download_resume' target='_blank'> download it here</a>."
                session.clear()
            else:
                job = {'title': user_message}
                response = "Where was this job located?"
                session['current_job'] = job
                session['step'] = 13
        elif step == 13:
            # Receive job location
            current_job = session.get('current_job', {})
            current_job['location'] = ' '.join(word.capitalize() for word in user_message.split())
            session['current_job'] = current_job
            response = "What was your start date? (MM/YYYY)"
            session['step'] = 14
        elif step == 14:
            # Receive job start date
            if validate_date(user_message):
                parsed_start = parse_date(user_message)
                if parsed_start and parsed_start > datetime.now():
                    response = "Start date cannot be in the future. Please enter a valid start date (MM/YYYY):"
                else:
                    current_job = session.get('current_job', {})
                    current_job['start_date'] = format_date(user_message)
                    session['current_job'] = current_job
                    response = "What was your end date? (MM/YYYY) or type 'Present' if you're still working there:"
                    session['step'] = 15
            else:
                response = "Invalid date format. Please enter the start date in MM/YYYY format:"
        elif step == 15:
            # Receive job end date
            if user_message.lower() == 'present':
                current_job = session.get('current_job', {})
                current_job['end_date'] = "Present"
                session['current_job'] = current_job
            elif validate_date(user_message):
                current_job = session.get('current_job', {})
                current_job['end_date'] = format_date(user_message)
                session['current_job'] = current_job
            else:
                response = "Invalid input. Please enter the end date in MM/YYYY format or type 'Present':"
                return jsonify({"message": response})
            
            # Generate job description using Inference Client
            job_title = session['current_job']['title']
            description = generate_job_description(job_title)
            session['current_job']['description'] = description
            session['work_experience'].append(session['current_job'])
            session.pop('current_job', None)
            
            response = "Job experience added. Please enter another job title or type 'done' to finish:"
            session['step'] = 12
        else:
            response = "I'm not sure how to help with that. Let's start over. What's your full name?"
            initialize_user_session()
        
        # Update session data
        session['user_info'] = user_info
        return jsonify({"message": response})
    except Exception as e:
        print(f"Error: {e}")
        response = "An error occurred while processing your request. Please try again."
        return jsonify({"message": response}), 500

@app.route('/download_resume', methods=['GET'])
def download_resume():
    try:
        return send_file("resume.pdf", as_attachment=True)
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    app.run(debug=False)
