# Rentals Management System

This project is a comprehensive application that manages the geographic representation of real estate properties and rental information. It includes property listings, ownership details, refined searches, and allows special users to manipulate data through a QGIS connection.

---

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, Django
- **Database:** PostgreSQL with PostGIS extension
- **Version Control:** GitHub
- **Deployment & Testing:** Shell scripting, unit tests

---

## Features

- **Manage Property Listings:** Add, update, and delete property details.
- **Geographic Data Integration:** Handle spatial data using PostGIS.
- **Ownership and Rental Details:** Track ownership and rental payment information.
- **QGIS Integration:** Allow special users to interact with data through QGIS.

---

## Installation

### Prerequisites

Ensure the following are installed on your system:

1. **Python 3.x**
2. **PostgreSQL** with the **PostGIS** extension
3. **Git**

---

### Steps to Install

#### 1. Clone the Repository
```bash
git clone https://github.com/philipnyakwaka1/rentals-management-system.git
cd rentals-management-system
```
#### 2. Set Up Virtual Environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

#### 3. Install Dependencies
pip install -r requirements.txt