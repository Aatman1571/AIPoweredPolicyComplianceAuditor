# AI-Powered Policy Compliance Auditor

> An NLP and Large Language Model–powered tool for automated cybersecurity policy compliance auditing against ISO 27001, NIST 800-53, and CIS Controls.

---

## 📌 Overview
The **AI-Powered Policy Compliance Auditor** automates the traditionally manual process of auditing security policies.  
By leveraging **Natural Language Processing (NLP)** and **Large Language Models (LLMs)**, the tool can:
- Parse security policy documents (DOCX, PDF, TXT)
- Map extracted clauses to compliance controls
- Detect gaps and missing coverage
- Score compliance levels
- Suggest AI-generated remediation steps

This solution improves audit speed, accuracy, and scalability — helping organizations stay continuously audit-ready.

---

## ⚡ Features
- **Multi-Framework Compliance** — ISO 27001, NIST 800-53, and CIS Controls.
- **Automated NLP Parsing** — Extracts control-relevant terms from policies.
- **AI Gap Analysis** — Identifies missing or incomplete controls using GPT-4/Gemini.
- **Compliance Scoring** — Provides document-level and control-level compliance percentages.
- **Remediation Suggestions** — Generates actionable text to address gaps.
- **Prototype Dashboard** — Displays scores, gaps and recommendations.
- **Multi-format Support** — Works with DOCX, PDF, and TXT policy documents.

---

## 🛠 Tech Stack
- **Language**: Python  
- **Frameworks/Libraries**: spaCy, Flask, Streamlit, PyPDF2
- **AI Models**: Google Gemini API  


---

## 📂 Repository Structure
```
├── controls/                  # JSON control definitions for compliance frameworks
├── output/                    # JSON reports generated after analysis
├── policies/                  # Source cybersecurity policy documents
├── processed/                 # Preprocessed text versions of policies
├── scripts/                   # Core application scripts
└── dashboard_uploads/         # Documents uploaded via dashboard UI
```

---

## 🚀 Getting Started

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Aatman1571/AIPoweredPolicyComplianceAuditor.git
cd AIPoweredPolicyComplianceAuditor
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Set API Keys
Create a `.env` file:
```
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
```

### 4️⃣ Launch Dashboard
```bash
streamlit -m run scripts/dashboard.py
```

---

## 📊 Example Output

### **Upload and Audit Execution**
<img width="975" height="548" alt="image" src="https://github.com/user-attachments/assets/5ac2fcc2-6304-43ab-b5ed-2b3a3a5dd2c6" />

### **Compliance Overview**
<img width="975" height="440" alt="image" src="https://github.com/user-attachments/assets/f15c9170-6226-46d5-af7e-0df305af9643" />

### **Remediation Suggestions**
<img width="975" height="442" alt="image" src="https://github.com/user-attachments/assets/2a8709e5-2be4-4497-8367-c432a0d53728" />

### **Matched Controls**
<img width="975" height="439" alt="image" src="https://github.com/user-attachments/assets/5ecf3d1c-14fe-48e2-aa83-c6092211f087" />
<img width="867" height="487" alt="image" src="https://github.com/user-attachments/assets/ae0b29c5-dac6-4133-b343-f1a2f26f7869" />

### **Gap Analysis**
<img width="975" height="548" alt="image" src="https://github.com/user-attachments/assets/c9198835-1490-4ba0-b8e7-bf7283e15563" />

### **Compliance Score**
<img width="975" height="548" alt="image" src="https://github.com/user-attachments/assets/f44f05b3-64bc-4ee2-afee-97b1b225d74e" />

### **PDF Audit Report**
<img width="975" height="548" alt="image" src="https://github.com/user-attachments/assets/779ba169-eeb5-44c6-8bd9-fd290ce03658" />


---

## 📈 Roadmap
- [ ] Add support for HIPAA, PCI-DSS, and GDPR.
- [ ] Real-time regulatory framework updates.
- [ ] Version control for policy changes.
- [ ] Enterprise GRC platform integration.
- [ ] Multi-language policy analysis.

---

## 📜 License
This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Authors
- Aatman Dilipkumar Shah  
- Parth Hareshbhai Kakadiya  
- Pruthvesh Mahendrakumar Prajapati  
- Shivam Satishkumar Patel  
- Tirth Patel  
