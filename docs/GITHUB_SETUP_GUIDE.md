# GitHub Setup, Upload & Team Collaboration Guide
## Smart Tourist Safety & Incident Response System

This guide outlines the exact Git workflow to initialize your repository, upload the database schemas and sample data to GitHub, and instruct teammates on how to clone and import everything.

---

## 1. Step-by-Step Instructions to Push to GitHub

### Step 1: Open Terminal in the Project Directory
Open PowerShell or Command Prompt and navigate to the project directory:
```bash
cd "C:\Users\NAVEENAMS\.gemini\antigravity\scratch\smart_tourist_safety_db"
```

### Step 2: Initialize Git Repository
```bash
git init
```

### Step 3: Create `.gitignore`
Ensure sensitive files, node modules, and environment configs are excluded:
```bash
# In the project root, create .gitignore:
node_modules/
.env
.DS_Store
*.log
```

### Step 4: Stage All Files
```bash
git add .
```

### Step 5: Commit Your Changes
```bash
git commit -m "feat: initial commit of Smart Tourist Safety dual MongoDB database schemas, sample datasets, and guides"
```

### Step 6: Create a New GitHub Repository
1. Log in to your [GitHub Account](https://github.com/).
2. Click **New Repository** (the `+` icon at the top right).
3. Set **Repository name**: `smart-tourist-safety-database` (or your preferred name).
4. Keep it **Public** or **Private** (according to your team's requirement).
5. Do **NOT** initialize with a README, .gitignore, or license (since we already created them).
6. Click **Create repository**.

### Step 7: Link Remote and Push
Copy your repository URL from GitHub (HTTPS or SSH) and run:
```bash
# Rename branch to main
git branch -M main

# Link to your remote GitHub repo (replace with your actual GitHub URL)
git remote add origin https://github.com/YOUR_USERNAME/smart-tourist-safety-database.git

# Push the code
git push -u origin main
```

---

## 2. Guidance for Teammates to Download & Import

Share these instructions with your project teammates:

### Step 1: Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/smart-tourist-safety-database.git
cd smart-tourist-safety-database
```

### Step 2: Option A - One-Click Import Using `mongosh` (Fastest)
If you have MongoDB Shell (`mongosh`) installed:
```bash
mongosh "mongodb://localhost:27017" scripts/seed_database.js
```
*This script will automatically create both `tourist_user_db` and `tourist_admin_db`, load all 21 collection JSON files, and build the required geospatial `2dsphere` indexes!*

### Step 3: Option B - Import via MongoDB Compass (Visual GUI)
If your teammates prefer using a graphic interface:
1. Open MongoDB Compass and connect to their local or Atlas MongoDB cluster.
2. Follow the detailed steps in [MONGODB_COMPASS_GUIDE.md](./MONGODB_COMPASS_GUIDE.md) to create the databases and import each JSON file.

### Step 4: Verify Database Health
Run the validation script using Node.js:
```bash
node scripts/validate_schemas.js
```
Expected output:
```
[PASS] tourist_user_db: 11 collections validated
[PASS] tourist_admin_db: 10 collections validated
[PASS] All GeoJSON coordinates and cross-database references valid!
```

---

## 3. Security & Zero-PII Policy

> [!CAUTION]
> **Zero Real PII in Git Repository:**
> * Never commit real Aadhaar numbers, Passport numbers, phone numbers, or passwords.
> * All dataset files in this repository use strictly masked test data (e.g. `XXXXXXXX9481`, mock bcrypt hashes).
> * If adding new sample documents, ensure they comply with this privacy standard before running `git commit`.
