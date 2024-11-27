# employee.py

import tkinter as tk
from tkinter import messagebox, ttk
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
    # Function to connect to the database
    def connect_db():
        return mysql.connector.connect(**config)

    # Function to fetch employees from the database
    def fetch_employees():
        try:
            cnx = connect_db()
            cursor = cnx.cursor()
            cursor.execute("SELECT employee_id, name FROM employee")
            employees = cursor.fetchall()
            cursor.close()
            cnx.close()
            return employees
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error fetching employees: {err}")
            return []

    # Function to populate form fields when an employee is selected
    def on_employee_select(event):
        selected = employee_listbox.curselection()
        if selected:
            emp_id = employee_listbox.get(selected[0]).split(" - ")[0]
            load_employee_data(emp_id)

    # Function to load employee data into the form fields
    def load_employee_data(emp_id):
        try:
            cnx = connect_db()
            cursor = cnx.cursor()
            cursor.execute(
                "SELECT name, role, username, password, phone, email FROM employee WHERE employee_id = %s",
                (emp_id,),
            )
            result = cursor.fetchone()
            cursor.close()
            cnx.close()

            if result:
                fullname_entry.delete(0, tk.END)
                role_entry.delete(0, tk.END)
                username_entry.delete(0, tk.END)
                password_entry.delete(0, tk.END)
                phone_entry.delete(0, tk.END)
                email_entry.delete(0, tk.END)

                fullname_entry.insert(0, result[0])
                role_entry.insert(0, result[1])
                username_entry.insert(0, result[2])
                password_entry.insert(0, result[3])
                phone_entry.insert(0, result[4])
                email_entry.insert(0, result[5])

                # Store the employee ID for updating
                employee_id_entry.config(state="normal")
                employee_id_entry.delete(0, tk.END)
                employee_id_entry.insert(0, emp_id)
                employee_id_entry.config(state="readonly")

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading employee data: {err}")

    # Function to add or update employee information
    def add_or_update_employee():
        emp_id = employee_id_entry.get()
        fullname = fullname_entry.get()
        role = role_entry.get()
        username = username_entry.get()
        password = password_entry.get()
        phone = phone_entry.get()
        email = email_entry.get()

        if not all([fullname, role, username, password, phone, email]):
            messagebox.showwarning("Incomplete Entry", "Please fill out all fields.")
            return

        try:
            cnx = connect_db()
            cursor = cnx.cursor()

            if emp_id:  # Update existing employee
                cursor.execute(
                    """
                    UPDATE employee
                    SET name = %s, role = %s, username = %s, password = %s, phone = %s, email = %s
                    WHERE employee_id = %s
                    """,
                    (fullname, role, username, password, phone, email, emp_id),
                )
            else:  # Insert new employee
                cursor.execute(
                    """
                    INSERT INTO employee (name, role, username, password, phone, email)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (fullname, role, username, password, phone, email),
                )

            cnx.commit()
            cursor.close()
            cnx.close()

            messagebox.showinfo("Success", "Employee information saved successfully.")
            refresh_employee_list()

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error saving employee data: {err}")

    # Function to delete the selected employee from the database
    def delete_employee():
        emp_id = employee_id_entry.get()
        
        if not emp_id:
            messagebox.showwarning("No Selection", "Please select an employee to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this employee?")
        if confirm:
            try:
                cnx = connect_db()
                cursor = cnx.cursor()
                cursor.execute("DELETE FROM employee WHERE employee_id = %s", (emp_id,))
                cnx.commit()
                cursor.close()
                cnx.close()

                messagebox.showinfo("Deleted", "Employee has been deleted successfully.")
                refresh_employee_list()

                # Clear form fields after deletion
                employee_id_entry.config(state="normal")
                employee_id_entry.delete(0, tk.END)
                fullname_entry.delete(0, tk.END)
                role_entry.delete(0, tk.END)
                username_entry.delete(0, tk.END)
                password_entry.delete(0, tk.END)
                phone_entry.delete(0, tk.END)
                email_entry.delete(0, tk.END)
                employee_id_entry.config(state="readonly")

            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error deleting employee: {err}")

    # Function to refresh the employee list
    def refresh_employee_list():
        employee_listbox.delete(0, tk.END)
        employees = fetch_employees()
        for emp in employees:
            employee_listbox.insert(tk.END, f"{emp[0]} - {emp[1]}")  # Display ID and name

    # Create the main window for the employee form
    employee_window = tk.Toplevel()
    employee_window.title("Employee Management")
    employee_window.geometry("700x500")

    # Left frame for employee list
    left_frame = tk.Frame(employee_window, padx=10, pady=10)
    left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

    # Right frame for employee form with padding for better spacing
    right_frame = tk.Frame(employee_window, padx=20, pady=20)
    right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

    # Employee Listbox
    tk.Label(left_frame, text="Employees", font=("Arial", 14)).pack()
    employee_listbox = tk.Listbox(left_frame, font=("Arial", 12), width=30, height=18)
    employee_listbox.pack(padx=10, pady=10)
    employee_listbox.bind("<<ListboxSelect>>", on_employee_select)

    # Form fields in the right frame with spacing
    tk.Label(right_frame, text="Employee Details", font=("Arial", 14)).grid(row=0, column=0, columnspan=2, pady=(0, 10))

    tk.Label(right_frame, text="Employee ID:", font=("Arial", 12)).grid(row=1, column=0, sticky="e", pady=5)
    employee_id_entry = tk.Entry(right_frame, font=("Arial", 12), state="readonly", width=30)
    employee_id_entry.grid(row=1, column=1, pady=5)

    tk.Label(right_frame, text="Full Name:", font=("Arial", 12)).grid(row=2, column=0, sticky="e", pady=5)
    fullname_entry = tk.Entry(right_frame, font=("Arial", 12), width=30)
    fullname_entry.grid(row=2, column=1, pady=5)

    tk.Label(right_frame, text="Role:", font=("Arial", 12)).grid(row=3, column=0, sticky="e", pady=5)
    role_entry = tk.Entry(right_frame, font=("Arial", 12), width=30)
    role_entry.grid(row=3, column=1, pady=5)

    tk.Label(right_frame, text="Username:", font=("Arial", 12)).grid(row=4, column=0, sticky="e", pady=5)
    username_entry = tk.Entry(right_frame, font=("Arial", 12), width=30)
    username_entry.grid(row=4, column=1, pady=5)

    tk.Label(right_frame, text="Password:", font=("Arial", 12)).grid(row=5, column=0, sticky="e", pady=5)
    password_entry = tk.Entry(right_frame, font=("Arial", 12), show="*", width=30)
    password_entry.grid(row=5, column=1, pady=5)

    tk.Label(right_frame, text="Phone:", font=("Arial", 12)).grid(row=6, column=0, sticky="e", pady=5)
    phone_entry = tk.Entry(right_frame, font=("Arial", 12), width=30)
    phone_entry.grid(row=6, column=1, pady=5)

    tk.Label(right_frame, text="Email:", font=("Arial", 12)).grid(row=7, column=0, sticky="e", pady=5)
    email_entry = tk.Entry(right_frame, font=("Arial", 12), width=30)
    email_entry.grid(row=7, column=1, pady=5)

    # Buttons to add/update and delete employees
    add_update_button = tk.Button(right_frame, text="Save Employee", font=("Arial", 12), command=add_or_update_employee)
    add_update_button.grid(row=8, column=1, pady=10, sticky="e")

    delete_button = tk.Button(right_frame, text="Delete Employee", font=("Arial", 12), command=delete_employee, fg="red")
    delete_button.grid(row=8, column=0, pady=10, sticky="w")

    # Populate employee list
    refresh_employee_list()

# Usage
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    open_employee_form()
    root.mainloop()
