# Port Scanner

A desktop TCP Port Scanner built with **Python** following the **MVC (Model-View-Controller)** architecture.

The application allows users to register, log in, perform port scans, save scan history, and review previous scan results through a graphical user interface.

## Features

* User registration and authentication using **bcrypt**
* SQLite database for user accounts and scan reports
* Quick Scan (Common Ports)
* Full Scan (1–65535)
* Custom Port Range Scan
* Multi-threaded scanning using `ThreadPoolExecutor`
* Automatic service name detection for common ports
* Scan history per user
* Graphical User Interface built with Tkinter
* MVC architecture for clear separation of responsibilities

## Technologies

* Python 3
* Tkinter
* SQLite
* bcrypt
* socket
* concurrent.futures
* JSON

## Project Structure

```text
PortScanner/
│
├── app.py
├── models/
├── controllers/
├── services/
├── views/
├── utils/
├── data/
└── exports/
```

## Architecture

The project follows the MVC pattern.

* **Models** – Database access and data persistence.
* **Controllers** – Application logic and communication between Views and Models.
* **Services** – Networking, authentication, scanning logic and utilities.
* **Views** – Graphical user interface.

## Running the Project

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
python app.py
```

## Notes

The backend architecture, business logic, networking, database design, authentication, and MVC structure were designed and implemented by me.

The graphical user interface (Views) was developed using AI-assisted (vibe coding) development while keeping the existing backend architecture unchanged also the export to pdf.
