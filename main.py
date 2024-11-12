import tkinter as tk
from tkinter import messagebox
import mysql.connector
import bcrypt
from PIL import Image, ImageTk  # For adding a head icon shape
from sales import open_sales_window
import sales
from employee import open_employee_form
import employee     # Import the employee form function

# Database connection settings
config = {
    "user": "root",
    "password": "root",
    "host": "127.0.0.1",
    "port": "1207",
    "database": "elax_pos",
}


class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ELAX POS - Login")
        self.root.geometry("800x600")  # Full-screen window size

        # Variables
        self.selected_username = None
        self.password_entry = tk.StringVar()

        # Fetch employee data
        self.employees = self.get_employees()

        # Header
        tk.Label(root, text="Select Employee", font=("Arial", 18)).pack(pady=10)

        # Create employee selection area
        self.create_employee_boxes()

        # Password Entry field and login button (hidden initially)
        self.password_label = tk.Label(root, text="Enter Password:", font=("Arial", 14))
        self.password_input = tk.Entry(
            root, textvariable=self.password_entry, show="*", font=("Arial", 12)
        )
        self.login_button = tk.Button(
            root, text="Login", command=self.login, font=("Arial", 12)
        )

    def get_employees(self):
        # Fetch employee usernames and names from the database
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        cursor.execute("SELECT username, name FROM Employee")
        employees = cursor.fetchall()
        cursor.close()
        cnx.close()
        return employees

    def create_employee_boxes(self):
        # Frame to hold the employee boxes
        frame = tk.Frame(self.root)
        frame.pack(pady=20)

        # Load head icon image
        head_image = Image.open("head_icon.png")  # Replace with a head icon path
        head_image = head_image.resize((80, 80))
        head_icon = ImageTk.PhotoImage(head_image)

        # Create a button for each employee
        for i, (username, name) in enumerate(self.employees):
            # Create employee box
            box = tk.Frame(frame, width=100, height=130, bg="lightgray")
            box.grid(row=i // 3, column=i % 3, padx=10, pady=10)

            # Add head icon
            icon_label = tk.Label(box, image=head_icon, bg="lightgray")
            icon_label.image = head_icon  # Keep a reference to avoid garbage collection
            icon_label.pack(pady=5)

            # Add employee name label
            name_label = tk.Label(box, text=name, font=("Arial", 12), bg="lightgray")
            name_label.pack()

            # Make the box clickable
            box.bind("<Button-1>", lambda e, u=username: self.select_employee(u))

    def select_employee(self, username):
        # Set the selected username
        self.selected_username = username

        # Show password entry and login button
        self.password_label.pack(pady=10)
        self.password_input.pack(pady=10)
        self.login_button.pack(pady=20)

    def login(self):
        if self.selected_username is None:
            messagebox.showerror("Error", "Please select an employee")
            return

        password = self.password_entry.get()

        if password:
            # Connect to the database and verify password
            cnx = mysql.connector.connect(**config)
            cursor = cnx.cursor()
            cursor.execute(
                "SELECT password, name, role FROM Employee WHERE username = %s",
                (self.selected_username,),
            )
            result = cursor.fetchone()
            cursor.close()
            cnx.close()

            if result:
                stored_password, name, role = result
                if bcrypt.checkpw(
                    password.encode("utf-8"), stored_password.encode("utf-8")
                ):
                    # Login successful
                    self.root.destroy()  # Close login window
                    self.open_admin_screen(name, role)
                else:
                    messagebox.showerror("Error", "Incorrect password")
            else:
                messagebox.showerror("Error", "User not found")
        else:
            messagebox.showerror("Error", "Please enter a password")

    def open_admin_screen(self, name, role):
        # Open the admin screen with the logged-in user's information
        admin_root = tk.Tk()
        AdminScreen(admin_root, name, role)
        admin_root.mainloop()


class AdminScreen:
    def __init__(self, root, name, role):
        self.root = root
        self.root.title("ELAX POS - Admin Screen")
        self.root.geometry("800x600")

        # Display logged-in user information
        tk.Label(root, text=f"Logged in as: {name} ({role})", font=("Arial", 16)).pack(
            pady=10
        )

        # Logout button at the top
        tk.Button(root, text="Logout", command=self.logout, font=("Arial", 14)).pack(
            pady=20
        )
        
        
       

        # Main function area with icons
        self.create_function_icons()

    def create_function_icons(self):
        # Create a frame to hold function buttons
        frame = tk.Frame(self.root)
        frame.pack(pady=30)

        # Define functions and corresponding icon image paths
        functions = [
            ("Sales", "../ELAX/image/sales_icon.png", self.open_sales),
            ("Inventory", "../ELAX/image/inventory_icon.png", self.open_inventory),
            ("Reports", "../ELAX/image/report_icon.png", self.open_reports),
            ("Employees", "../ELAX/image/employees.png", self.open_employees),
            ("Settings", "../ELAX/image/settings.png", self.open_settings),
            ("Purchase", "../ELAX/image/purchase_icon.png", self.open_purchase),
        ]

        # Create a button for each function
        for i, (name, image_path, command) in enumerate(functions):
            # Load the image
            icon_image = Image.open(image_path)
            icon_image = icon_image.resize((80, 80))  # Resize to fit the icon size
            icon_photo = ImageTk.PhotoImage(icon_image)

            # Create a button with the icon and function name
            button = tk.Button(
                frame,
                image=icon_photo,
                text=name,
                compound="top",
                command=command,
                font=("Arial", 10),
                width=100,
                height=130,
            )
            button.image = icon_photo  # Keep a reference to avoid garbage collection
            button.grid(row=i // 3, column=i % 3, padx=15, pady=15)

    def open_sales(self):

        try:
            sales.open_sales_window()  # This calls the function from sales.py
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Sales module: {e}")

    def open_inventory(self):
        messagebox.showinfo("Inventory", "Opening Inventory Module...")

    def open_reports(self):
        messagebox.showinfo("Reports", "Opening Reports Module...")

    def open_employees(self):
        try:
            employee.open_employee_form()
        except Exception as ex:
            messagebox.showinfo("Employees", "Opening Employees Module...")

    def open_settings(self):
        messagebox.showinfo("Settings", "Opening Settings Module...")

    def open_purchase(self):
        messagebox.showinfo("Purchases", "Opening Purchase Module...")

    def logout(self):
        self.root.destroy()
        # Reopen the login window
        main()


# Sample main function for testing the admin screen
def main():
    # Start the application with the login screen
    root = tk.Tk()
    LoginApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
