# Resident Service Portal

Resident Service Portal is a simple and clean web based system designed for residential communities.  
Residents can log in and book maintenance services such as plumbing or electrical work.  
Admins can view all bookings in one place, making this project perfect for demos, academic submissions, and client presentations.

## Features

### Resident features

* Login using a resident ID from the data file  
* View a personalized dashboard with resident details  
* Browse available services with icons and descriptions  
* Submit service booking requests with a date selector  
* Receive a booking confirmation with reference number  
* Access booking history during the session  

### Admin features

* Separate admin login page  
* View all recent service bookings in a single table  
* Check resident information such as name, flat, floor, and building  
* See requested service details and booking reference  
* Easy interface suitable for managers and clients  

## Tech stack used

### Backend

* Python  
* Flask  
* Jinja templates  
* JSON based storage for demo residents and service data

### Frontend

* HTML  
* CSS  
* Simple responsive layout  

## Project structure

Below is the main project layout  
This structure makes it easy to understand and extend

* app.py main application file  
* residents.json sample resident data  
* requirements.txt list of dependencies  

Templates folder contains

* login.html resident login  
* dashboard.html resident dashboard  
* services.html service booking page  
* admin_login.html admin authentication  
* admin.html admin booking preview screen  

Static folder contains

* style.css stylesheet  

## How to run this project

### Install dependencies

Use your existing virtual environment or create a new one then run

```bash
pip install -r requirements.txt
