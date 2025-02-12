import tkinter as tk
from tkinter import messagebox
import mysql.connector
import bcrypt
from PIL import Image, ImageTk
from sales import open_sales_window
import sales
from employee import open_employee_form
import employee
from purchase import open_purchase_form
from items import open_item_form

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
        self.root.geometry("800x600")

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
        self.password_frame = tk.Frame(root)  # New frame to contain password elements

        self.password_label = tk.Label(
            self.password_frame, text="Enter Password:", font=("Arial", 14)
        )
        self.password_input = tk.Entry(
            self.password_frame,
            textvariable=self.password_entry,
            show="*",
            font=("Arial", 12),
            width=20,
        )
        self.login_button = tk.Button(
            self.password_frame,
            text="Login",
            command=self.login,
            font=("Arial", 12),
            width=10,
        )

        # Bind Enter key to login
        self.password_input.bind("<Return>", lambda event: self.login())

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
        try:
            head_image = Image.open("head_icon.png")
            head_image = head_image.resize((80, 80))
            head_icon = ImageTk.PhotoImage(head_image)
        except FileNotFoundError:
            head_icon = None

        # Create a button for each employee
        for i, (username, name) in enumerate(self.employees):
            box = tk.Frame(
                frame,
                width=100,
                height=130,
                bg="lightgray",
                relief="raised",
                borderwidth=2,
            )
            box.grid(row=i // 3, column=i % 3, padx=10, pady=10)

            if head_icon:
                icon_label = tk.Label(box, image=head_icon, bg="lightgray")
                icon_label.image = head_icon
                icon_label.pack(pady=5)

            name_label = tk.Label(box, text=name, font=("Arial", 12), bg="lightgray")
            name_label.pack()

            box.bind("<Button-1>", lambda e, u=username: self.select_employee(u))

    def select_employee(self, username):
        # Reset previous selection
        self.selected_username = username
        self.password_entry.set("")  # Clear previous input

        # Show password entry elements
        self.password_frame.pack(pady=20)
        self.password_label.pack(side="left", padx=5)
        self.password_input.pack(side="left", padx=5)
        self.login_button.pack(side="left", padx=5)

        # Set focus to password input
        self.password_input.focus_set()

    def login(self):
        if not self.selected_username:
            messagebox.showerror("Error", "Please select an employee first!")
            return

        password = self.password_entry.get().strip()

        if not password:
            messagebox.showerror("Error", "Please enter your password!")
            self.password_input.focus_set()
            return

        # Database verification
        try:
            cnx = mysql.connector.connect(**config)
            cursor = cnx.cursor()
            cursor.execute(
                "SELECT password, name, role FROM Employee WHERE username = %s",
                (self.selected_username,),
            )
            result = cursor.fetchone()
            cursor.close()
            cnx.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Connection failed: {str(e)}")
            return

        if result:
            stored_password, name, role = result
            if bcrypt.checkpw(
                password.encode("utf-8"), stored_password.encode("utf-8")
            ):
                self.root.destroy()
                self.open_admin_screen(name, role)
            else:
                messagebox.showerror("Login Failed", "Incorrect password!")
                self.password_entry.set("")
                self.password_input.focus_set()
        else:
            messagebox.showerror("Error", "User not found!")
            self.password_entry.set("")
            self.selected_username = None
            self.password_frame.pack_forget()

    def open_admin_screen(self, name, role):
        admin_root = tk.Tk()
        AdminScreen(admin_root, name, role)
        admin_root.mainloop()


# Rest of the AdminScreen class remains the same...


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
        try:
            open_item_form()  # This calls the function from inventory.py
        except Exception as ex:
            messagebox.showerror("Error", f"Failed to open Inventory module: {ex}")
        # messagebox.showinfo("Inventory", "Opening Inventory Module...")

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
        try:
            open_purchase_form()  # This calls the function from purchase.py
        except Exception as ex:
            messagebox.showerror("Error", f"Failed to open Purchase module: {ex}")

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
