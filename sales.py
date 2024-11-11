# sales.py

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


def open_sales_window():
    # Cart items list
    checkout = None
    cart_items = []

    # Create a new window for the sales screen
    sales_window = tk.Toplevel()
    sales_window.title("Sales - ELAX POS")
    sales_window.geometry("800x600")

    # Header
    tk.Label(sales_window, text="Sales Module", font=("Arial", 18)).pack(pady=10)

    # Inventory item dropdown to select and fetch item details
    inventory_items = fetch_inventory_items()
    tk.Label(sales_window, text="Select Item:", font=("Arial", 12)).place(x=50, y=100)
    item_combobox = ttk.Combobox(
        sales_window, font=("Arial", 12), values=inventory_items
    )
    item_combobox.place(x=200, y=100, width=200)

    # Labels for quantity and price
    tk.Label(sales_window, text="Quantity:", font=("Arial", 12)).place(x=50, y=150)
    quantity_entry = tk.Entry(sales_window, font=("Arial", 12))
    quantity_entry.place(x=200, y=150, width=200)

    # Add to cart button
    add_to_cart_button = tk.Button(
        sales_window,
        text="Add to Cart",
        font=("Arial", 12),
        command=lambda: add_to_cart(
            item_combobox, quantity_entry, cart_items, cart_listbox
        ),
    )
    add_to_cart_button.place(x=50, y=250)

    # Cart area (displaying cart items)
    cart_frame = tk.Frame(sales_window, bg="lightgrey", bd=1, relief="sunken")
    cart_frame.place(x=450, y=100, width=300, height=300)
    tk.Label(cart_frame, text="Cart", font=("Arial", 14), bg="lightgrey").pack()

    # Listbox for cart items display
    cart_listbox = tk.Listbox(cart_frame, font=("Arial", 12), width=40, height=15)
    cart_listbox.pack(pady=5)

    # Checkout button
    tk.Button(
        sales_window, text="Checkout", font=("Arial", 14), command=checkout
    ).place(x=50, y=400)

    # Close button
    tk.Button(
        sales_window, text="Close", font=("Arial", 12), command=sales_window.destroy
    ).place(x=700, y=500)

    def add_to_cart(item_combo, qty_entry, cart, listbox):
        item_name = item_combo.get()
        quantity = qty_entry.get()

        # Check if item and quantity are provided
        if not item_name or not quantity:
            messagebox.showwarning(
                "Incomplete Entry", "Please select an item and enter quantity."
            )
            return

        try:
            # Fetch item details from the database
            item_details = fetch_item_details(item_name)
            price = item_details["price"]
            subtotal = price * int(quantity)
            cart.append((item_name, quantity, price, subtotal))

            # Update the cart listbox
            listbox.insert(tk.END, f"{item_name} x {quantity} @ {price} = {subtotal}")

            # Clear inputs after adding to cart
            item_combo.set("")
            qty_entry.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error adding item to cart: {err}")

    def checkout():
        # Display checkout details
        total = sum(item[3] for item in cart_items)
        messagebox.showinfo(
            "Checkout", f"Total amount: {total}\nProceeding to payment..."
        )
        # Additional payment logic can be added here


def fetch_inventory_items():
    """Fetch inventory item names from the database and return as a list."""
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        cursor.execute(
            "SELECT name FROM Inventory"
        )  # Adjust table/column name as needed
        items = cursor.fetchall()
        cursor.close()
        cnx.close()
        return [item[0] for item in items]  # Convert tuple list to name list
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching items: {err}")
        return []


def fetch_item_details(item_name):
    """Fetch item details, like price, from the database for a specific item."""
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT price FROM Inventory WHERE name = %s", (item_name,))
        item_details = cursor.fetchone()
        cursor.close()
        cnx.close()

        if item_details:
            return item_details
        else:
            messagebox.showerror("Error", "Item details not found.")
            return {"price": 0}
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching item details: {err}")
        return {"price": 0}
