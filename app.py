import logging
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLineEdit, QTableWidget, QTableWidgetItem, QPushButton, QDateEdit, QTimeEdit, QVBoxLayout, QFormLayout, QHBoxLayout, QApplication
from PyQt5.QtCore import Qt, QDate, QTime
import sys
import csv
import os
from cryptography.fernet import Fernet
import io

# Log configuration
logging.basicConfig(level=logging.INFO)

class EventsManager(QtWidgets.QWidget): 
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Events Manager")
        self.setGeometry(100, 100, 1000, 600)
        self.layout = QVBoxLayout()

        logging.info("Initializing Events Manager...")

        # --- Create directories and files ---
        self.app_directory = os.path.dirname(os.path.abspath(__file__))
        self.data_folder = os.path.join(self.app_directory, "data")
        os.makedirs(self.data_folder, exist_ok=True)

        # --- Define file paths ---
        self.csv_file_path = os.path.join(self.data_folder, "attendees.csv")

        # --- Initialize encryption handling ---
        self.fernet = self.load_or_create_key()

        # --- Registration form ---
        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.phone_input = QLineEdit()

        # Date and time fields
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.time_input = QTimeEdit()
        self.time_input.setDisplayFormat("HH:mm")

        form_layout.addRow("Full Name", self.name_input)
        form_layout.addRow("Email", self.email_input)
        form_layout.addRow("Phone", self.phone_input)
        form_layout.addRow("Date", self.date_input)
        form_layout.addRow("Time", self.time_input)

        self.layout.addLayout(form_layout)

        # --- Buttons ---
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Register")
        self.add_button.setFixedWidth(150)
        self.add_button.clicked.connect(self.add_register)
        button_layout.addWidget(self.add_button)

        self.update_button = QPushButton("Update")
        self.update_button.setFixedWidth(150)
        self.update_button.clicked.connect(self.update_selected_register)
        button_layout.addWidget(self.update_button)

        self.delete_button = QPushButton("Delete")
        self.delete_button.setFixedWidth(150)
        self.delete_button.clicked.connect(self.delete_selected_row)
        button_layout.addWidget(self.delete_button)

        button_layout.setAlignment(Qt.AlignCenter)
        self.layout.addLayout(button_layout)

        # --- Search input ---
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by email or phone...")
        self.search_input.textChanged.connect(self.filter_data)
        self.layout.addWidget(self.search_input)

        # --- Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Name", "Email", "Phone", "Date", "Time"])
        self.table.itemSelectionChanged.connect(self.on_item_selection_changed)  # Detect selection change
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)

        # --- Create or load encrypted CSV file ---
        if not os.path.exists(self.csv_file_path):
            logging.info("CSV file not found. Creating new one...")
            self.create_empty_csv()
        else:
            logging.info("Loading data from CSV...")
            self.load_data()

    # ------------------- SECURITY -------------------
    def load_or_create_key(self):
        """Load or create an encryption key."""
        logging.info("Loading or creating encryption key...")
        self.key_path = os.path.join(self.data_folder, "key.key")
        if not os.path.exists(self.key_path):
            key = Fernet.generate_key()
            with open(self.key_path, "wb") as key_file:
                key_file.write(key)
        else:
            with open(self.key_path, "rb") as key_file:
                key = key_file.read()
        return Fernet(key)

    def create_empty_csv(self):
        """Create an empty CSV file with headers and encrypt it."""
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["Name", "Email", "Phone", "Date", "Time"])
        encrypted = self.fernet.encrypt(buffer.getvalue().encode("utf-8"))
        with open(self.csv_file_path, "wb") as file:
            file.write(encrypted)
        logging.info("Empty CSV created and encrypted.")

    # ------------------- MAIN FUNCTIONALITY -------------------
    def add_register(self):
        """Add new register and save it in the encrypted CSV file."""
        # Validate fields
        name = self.name_input.text()
        email = self.email_input.text()
        phone = self.phone_input.text()
        date = self.date_input.date().toString("dd-MM-yyyy")
        time = self.time_input.time().toString("HH:mm")

        if not name or not email or not phone or not date or not time:
            QtWidgets.QMessageBox.warning(self, "Warning", "All fields are required!")
            return  # Don't proceed if any field is empty

        logging.info(f"Adding data: {name}, {email}, {phone}, {date}, {time}")

        # Add data to the table
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        self.table.setItem(row_position, 0, QTableWidgetItem(name))
        self.table.setItem(row_position, 1, QTableWidgetItem(email))
        self.table.setItem(row_position, 2, QTableWidgetItem(phone))
        self.table.setItem(row_position, 3, QTableWidgetItem(date))
        self.table.setItem(row_position, 4, QTableWidgetItem(time))

        # Save the table to the encrypted CSV
        self.save_table_to_csv()

        # Clear the form fields
        self.name_input.clear()
        self.email_input.clear()
        self.phone_input.clear()
        self.date_input.setDate(QDate.currentDate())
        self.time_input.setTime(QTime.currentTime())

    def update_selected_register(self):
        """Update the selected record."""
        selected_row = self.table.currentRow()

        if selected_row >= 0:
            # Get the data from the form fields
            name = self.name_input.text()
            email = self.email_input.text()
            phone = self.phone_input.text()
            date = self.date_input.date().toString("dd-MM-yyyy")
            time = self.time_input.time().toString("HH:mm")

            # Validate fields
            if not name or not email or not phone or not date or not time:
                QtWidgets.QMessageBox.warning(self, "Warning", "All fields are required!")
                return  # Don't proceed if any field is empty

            # Update the data in the table
            self.table.setItem(selected_row, 0, QTableWidgetItem(name))
            self.table.setItem(selected_row, 1, QTableWidgetItem(email))
            self.table.setItem(selected_row, 2, QTableWidgetItem(phone))
            self.table.setItem(selected_row, 3, QTableWidgetItem(date))
            self.table.setItem(selected_row, 4, QTableWidgetItem(time))

            # Save the changes to the encrypted CSV
            self.save_table_to_csv()

            # Success confirmation message
            QtWidgets.QMessageBox.information(self, "Success", "Record updated successfully!")

        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select a row to update.")

    def save_table_to_csv(self):
        """Encrypt and save the current table data to the CSV file."""
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["Name", "Email", "Phone", "Date", "Time"])
        for row in range(self.table.rowCount()):
            row_data = []
            for column in range(self.table.columnCount()):
                item = self.table.item(row, column)
                row_data.append(item.text() if item else "")
            writer.writerow(row_data)
        data_bytes = buffer.getvalue().encode('utf-8')
        encrypted_data = self.fernet.encrypt(data_bytes)
        with open(self.csv_file_path, "wb") as file:
            file.write(encrypted_data)
        logging.info("Table data saved to CSV.")

    def load_data(self):
        """Decrypt and load data from the CSV file."""
        try:
            with open(self.csv_file_path, "rb") as file:
                encrypted_data = file.read()
                decrypted_data = self.fernet.decrypt(encrypted_data).decode("utf-8")
                reader = csv.reader(decrypted_data.splitlines())
                next(reader)  # Skip header
                for row in reader:
                    row_position = self.table.rowCount()
                    self.table.insertRow(row_position)
                    for col, value in enumerate(row):
                        self.table.setItem(row_position, col, QTableWidgetItem(value))
            logging.info("Data loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading attendees: {e}")

    def filter_data(self, text):
        """Filter the table by email or phone."""
        for row in range(self.table.rowCount()):
            email = self.table.item(row, 1).text().lower()
            phone = self.table.item(row, 2).text().lower()
            visible = text.lower() in email or text.lower() in phone
            self.table.setRowHidden(row, not visible)

    def delete_selected_row(self):
        """Delete the selected record after confirmation."""
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            reply = QtWidgets.QMessageBox.question(
                self,
                'Confirm Deletion',
                'Are you sure you want to delete this record?',
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No
            )
            if reply == QtWidgets.QMessageBox.Yes:
                self.table.removeRow(selected_row)
                self.save_table_to_csv()
                # No success message displayed here
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select a row to delete.")

    # ------------------- HELPER METHODS -------------------
    def on_item_selection_changed(self):
        """Handle table row selection and populate the form fields."""
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            # Populate the form fields with the selected row data
            self.name_input.setText(self.table.item(selected_row, 0).text())
            self.email_input.setText(self.table.item(selected_row, 1).text())
            self.phone_input.setText(self.table.item(selected_row, 2).text())
            self.date_input.setDate(QDate.fromString(self.table.item(selected_row, 3).text(), "dd-MM-yyyy"))
            self.time_input.setTime(QTime.fromString(self.table.item(selected_row, 4).text(), "HH:mm"))

# Main function to run the app
if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = EventsManager()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        logging.error(f"An error occurred: {e}")
