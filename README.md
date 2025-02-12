# Rentals Management System

This project is a comprehensive application that manages the geographic representation of real estate properties and rental information. It includes property listings, ownership details, refined searches, and allows special users to manipulate data through a QGIS connection.

---

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript, Leaflet
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
```
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Dependencies
```
pip install -r requirements.txt
```
#### 4. Set Up the Database
* Create a PostgreSQL database.
* Update the DATABASES section in settings.py with your PostgreSQL credentials:
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_database_name',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```
#### 5. Apply Migrations
```
python manage.py makemigrations
python manage.py migrate
```
#### 6. Run the Development Server
```
python manage.py runserver
```
## API Usage
The project includes several API endpoints for managing data.
### Example: PUT Data to an API Endpoint
Use the PUT method to add a building using cURL:
```
curl -X PUT http://127.0.0.1:8000/api/buildings/ \
     -H "Content-Type: application/json" \
     -d '{
         "user_id": 1,
         "county": "Nairobi",
         "district": "Westlands",
         "rent": 45000.00,
         "payment_details": "Paid",
         "occupancy": true,
         "building": "POINT(36.8219 -1.2921)"
     }'
```
### Endpoints Overview
* GET /api/buildings/: Retrieve all buildings in GeoJSON format.
* PUT /api/buildings/: Add a new building.
* GET /api/buildings/<building_pk>/: Retrieve details of a specific building.
* PATCH /api/buildings/<building_pk>/: Update details of a specific building.
* DELETE /api/buildings/<building_pk>/: Delete a specific building.
## Testing
```
python manage.py test
```
## Contributing
To contribute to the project, follow these steps:
* Fork the repository.
* Create a feature branch:
```
git checkout -b feature-name
```
* Commit your changes:
```
git commit -m "Description of the feature added"
```
* Push to your branch:
```
git push origin feature-name
```
* Create a pull request on GitHub.
## Authors 
Philip Nyakwaka - [Github](https://github.com/philipnyakwaka1) / [Twitter](https://x.com/ominaphillip18)

## License
Public Domain. No copy write protection. 