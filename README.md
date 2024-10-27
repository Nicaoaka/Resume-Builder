# 📝 AI Resume Builder

AI Resume Builder is a web application that guides users through creating a professional resume using a chatbot interface. The application collects user input, generates a resume, and exports it as a PDF file. Flask powers the backend, while the frontend uses HTML, CSS, and JavaScript for a seamless user experience.

## ✨ Features

- **Interactive Chatbot Interface**: Guide users through inputting essential resume details step-by-step.
- **Automated PDF Generation**: Generate professional resumes based on user input.
- **Validation**: Input validation for email, phone numbers, and dates.
- **Easy Navigation**: Simple and intuitive UI for easy interaction.
- **Pre-Designed Templates**: Stylish and clean templates for a polished resume.
- **Supports Multiple Job Experiences and Skills**: Users can add multiple job entries and skills.

## 📂 Project Structure

```plaintext
.
├── static/
│   ├── index.html          # Frontend HTML file
│   ├── style.css           # Styling for the chat interface
│   ├── script.js           # JavaScript for managing chat interaction
├── flask_resume_builder.py # Main backend script using Flask
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
```

## 🚀 Getting Started

### 🛠 Prerequisites

- **Python 3.x**: Ensure Python is installed.
- **Flask**: Backend framework for running the application.
- **ReportLab**: For generating PDF files.
- **InferenceClient**: For AI-driven job description generation.

### 🔧 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Nicaoaka/Resume-Builder.git
   cd ai-resume-builder
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API Key**:
   - Get an API key from the required inference service.
   - Add it to your environment variables:
HuggingFace provides the API key. Make a HuggingFace Account and generate a token for full use.
     ```bash
     export HF_API_KEY="your_api_key_here"
     ```

4. **Run the application**:
   ```bash
   python flask_resume_builder.py
   ```

5. **Access the application**:
   - Open your web browser and navigate to: `http://127.0.0.1:5000/`

## 💡 Usage

1. Open the application in your browser.
2. Start by sending any message in the chat interface.
3. Follow the chatbot's prompts to input your details.
4. Once completed, the chatbot will generate your resume and provide a download link.

## 📄 Files

### 🖥 Backend

- **`flask_resume_builder.py`**:
  - Handles the chatbot interaction and PDF generation.
  - Includes helper functions for validation and formatting.
  - Uses an AI inference client to generate job descriptions.

### 🎨 Frontend

- **`index.html`**: 
  - The main structure of the chat interface.
- **`style.css`**:
  - Styling for a clean and modern user interface.
- **`script.js`**:
  - Manages user interactions and sends messages to the backend.

## 🤝 Contributing

Feel free to fork this project and submit pull requests. Contributions are welcome! The project is submitted as is for a hackathon.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
