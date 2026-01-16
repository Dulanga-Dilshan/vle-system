# vle-system
A web-based Virtual Learning Environment (VLE) built with Django for managing courses, students, and faculty roles.


## Project Overview

This project aims to provide a robust platform for universities to manage courses, students, faculty, and announcements through a role-based web interface. The system is built using Django, leveraging its built-in authentication and admin features for rapid development and secure management.

## Admin Features (Implemented)

The admin panel currently supports the following functionalities:

- **User Management**: Create, update, and manage student and faculty accounts.
- **Faculty Management**: Add and manage faculty departments and assignments.
- **Course Management**: Create and manage courses offered by the university.
- **Announcements**: Publish and manage announcements for students and faculty.
- **Batch Management**: Organize students into batches for easier course allocation.
- **Registration Requests**: Approve or reject student registration requests efficiently.

## Tech Stack

- **Backend**: Django (Python 3.x)
- **Database**: PostgreSQL (or SQLite for development)
- **Frontend**: Django templates, HTML, CSS
- **Authentication**: Django built-in auth system
- **Other**: Bootstrap (optional styling), Django admin for management

## Setup Instructions


1. Clone the repository:

```bash
git clone https://github.com/<Dulanga-Dilshan>/vle-system.git
cd vle-system

2. Create a virtual environment and activate it:

python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows


3. Install dependencies:

pip install -r requirements.txt


4. Apply migrations:

python manage.py migrate


5. Create a superuser to access the admin panel:

python manage.py createsuperuser


6. Run the development server:

python manage.py runserver


7. Access the site at http://127.0.0.1:8000/ and log in using the admin credentials.
