# 🗓️ Events Manager

**Events Manager** is a simple desktop application built with **PyQt5** that allows you to register, update, search, and delete event attendees.  
All attendee data is securely stored in an **encrypted CSV file** using **Fernet encryption** from the `cryptography` library.

---

## 🚀 Features

- Add, update, and delete attendee records  
- Search attendees by **email or phone number**  
- Store all data in an **encrypted CSV file** (`attendees.csv`)  
- Automatically generates an encryption key (`key.key`)  
- User-friendly **GUI built with PyQt5**  

---

## 🧰 Requirements

Make sure you have **Python 3.8+** installed.  
Then install the required dependencies:

`pip install PyQt5 cryptography`

---

## ▶️ How to Run

- Clone or download the project.
- Open a terminal in the project folder.
- Run the application with:

`python events_manager.py`

---

## 🔒 Security

- All attendee data is encrypted using **Fernet (AES-128)**.  
- The encryption key is stored in `data/key.key`.  
- Do **not share** this key if you want to keep your data private.

---

## 🧑‍💻 Usage

- Fill in the attendee’s **name, email, phone, date, and time**.
- Click **Register** to add them to the list.
- Select a row to **update** or **delete** an existing record.
- Use the search bar to find attendees by **email** or **phone**.

---

## 🪲 Logging

The app logs useful information and errors to the console using Python’s `logging` module.
