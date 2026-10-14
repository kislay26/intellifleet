# Contribution Guidelines for IntelliFleet

## Antigravity Prompt to Resume Work

You can resume the development workflow exactly where we left off by entering the following prompt in Antigravity:
```
/plan
```
This will generate a concrete roadmap based on the current repository state and continue the automated workflow.

---

## Overview
This document outlines how you (or any teammate) can clone, set up, and contribute to the **IntelliFleet** repository safely.

### 1. Clone the repository
```bash
git clone https://github.com/kislay26/intellifleet.git
cd intellifleet
```

### 2. Create a personal branch
```bash
git checkout -b <your‑feature‑name>
```
Replace `<your‑feature‑name>` with a short, descriptive name (e.g., `add‑ci‑to‑cloud‑run`).

### 3. Install dependencies
#### Backend (Python)
```bash
python -m venv venv
# PowerShell
.\venv\Scripts\Activate.ps1
# Bash/CMD
source venv/Scripts/activate
pip install -r server/intellifleet/requirements.txt
```

#### Front‑end (React)
```bash
cd web
npm install
```

### 4. Configure environment variables
- **Never commit the real `.env` file** – it contains secret keys.
- Copy the template and fill in your own values:
```bash
cp .env.example .env
# Edit .env with your Gemini credentials, etc.
```
The repository’s `.gitignore` already excludes `.env`.

### 5. Run the services locally
#### Backend
```bash
cd server/intellifleet
uvicorn main:app --reload   # http://127.0.0.1:8000
```

#### Front‑end
```bash
cd ../../web
npm start   # http://localhost:3000
```

### 6. Run the test suite
```bash
cd ../server/intellifleet
pytest -q
```
All tests should pass (`8 passed`).

### 7. Commit & push
```bash
git add .
git commit -m "Add contribution guidelines"
git push origin <your‑feature‑name>
```

### 8. Open a Pull Request
- Go to the GitHub repo page, click **Pull requests → New pull request**.
- Select your branch as the source and `master` as the target.
- Add a clear title, description, and reference any related issue.
- Request a review from the repository owner.

### 9. Review & merge
- After approvals, the maintainer merges the PR.
- GitHub Actions will run CI automatically.

---

**Important security note**: The repository has *Push Protection* enabled; any commit containing secrets (e.g., the real `.env`) will be rejected. Always keep secrets out of the repo and use `.env.example` as a template.
