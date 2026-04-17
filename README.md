# 🎯 Invigilator Allocation Management System

A robust **Django-based web application** designed to automate and streamline the allocation of invigilation duties for faculty during examinations. The system eliminates manual scheduling errors, ensures fairness, and improves operational efficiency in academic institutions.

---

## 🚀 Features

- 🔐 **User Authentication**
  - Secure login and registration system

- 👨‍🏫 **Faculty Dashboard**
  - View assigned invigilation duties
  - Download duty reports in PDF format

- 🧑‍💼 **HOD Dashboard**
  - View complete allocation data
  - Access analytics and generate reports

- ⚙️ **Automated Invigilator Allocation**
  - Intelligent assignment based on availability
  - Ensures fair and balanced distribution

- 📅 **Session-Based Scheduling**
  - Supports Forenoon and Afternoon sessions
  - Prevents duplicate assignments within the same session

- 🚫 **Absence Handling**
  - Excludes unavailable faculty during allocation

- 📄 **PDF Report Generation**
  - Individual faculty reports
  - Full allocation reports using ReportLab

---

## 🛠️ Tech Stack

- **Backend:** Django (Python)  
- **Frontend:** HTML, CSS, Bootstrap  
- **Database:** SQLite  
- **PDF Generation:** ReportLab  

---

## ⚡ System Workflow

1. **Admin creates exam schedule**
   - Defines date and session (Forenoon/Afternoon)

2. **Admin marks unavailable faculty**
   - Ensures accurate allocation

3. **System executes allocation algorithm**
   - Assigns invigilators to rooms/sessions

4. **Faculty access dashboard**
   - View and download assigned duties

5. **HOD generates reports**
   - Full allocation overview and analytics

---

## 🧠 Allocation Logic

The allocation system is designed to ensure **fairness, efficiency, and conflict-free scheduling**:

- Faculty are assigned based on **availability**
- Each session is processed **independently**
- The system ensures:
  - ❌ No duplicate assignment in the same session  
  - ⚖️ Balanced distribution of duties among faculty  
  - 🚫 No allocation for absent staff  

> The allocation follows a **sequential/rotational approach**, ensuring equal workload distribution across all available faculty members.

---

## 🗃️ Database Design

The system uses a relational database with key entities:

- **Faculty**
  - `id`, `name`, `availability_status`

- **Exam Schedule**
  - `id`, `date`, `session`, `room`

- **Allocation**
  - `faculty_id`, `exam_id`

---

## 📷 Screenshots

> *(Add screenshots here for better visualization)*  
- Login Page  
- Faculty Dashboard  
- HOD Dashboard  
- Allocation Results  
- PDF Reports  

---

## ▶️ Installation & Setup

Follow these steps to run the project locally:

# Clone the repository
git clone https://github.com/bhoomika-codes/invigilator-allocation-management-system.git

# Navigate to project directory
cd invigilator-allocation-management-system

# Create virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
venv\Scripts\activate   # On Windows
source venv/bin/activate  # On Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Run the development server
python manage.py runserver

## 👩‍💻 Author

**Bhoomika**  
- GitHub: https://github.com/bhoomika-codes  
- LinkedIn: *(Add your LinkedIn profile link here)*  

---

## 📄 License

This project is licensed under the **MIT License**.  
You are free to use, modify, and distribute this software with proper attribution.

---
