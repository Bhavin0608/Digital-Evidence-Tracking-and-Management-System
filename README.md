<p align="center">
  <img src="https://img.shields.io/badge/Django-6.0.2-0B132B?style=for-the-badge&logo=django&logoColor=5BC0BE" />
  <img src="https://img.shields.io/badge/Python-3.14-0B132B?style=for-the-badge&logo=python&logoColor=5BC0BE" />
  <img src="https://img.shields.io/badge/PostgreSQL-16-0B132B?style=for-the-badge&logo=postgresql&logoColor=5BC0BE" />
  <img src="https://img.shields.io/badge/License-MIT-0B132B?style=for-the-badge&logoColor=5BC0BE" />
</p>

<h1 align="center">DETAMS</h1>
<h3 align="center">Digital Evidence Tracking & Management System</h3>

<p align="center">
  A secure, role-based web application for managing digital forensic evidence<br/>
  with SHA-256 integrity verification and an immutable chain of custody.
</p>

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [User Roles](#user-roles)
- [System Workflow](#system-workflow)
- [Data Models](#data-models)
- [Installation & Setup](#installation--setup)
- [URL Reference](#url-reference)
- [Security](#security)
- [Project Structure](#project-structure)
- [Screenshots](#screenshots)

---

## Overview

**DETAMS** is a web-based forensic evidence management platform designed for law enforcement agencies. It provides a secure, auditable environment for managing digital evidence throughout its entire lifecycle — from collection to case closure.

The system enforces strict role-based access control across four user roles, guarantees evidence integrity through SHA-256 cryptographic hashing, and maintains a tamper-proof audit trail via immutable custody log records.

---

## Key Features

| Category | Features |
|---|---|
| **Evidence Management** | Secure upload with automatic SHA-256 hashing, preview, download, verification |
| **Chain of Custody** | Immutable `CustodyLog` records — cannot be edited or deleted once created |
| **Integrity Verification** | Bulk & individual SHA-256 re-verification to detect file tampering |
| **Role-Based Access** | 4 roles (Admin, Senior Officer, Investigator, Auditor) with strict access boundaries |
| **Case Lifecycle** | Full workflow: OPEN → IN_PROGRESS → PENDING_CLOSURE → CLOSED |
| **Audit & Compliance** | Custody timeline, integrity console, printable compliance reports |
| **Observations** | Investigators can attach notes/comments to individual evidence items |
| **Admin Dashboard** | Custom dashboard with real-time stats, quick actions, and activity feed |
| **Design System** | Unified dark glassmorphism UI with cyan accents across all pages |

---

## Tech Stack

| Component | Technology |
|---|---|
| Backend | Django 6.0.2 |
| Language | Python 3.14 |
| Database | PostgreSQL |
| DB Adapter | psycopg2 2.9.11 |
| Frontend | Django Templates, HTML5, CSS3, JavaScript |
| Hashing | hashlib (SHA-256) |
| File Storage | Django FileField (local `media/evidence_files/`) |
| Auth | Django built-in authentication + session management |

---

## Architecture

The project is organized into **5 Django apps**, each handling a distinct domain:

```
┌─────────────────────────────────────────────────────────┐
│                      DETAMS                             │
├──────────┬──────────┬──────────┬──────────┬─────────────┤
│  users   │  cases   │ evidence │ custody  │    core     │
│          │          │          │          │             │
│ Auth     │ Case     │ Upload   │ Custody  │ HashService │
│ Profiles │ Lifecycle│ SHA-256  │ Log      │ RBACService │
│ Dash-    │ Members  │ Notes    │ Timeline │ Admin Site  │
│ boards   │ Closure  │ Verify   │ Reports  │             │
└──────────┴──────────┴──────────┴──────────┴─────────────┘
```

| App | Responsibility |
|---|---|
| `users` | Authentication, role-based dashboards, SO actions, profile management |
| `cases` | Case CRUD, case detail, closure requests, case note updates |
| `evidence` | Evidence upload with SHA-256, observations/notes, preview, download, verify |
| `custody` | Immutable audit trail, auditor pages (timeline, integrity console, reports) |
| `core` | Shared services — `HashService`, `RBACService`, custom `DETAMSAdminSite` |

---

## User Roles

### 1. Administrator
- **Access**: Custom admin dashboard at `/admin/`
- **Capabilities**: Create users/officers, create cases, assign Senior Officers, close cases, view all audit logs
- **Blocked from**: All user-facing pages (forced to use admin panel)

### 2. Senior Officer
- **Access**: SO Dashboard at `/dashboard/so/`
- **Capabilities**: Assign investigators to cases, monitor case progress (evidence + timeline), request case closure

### 3. Investigator
- **Access**: Investigator Dashboard at `/dashboard/investigator/`
- **Capabilities**: Upload evidence (auto SHA-256), add observations/notes, update case notes, view/preview/download/verify evidence

### 4. Auditor
- **Access**: Auditor Dashboard at `/dashboard/auditor/`
- **Capabilities**: View custody timeline, run bulk integrity scans, generate printable compliance reports
- **Note**: Read-only access to ALL cases

---

## System Workflow

```
   ADMIN                  SENIOR OFFICER           INVESTIGATOR              AUDITOR
     │                         │                        │                       │
     ├─ Create Officers        │                        │                       │
     ├─ Create Case ───────────┤                        │                       │
     ├─ Assign SO ─────────────┤                        │                       │
     │                         ├─ Assign Investigators ─┤                       │
     │                         ├─ Monitor Progress      │                       │
     │                         │                        ├─ Upload Evidence       │
     │                         │                        ├─ Add Observations      │
     │                         │                        ├─ Update Case Notes     │
     │                         │                        ├─ Verify Evidence       │
     │                         │                        │                       │
     │                         │                        │           ┌───────────┤
     │                         │                        │           │ Timeline  │
     │                         │                        │           │ Integrity │
     │                         │                        │           │ Reports   │
     │                         │                        │           └───────────┘
     │                         ├─ Request Closure       │                       │
     ├─ Close Case (FINAL) ◄───┤                        │                       │
     │                         │                        │                       │
     ▼                         ▼                        ▼                       ▼
              ═══════ ALL ACTIONS LOGGED TO CustodyLog (IMMUTABLE) ═══════
```

### Phase Breakdown

| Phase | Actor | Actions | Output |
|---|---|---|---|
| **1. Setup** | Admin | Create users, cases, assign SO | User + UserProfile, Case (OPEN) |
| **2. Management** | Senior Officer | Assign investigators, monitor progress | CaseMember entries |
| **3. Investigation** | Investigator | Upload evidence, add notes, verify files | Evidence + SHA-256, EvidenceNote, CustodyLog |
| **4. Audit** | Auditor | Timeline, integrity scan, generate report | Verification results, compliance report |
| **5. Closure** | SO → Admin | Request closure → close case | Case (CLOSED), final CustodyLog |

---

## Data Models

### Entity Relationship

```
User (Django Auth)
 └── UserProfile (1:1)  ─── role, dob, gender, badge_number, department

Case
 ├── created_by  → User (Admin)
 ├── assigned_so → User (Senior Officer)
 ├── CaseMember (M2M) → User (Investigators)
 ├── Evidence[] (1:N)
 │    ├── file, file_name, description, sha256_hash
 │    ├── uploaded_by → User
 │    └── EvidenceNote[] (1:N)
 │         ├── author → User
 │         └── content, created_at
 └── CustodyLog[] (1:N)  ← IMMUTABLE
      ├── evidence → Evidence (nullable)
      ├── performed_by → User
      ├── action_type (10 types)
      └── remarks, timestamp
```

### Models Summary

| Model | App | Key Fields | Notes |
|---|---|---|---|
| `UserProfile` | users | role, dob, gender, badge_number, department | 1:1 with Django User |
| `Case` | cases | case_id, title, description, category, priority, status | 8 categories, 4 statuses |
| `CaseMember` | cases | case, user, assigned_at | unique_together constraint |
| `Evidence` | evidence | file, sha256_hash, description, file_type, file_size | Hash is non-editable |
| `EvidenceNote` | evidence | evidence, author, content | Observation/comment on evidence |
| `CustodyLog` | custody | case, evidence, performed_by, action_type, remarks | **Immutable** — save() blocks updates |

### CustodyLog Action Types

| Action | Trigger |
|---|---|
| `UPLOAD` | Investigator uploads evidence |
| `PREVIEW` | User previews evidence inline |
| `COMMENT` | Investigator adds observation note |
| `VIEW` | User views evidence detail page |
| `VERIFY` | SHA-256 integrity check performed |
| `DOWNLOAD` | User downloads evidence file |
| `INVESTIGATOR_ASSIGNED` | SO assigns investigator to case |
| `CASE_UPDATE` | Investigator updates case notes |
| `CLOSURE_REQUEST` | SO requests case closure |
| `CASE_CLOSED` | Admin closes the case |

---

## Installation & Setup

### Prerequisites

- Python 3.12+
- PostgreSQL 14+
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/Digital-Evidence-Tracking-and-Management-System.git
cd Digital-Evidence-Tracking-and-Management-System
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Database

Create a PostgreSQL database and update `Webapp/mysite/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'detams_db',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '',
    }
}
```

### 5. Run Migrations

```bash
cd Webapp
python manage.py migrate
```

### 6. Create Admin (Superuser)

```bash
python manage.py createsuperuser
```

### 7. Start Development Server

```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000/** — you will be redirected to the login page.

### 8. Initial Setup

1. Log in at `/admin/` with your superuser account
2. **Add Officers** — create users with roles (Senior Officer, Investigator, Auditor)
3. **Create Cases** — fill in case details and assign a Senior Officer
4. Officers can now log in at `/login/` and access their respective dashboards

---

## URL Reference

| URL | View | Access |
|---|---|---|
| `/` | Root redirect | Redirects to dashboard by role |
| `/login/` | Login page | Public |
| `/logout/` | Logout | All authenticated |
| `/admin/` | Admin dashboard | Admin only |
| `/profile/` | Profile page | All (except Admin) |
| `/dashboard/so/` | SO Dashboard | Senior Officer |
| `/dashboard/investigator/` | Investigator Dashboard | Investigator |
| `/dashboard/auditor/` | Auditor Dashboard | Auditor |
| `/assign-investigators/` | Assign Investigators | Senior Officer |
| `/monitor-progress/` | Monitor Progress | Senior Officer |
| `/evidence/upload/` | Upload Evidence | Investigator |
| `/evidence/observations/` | Observations | Investigator |
| `/evidence/<id>/` | Evidence Detail | Authorized users |
| `/evidence/<id>/preview/` | Preview Evidence | Authorized users |
| `/evidence/<id>/download/` | Download Evidence | Authorized users |
| `/evidence/<id>/verify/` | Verify Evidence | Authorized users |
| `/cases/<id>/` | Case Detail | Authorized users |
| `/cases/request_closure/` | Request Closure | Senior Officer |
| `/cases/update_notes/` | Update Case Notes | Investigator |
| `/custody/timeline/` | Custody Timeline | Auditor |
| `/custody/integrity/` | Integrity Console | Auditor |
| `/custody/report/` | Generate Report | Auditor |

---

## Security

### RBAC (Role-Based Access Control)

The `RBACService` class enforces access rules on every view:

| Role | Access Scope |
|---|---|
| Admin (superuser) | Full access to everything |
| Auditor | Read-only access to ALL cases |
| Senior Officer | Only cases where `assigned_so == user` |
| Investigator | Only cases with a `CaseMember` entry |

### View-Level Protections

- **`@login_required`** on every view
- **`@never_cache`** on dashboards and auth views (prevents back-button access after logout)
- **Role verification** — each view checks `user.profile.role`
- **Superuser blocking** — admins are redirected away from user-facing pages
- **CSRF protection** — Django's built-in middleware

### Session Management

| Setting | Value | Purpose |
|---|---|---|
| `SESSION_COOKIE_AGE` | 3600 (1 hour) | Session timeout |
| `SESSION_EXPIRE_AT_BROWSER_CLOSE` | True | Destroyed on browser close |
| `SESSION_SAVE_EVERY_REQUEST` | True | Timer resets on activity |

### Evidence Integrity

- **SHA-256 hashing** — computed at upload, stored in `Evidence.sha256_hash` (non-editable)
- **Verification** — recomputes hash and compares against stored value
- **Tamper detection** — any file modification results in hash mismatch → flagged as COMPROMISED
- **Immutable logs** — `CustodyLog.save()` raises `ValueError` if record already exists

---

## Project Structure

```
Digital-Evidence-Tracking-and-Management-System/
├── README.md
├── requirements.txt
├── DETAMS_Documentation.pdf
│
└── Webapp/
    ├── manage.py
    ├── db.sqlite3
    ├── generate_docs_pdf.py
    │
    ├── mysite/                  # Project configuration
    │   ├── settings.py
    │   ├── urls.py
    │   ├── wsgi.py
    │   └── asgi.py
    │
    ├── users/                   # Authentication & dashboards
    │   ├── models.py            #   UserProfile model
    │   ├── views.py             #   Login, dashboards, assign, monitor
    │   ├── urls.py
    │   ├── admin.py             #   Custom UserAdmin with inline profile
    │   └── templates/users/
    │       ├── login.html
    │       ├── profile.html
    │       ├── so_dashboard.html
    │       ├── investigator_dashboard.html
    │       ├── auditor_dashboard.html
    │       ├── assign_investigators.html
    │       └── monitor_progress.html
    │
    ├── cases/                   # Case management
    │   ├── models.py            #   Case, CaseMember models
    │   ├── views.py             #   case_detail, request_closure, update_notes
    │   ├── urls.py
    │   ├── admin.py             #   CaseAdmin with SO-filtered dropdowns
    │   └── templates/cases/
    │       ├── case_detail.html
    │       └── request_closure.html
    │
    ├── evidence/                # Evidence handling
    │   ├── models.py            #   Evidence, EvidenceNote models
    │   ├── views.py             #   upload, observations, detail, verify, preview, download
    │   ├── forms.py
    │   ├── urls.py
    │   ├── admin.py             #   EvidenceAdmin with readonly notes inline
    │   └── templates/evidence/
    │       ├── upload.html
    │       ├── detail.html
    │       └── observations.html
    │
    ├── custody/                 # Audit trail & auditor tools
    │   ├── models.py            #   CustodyLog model (immutable)
    │   ├── views.py             #   timeline, integrity_console, generate_report
    │   ├── urls.py
    │   ├── admin.py             #   Fully readonly CustodyLogAdmin
    │   └── templates/custody/
    │       ├── timeline.html
    │       ├── integrity_console.html
    │       └── generate_report.html
    │
    ├── core/                    # Shared services
    │   ├── hash_service.py      #   SHA-256 generate & verify
    │   ├── rbac_service.py      #   Role-based access control
    │   └── admin_site.py        #   Custom DETAMSAdminSite
    │
    ├── templates/               # Global template overrides
    │   ├── admin/
    │   │   ├── index.html       #   Custom admin dashboard
    │   │   ├── base_site.html   #   Admin CSS overrides
    │   │   └── login.html       #   Custom admin login
    │   └── registration/
    │       └── logged_out.html
    │
    └── media/                   # Uploaded files
        └── evidence_files/
```

---
<p align="center">
  Built with Django  •  Secured with SHA-256  •  Audited with Immutable Logs
</p>
