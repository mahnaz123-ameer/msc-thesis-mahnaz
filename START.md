# MSc Thesis App — Quick Start

## First Time Setup

### Backend
```bash
cd backend
pip install -r requirements.txt
```

### Frontend
```bash
cd frontend
npm install
```

---

## Run the App

Open **2 terminals**:

**Terminal 1 — Backend (FastAPI)**
```bash
cd backend
uvicorn main:app --reload
```
Runs at: http://localhost:8000

**Terminal 2 — Frontend (React + Vite)**
```bash
cd frontend
npm run dev
```
Runs at: http://localhost:5173

Open your browser at **http://localhost:5173**

---

## Pages

| Page | URL | What It Does |
|---|---|---|
| Dashboard | / | Thesis overview, project stats, related papers |
| Projects | /projects | Browse all 36 files and 557 functions |
| Run Functions | /runner | Run any function with real inputs |
| AST Analyzer | /ast | View AST trees and detect duplicate tests |
| Mutation Tester | /mutation | Validate test quality with mutation testing |

---

## Project Structure

```
thesis-app/
├── backend/
│   ├── main.py              ← FastAPI server (all endpoints)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx          ← Router + Layout
│   │   ├── api.js           ← All API calls
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── ProjectBrowser.jsx
│   │   │   ├── FunctionRunner.jsx
│   │   │   ├── ASTAnalyzer.jsx
│   │   │   └── MutationTester.jsx
│   │   └── index.css        ← Tailwind + custom styles
│   ├── .env                 ← API URL config
│   ├── vite.config.js
│   └── tailwind.config.js
└── research_projects/       ← Your 557 Python functions
    ├── 01_university_management/
    ├── 02_banking_system/
    ├── 03_hospital_management/
    ├── 04_ecommerce_system/
    └── 05_ride_sharing/
```
