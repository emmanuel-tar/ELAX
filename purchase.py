import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime

# Database configuration
config = {
    "user": "root",
    "password": "root",
    "host": "127.0.0.1",
    "port": "1207",
    "database": "elax_pos",
}


# Create tables for suppliers and purchases
def create_tables():
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS suppliers (
                supplier_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                contact_info VARCHAR(255)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS purchase (
                purchase_id INT AUTO_INCREMENT PRIMARY KEY,
                supplier_id INT NOT NULL,
                item_id INT NOT NULL,
                quantity INT NOT NULL,
                cost_price DECIMAL(10, 2) NOT NULL,
                warehouse VARCHAR(255) NOT NULL,
                purchase_date DATETIME NOT NULL,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
                FOREIGN KEY (item_id) REFERENCES Inventory(item_id)
            )
            """
        )
        cnx.commit()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error creating tables: {err}")
    finally:
        cursor.close()
        cnx.close()


# Fetch suppliers, inventory items, and warehouses
def fetch_suppliers():
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        cursor.execute("SELECT name FROM suppliers")
        suppliers = cursor.fetchall()
        return [supplier[0] for supplier in suppliers]
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching suppliers: {err}")
        return []
    finally:
        cursor.close()
        cnx.close()


def fetch_inventory_items():
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        cursor.execute("SELECT name FROM Inventory")
        items = cursor.fetchall()
        return [item[0] for item in items]
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching inventory items: {err}")
        return []
    finally:
        cursor.close()
        cnx.close()


def fetch_warehouses():
    return ["Warehouse A", "Warehouse B", "Warehouse C"]


# Add purchase records
def add_purchase(table, selected_items, supplier, warehouse):
    if not all([supplier, warehouse, selected_items]):
        messagebox.showwarning(
            "Incomplete Data", "Please fill all fields and select items."
        )
        return

    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        # Fetch supplier ID
        cursor.execute("SELECT supplier_id FROM suppliers WHERE name = %s", (supplier,))
        supplier_id = cursor.fetchone()

        if not supplier_id:
            messagebox.showerror("Error", "Invalid supplier selection.")
            return

        supplier_id = supplier_id[0]

        # Insert purchase records for selected items
        for item in selected_items:
            item_name, quantity, cost = item
            cursor.execute(
                "SELECT item_id FROM Inventory WHERE name = %s", (item_name,)
            )
            item_id = cursor.fetchone()

            if not item_id:
                messagebox.showerror("Error", f"Invalid item: {item_name}")
                continue

            item_id = item_id[0]
            query = """
                INSERT INTO purchase (supplier_id, item_id, quantity, cost_price, warehouse, purchase_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            purchase_date = datetime.now()
            cursor.execute(
                query, (supplier_id, item_id, quantity, cost, warehouse, purchase_date)
            )

            # Update inventory
            cursor.execute(
                "UPDATE Inventory SET quantity = quantity + %s WHERE item_id = %s",
                (quantity, item_id),
            )

        cnx.commit()
        messagebox.showinfo("Success", "Purchase added successfully.")

        # Update table view
        for item in selected_items:
            item_name, quantity, cost = item
            table.insert(
                "", "end", values=(supplier, item_name, quantity, cost, warehouse)
            )

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error adding purchase: {err}")
    finally:
        cursor.close()
        cnx.close()


# Open purchase form
def open_purchase_form():
    create_tables()

    selected_items = []

    def select_item():
        """Open a new window to select multiple items."""
        selection_window = tk.Toplevel(purchase_window)
        selection_window.title("Select Items")
        selection_window.geometry("400x300")

        tk.Label(selection_window, text="Select Items").pack(pady=10)

        item_listbox = tk.Listbox(selection_window, selectmode=tk.MULTIPLE, height=15)
        for item in inventory_items:
            item_listbox.insert(tk.END, item)
        item_listbox.pack(pady=10)

        tk.Button(
            selection_window,
            text="Add Selected Items",
            command=lambda: add_selected_items(item_listbox, selection_window),
        ).pack()

    def add_selected_items(listbox, window):
        """Add selected items to the list and close the selection window."""
        selected_indices = listbox.curselection()
        for index in selected_indices:
            item_name = inventory_items[index]
            quantity = 1  # Default quantity
            cost = 0.0  # Default cost
            selected_items.append((item_name, quantity, cost))
        window.destroy()

    purchase_window = tk.Toplevel()
    purchase_window.title("Purchase Management")
    purchase_window.geometry("800x500")

    table_frame = ttk.Frame(purchase_window)
    table_frame.pack(fill="both", expand=True)

    columns = ("Supplier", "Item", "Quantity", "Cost", "Warehouse")
    purchase_table = ttk.Treeview(
        table_frame, columns=columns, show="headings", height=10
    )
    for col in columns:
        purchase_table.heading(col, text=col)
        purchase_table.column(col, width=150, anchor=tk.CENTER)
    purchase_table.pack(fill="both", expand=True)

    suppliers = fetch_suppliers()
    inventory_items = fetch_inventory_items()
    warehouses = fetch_warehouses()

    form_frame = ttk.Frame(purchase_window)
    form_frame.pack(fill="x")

    ttk.Label(form_frame, text="Supplier:").grid(row=0, column=0, padx=5, pady=5)
    supplier_combobox = ttk.Combobox(form_frame, values=suppliers, state="readonly")
    supplier_combobox.grid(row=0, column=1)

    ttk.Label(form_frame, text="Warehouse:").grid(row=1, column=0, padx=5, pady=5)
    warehouse_combobox = ttk.Combobox(form_frame, values=warehouses, state="readonly")
    warehouse_combobox.grid(row=1, column=1)

    ttk.Button(form_frame, text="Select Items", command=select_item).grid(
        row=2, column=0, pady=10
    )

    ttk.Button(
        form_frame,
        text="Save",
        command=lambda: add_purchase(
            purchase_table,
            selected_items,
            supplier_combobox.get(),
            warehouse_combobox.get(),
        ),
    ).grid(row=2, column=1, pady=10)

    ttk.Button(
        form_frame,
        text="Close",
        command=purchase_window.destroy,
    ).grid(row=2, column=2, pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    open_purchase_form()
