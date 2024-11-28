import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

# Database configuration
config = {
    "user": "root",
    "password": "root",
    "host": "127.0.0.1",
    "port": "1207",
    "database": "elax_pos",
}


# Create the Inventory table if not exists
def create_inventory_table():
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Inventory (
                item_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                quantity INT DEFAULT 0,
                price DECIMAL(10, 2) NOT NULL,
                barcode VARCHAR(100) UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
        )
        cnx.commit()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error creating table: {err}")
    finally:
        cursor.close()
        cnx.close()


# Fetch all items from the database
def fetch_items():
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        cursor.execute("SELECT item_id, name FROM Inventory")
        items = cursor.fetchall()
        return items
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching items: {err}")
        return []
    finally:
        cursor.close()
        cnx.close()


# Save or update item in the database
def save_item(name, description, quantity, price, barcode):
    if not all([name, quantity, price, barcode]):
        messagebox.showwarning("Incomplete Data", "Please fill all required fields.")
        return

    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        # Insert or update item
        query = """
            INSERT INTO Inventory (name, description, quantity, price, barcode)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                description = VALUES(description),
                quantity = VALUES(quantity),
                price = VALUES(price)
        """
        cursor.execute(query, (name, description, quantity, price, barcode))
        cnx.commit()
        messagebox.showinfo("Success", "Item saved successfully.")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error saving item: {err}")
    finally:
        cursor.close()
        cnx.close()


# Delete item from the database
def delete_item(item_id):
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        cursor.execute("DELETE FROM Inventory WHERE item_id = %s", (item_id,))
        cnx.commit()
        messagebox.showinfo("Success", "Item deleted successfully.")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error deleting item: {err}")
    finally:
        cursor.close()
        cnx.close()


# Open item form
def open_item_form():
    create_inventory_table()

    def refresh_item_list():
        """Refresh the list of items displayed."""
        items = fetch_items()
        item_list.delete(*item_list.get_children())
        for item_id, name in items:
            item_list.insert("", "end", values=(item_id, name))

    def save_item_handler():
        """Save the item to the database."""
        save_item(
            name_entry.get(),
            description_entry.get("1.0", tk.END).strip(),
            quantity_spinbox.get(),
            price_entry.get(),
            barcode_entry.get(),
        )
        refresh_item_list()

    def delete_item_handler():
        """Delete the selected item from the database."""
        selected = item_list.selection()
        if not selected:
            messagebox.showwarning(
                "Selection Error", "Please select an item to delete."
            )
            return
        item_id = item_list.item(selected[0])["values"][0]
        delete_item(item_id)
        refresh_item_list()

    def load_item_details(event):
        """Load the selected item details into the form for editing."""
        selected = item_list.selection()
        if not selected:
            return
        item_id = item_list.item(selected[0])["values"][0]

        try:
            cnx = mysql.connector.connect(**config)
            cursor = cnx.cursor()
            cursor.execute(
                "SELECT name, description, quantity, price, barcode FROM Inventory WHERE item_id = %s",
                (item_id,),
            )
            item = cursor.fetchone()
            if item:
                clear_form()
                name_entry.insert(0, item[0])
                description_entry.insert("1.0", item[1])
                quantity_spinbox.insert(0, item[2])
                price_entry.insert(0, item[3])
                barcode_entry.insert(0, item[4])
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading item details: {err}")
        finally:
            cursor.close()
            cnx.close()

    def clear_form():
        """Clear the form fields for a new entry."""
        name_entry.delete(0, tk.END)
        description_entry.delete("1.0", tk.END)
        quantity_spinbox.delete(0, tk.END)
        price_entry.delete(0, tk.END)
        barcode_entry.delete(0, tk.END)

    item_window = tk.Toplevel()
    item_window.title("Item Management")
    item_window.geometry("800x500")

    # Left frame for item list
    left_frame = ttk.Frame(item_window)
    left_frame.pack(side="left", fill="y", padx=10, pady=10)

    ttk.Label(left_frame, text="Items").pack(anchor="w")
    item_list = ttk.Treeview(left_frame, columns=("ID", "Name"), show="headings")
    item_list.heading("ID", text="ID")
    item_list.heading("Name", text="Name")
    item_list.pack(fill="y", expand=True)
    item_list.bind("<<TreeviewSelect>>", load_item_details)

    # Right frame for item form
    right_frame = ttk.Frame(item_window)
    right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    form_frame = ttk.Frame(right_frame)
    form_frame.pack(fill="x", padx=10, pady=10)

    ttk.Label(form_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
    name_entry = ttk.Entry(form_frame)
    name_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Description:").grid(row=1, column=0, padx=5, pady=5)
    description_entry = tk.Text(form_frame, height=3, width=30)
    description_entry.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Quantity:").grid(row=2, column=0, padx=5, pady=5)
    quantity_spinbox = ttk.Spinbox(form_frame, from_=0, to=10000)
    quantity_spinbox.grid(row=2, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Price:").grid(row=3, column=0, padx=5, pady=5)
    price_entry = ttk.Entry(form_frame)
    price_entry.grid(row=3, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Barcode:").grid(row=4, column=0, padx=5, pady=5)
    barcode_entry = ttk.Entry(form_frame)
    barcode_entry.grid(row=4, column=1, padx=5, pady=5)

    button_frame = ttk.Frame(right_frame)
    button_frame.pack(fill="x", padx=10, pady=10)

    ttk.Button(button_frame, text="New", command=clear_form).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Save", command=save_item_handler).pack(
        side="left", padx=5
    )
    ttk.Button(button_frame, text="Delete", command=delete_item_handler).pack(
        side="left", padx=5
    )
    ttk.Button(button_frame, text="Close", command=item_window.destroy).pack(
        side="right", padx=5
    )

    refresh_item_list()


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    open_item_form()
