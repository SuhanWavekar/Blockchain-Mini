# 🔗 CertChain — Blockchain Certificate Verification System

A full-featured web application that demonstrates blockchain technology by issuing, verifying, and managing digital certificates. Built with Python, Flask, and SHA-256 hashing, this project showcases core blockchain concepts including **proof of work mining**, **hash chaining**, **tamper detection**, and **chain integrity verification**.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Usage](#-usage)
- [Pages & Routes](#-pages--routes)
- [REST API](#-rest-api)
- [Blockchain Concepts](#-blockchain-concepts-demonstrated)
- [Screenshots](#-screenshots)
- [Contributing](#-contributing)

---

## ✨ Features

### Core Blockchain
- **SHA-256 Hash Chaining** — Each block's hash depends on the previous block, creating an immutable chain
- **Proof of Work Mining** — Blocks are mined by finding a nonce that produces a hash with leading zeros (configurable difficulty)
- **Tamper Detection** — Any modification to a block invalidates it and all subsequent blocks
- **Chain Integrity Verification** — Full chain validation checking hashes, links, and indices

### Certificate Management
- **Issue Certificates** — Create blockchain-verified digital certificates with student name, course, and institution
- **Verify Certificates** — Look up any certificate by its UUID and confirm authenticity
- **PDF Download** — Generate styled PDF certificates with QR codes and blockchain verification stamps
- **QR Code Generation** — Each certificate gets a scannable QR code for instant verification

### Dashboard & Analytics
- **Statistics Dashboard** — Total blocks, certificates issued, chain health status
- **Charts** — Certificates over time (line chart) and per-institution distribution (bar chart)
- **Recent Activity** — Table showing the latest issued certificates with quick actions

### Educational Tools
- **Interactive Tamper Demo** — Modify block data in-browser and watch the chain break in real-time
- **Block-by-Block Integrity Report** — Detailed per-block hash, link, and index verification results
- **Blockchain Explorer** — Browse all blocks with search and filter functionality

### Technical
- **REST API** — JSON endpoints for programmatic access (`/api/chain`, `/api/issue`, `/api/verify`, `/api/stats`)
- **Responsive Design** — Works on desktop and mobile with a collapsible sidebar
- **Persistent Storage** — Blockchain data stored in `blockchain.json` (no database required)

---

## 🛠 Tech Stack

| Component        | Technology                                    |
|------------------|-----------------------------------------------|
| **Backend**      | Python 3.10+, Flask 3.1                       |
| **Hashing**      | SHA-256 (hashlib)                             |
| **PDF Generation**| ReportLab                                    |
| **QR Codes**     | qrcode + Pillow                               |
| **Frontend**     | HTML5, CSS3, Jinja2 Templates                 |
| **Charts**       | Chart.js (CDN)                                |
| **Icons**        | Font Awesome 6 (CDN)                          |
| **Font**         | Inter (Google Fonts)                          |
| **Storage**      | JSON file (`blockchain.json`)                 |

---

## 📁 Project Structure

```
Blockchain mini1/
├── app.py                  # Flask application with all routes and blockchain logic
├── blockchain.json         # Persistent blockchain data storage
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── static/
│   └── style.css           # Complete stylesheet (dark sidebar theme)
├── templates/
│   ├── base.html           # Base layout with sidebar navigation
│   ├── dashboard.html      # Stats, charts, and recent activity
│   ├── issue.html          # Certificate issuance form
│   ├── verify.html         # Certificate verification lookup
│   ├── explorer.html       # Blockchain explorer with search
│   ├── integrity.html      # Chain integrity verification report
│   └── tamper_demo.html    # Interactive tamper detection demo
└── venv/                   # Python virtual environment (auto-generated)
```

---

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Steps

1. **Clone or download the project**
   ```bash
   cd "Blockchain mini1"
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**

   - **Windows (PowerShell):**
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **Windows (CMD):**
     ```cmd
     venv\Scripts\activate.bat
     ```
   - **macOS / Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open in browser**
   ```
   http://127.0.0.1:5000
   ```

> **Note:** On first run, if `blockchain.json` does not exist, a genesis block will be automatically created and mined.

---

## 📖 Usage

### Issuing a Certificate
1. Navigate to the **Issue** page from the sidebar
2. Fill in the student name, course/degree, and institution
3. Click **Issue Certificate**
4. The system mines a new block (proof of work) and adds it to the chain
5. Download the **PDF certificate** or view the **QR code**

### Verifying a Certificate
1. Navigate to the **Verify** page
2. Paste the certificate UUID (e.g., `2EE0AA06-C672-483D-908A-F20FDD64479C`)
3. Click **Verify Certificate**
4. The system checks if the certificate exists and validates the entire chain integrity

### Exploring the Blockchain
1. Navigate to the **Explorer** page
2. Browse all blocks in the chain with their hashes and data
3. Use the search bar to filter by student name, course, institution, or certificate ID

### Checking Integrity
1. Navigate to the **Integrity** page
2. View the overall chain status and per-block verification details
3. Each block shows pass/fail for hash check, link check, and index check

### Tamper Detection Demo
1. Navigate to the **Tamper Demo** page
2. Select a block and a field to modify
3. Enter a new value and click **Tamper Block**
4. Watch how the modified block's hash changes, breaking the chain
5. Click **Reset Chain** to restore the original data

---

## 🌐 Pages & Routes

| Page            | URL             | Method | Description                          |
|-----------------|-----------------|--------|--------------------------------------|
| Dashboard       | `/`             | GET    | Stats, charts, recent certificates   |
| Issue Page      | `/issue`        | GET    | Certificate issuance form            |
| Issue Action    | `/issue`        | POST   | Process certificate issuance         |
| Verify Page     | `/verify`       | GET    | Certificate verification form        |
| Verify Action   | `/verify`       | POST   | Process certificate verification     |
| Explorer        | `/explorer`     | GET    | Blockchain explorer with search      |
| Integrity       | `/integrity`    | GET    | Chain integrity verification         |
| Tamper Demo     | `/tamper-demo`  | GET    | Interactive tamper detection demo     |
| PDF Download    | `/certificate/<id>/pdf` | GET | Download certificate as PDF   |
| QR Code         | `/certificate/<id>/qr`  | GET | View certificate QR code      |

---

## 🔌 REST API

All API endpoints return JSON responses.

### `GET /api/chain`
Returns the complete blockchain.

**Response:**
```json
[
  {
    "index": 0,
    "timestamp": "2026-10-05T08:39:19+00:00",
    "data": { "message": "Genesis Block" },
    "previous_hash": "0",
    "nonce": 42,
    "hash": "00a3f...",
    "mining_time": 0.0012
  },
  ...
]
```

### `POST /api/issue`
Issue a new certificate.

**Request Body:**
```json
{
  "student_name": "Rahul Sharma",
  "course": "B.E. Computer Engineering",
  "institution": "ABC College"
}
```

**Response (201):**
```json
{
  "certificate": {
    "certificate_id": "2EE0AA06-C672-483D-908A-F20FDD64479C",
    "student_name": "Rahul Sharma",
    "course": "B.E. Computer Engineering",
    "institution": "ABC College",
    "issue_date": "2026-10-05T08:42:02+00:00"
  },
  "block_index": 1
}
```

### `GET /api/verify/<certificate_id>`
Verify a certificate by its ID.

**Response (200):**
```json
{
  "status": "VERIFIED",
  "message": "All blocks and hash links are valid.",
  "certificate": { ... },
  "block": { ... }
}
```

### `GET /api/stats`
Get blockchain statistics.

**Response:**
```json
{
  "total_blocks": 4,
  "total_certificates": 3,
  "chain_valid": true,
  "chain_message": "All blocks and hash links are valid.",
  "last_block_time": "2026-10-05T18:06:05+00:00",
  "institutions": { "ABC College": 1, "MIT": 2 },
  "timeline": { "2026-10-05": 3 }
}
```

---

## 🧠 Blockchain Concepts Demonstrated

### 1. Hash Function (SHA-256)
Each block's data is serialized and hashed using SHA-256, producing a unique 64-character hexadecimal fingerprint. Any change in the data produces a completely different hash.

### 2. Hash Chaining
Every block stores the hash of the previous block in its `previous_hash` field. This creates a linked chain where altering any block invalidates all subsequent blocks.

### 3. Proof of Work (Mining)
Before a block is added to the chain, a **nonce** (number) must be found such that the block's hash starts with a certain number of leading zeros (determined by the `DIFFICULTY` setting). This computationally expensive process is what makes blockchains secure.

```
Difficulty = 2 → Hash must start with "00..."
Difficulty = 3 → Hash must start with "000..."
```

### 4. Immutability
Once a block is mined and added to the chain, its data cannot be changed without:
- Recalculating the hash of the modified block
- Recalculating the hashes of ALL subsequent blocks
- Re-mining ALL subsequent blocks (proof of work)

This makes tampering computationally infeasible on real blockchains.

### 5. Verification
The chain can be verified by:
- Recalculating each block's hash and comparing it to the stored hash
- Checking that each block's `previous_hash` matches the prior block's `hash`
- Validating that block indices are sequential

---

## 🤝 Contributing

This is an educational mini project. Contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m "Add new feature"`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

---

## 📄 License

This project is for educational purposes. Feel free to use and modify.

---

<p align="center">
  <strong>Built with ❤️ using Python, Flask & SHA-256</strong><br>
  <em>Educational Mini Project — Blockchain Certificate Verification</em>
</p>
