# employee.py

import tkinter as tk
from tkinter import messagebox
import mysql.connector

# Database configuration
config = {
    "user": "root",
    "password": "root",
    "host": "127.0.0.1",
    "port": "1207",
    "database": "elax_pos",
}


def open_employee_form():
    # Create a new window for the employee form
    employee_window = tk.Toplevel()
    employee_window.title("Add New Employee")
    employee_window.geometry("400x400")

    # Labels and Entry fields for each attribute
    tk.Label(employee_window, text="Full Name:", font=("Arial", 12)).place(x=20, y=50)
    fullname_entry = tk.Entry(employee_window, font=("Arial", 12))
    fullname_entry.place(x=150, y=50, width=200)

    tk.Label(employee_window, text="Role:", font=("Arial", 12)).place(x=20, y=100)
    role_entry = tk.Entry(employee_window, font=("Arial", 12))
    role_entry.place(x=150, y=100, width=200)

    tk.Label(employee_window, text="Username:", font=("Arial", 12)).place(x=20, y=150)
    username_entry = tk.Entry(employee_window, font=("Arial", 12))
    username_entry.place(x=150, y=150, width=200)

    tk.Label(employee_window, text="Password:", font=("Arial", 12)).place(x=20, y=200)
    password_entry = tk.Entry(employee_window, font=("Arial", 12), show="*")
    password_entry.place(x=150, y=200, width=200)

    tk.Label(employee_window, text="Phone:", font=("Arial", 12)).place(x=20, y=250)
    phone_entry = tk.Entry(employee_window, font=("Arial", 12))
    phone_entry.place(x=150, y=250, width=200)

    tk.Label(employee_window, text="Email:", font=("Arial", 12)).place(x=20, y=300)
    email_entry = tk.Entry(employee_window, font=("Arial", 12))
    email_entry.place(x=150, y=300, width=200)

    # Submit button
    tk.Button(
        employee_window,
        text="Add Employee",
        font=("Arial", 14),
        command=lambda: add_employee(
            fullname_entry.get(),
            role_entry.get(),
            username_entry.get(),
            password_entry.get(),
            phone_entry.get(),
            email_entry.get(),
        ),
    ).place(x=150, y=350)

    # Close button
    tk.Button(
        employee_window,
        text="Close",
        font=("Arial", 12),
        command=employee_window.destroy,
    ).place(x=300, y=350)


def add_employee(fullname, role, username, password, phone, email):
    """Add a new employee to the database."""
    if not all([fullname, role, username, password, phone, email]):
        messagebox.showwarning("Incomplete Entry", "Please fill out all fields.")
        return

    # Insert the employee data into the database
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        query = """
            INSERT INTO employee (name, role, username, password, phone, email)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (fullname, role, username, password, phone, email))
        cnx.commit()

        # Confirm the addition of the employee
        messagebox.showinfo("Success", "Employee added successfully.")

        # Clear the form after submission
        for entry in [fullname, role, username, password, phone, email]:
            entry.set("")

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error adding employee: {err}")
    finally:
        cursor.close()
        cnx.close()
