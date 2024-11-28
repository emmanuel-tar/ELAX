# sales.py

import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from fpdf import FPDF
import os

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
    cart_items = []

    # Create a new window for the sales screen
    sales_window = tk.Toplevel()
    sales_window.title("Sales - ELAX POS")
    sales_window.geometry("800x600")

    # Header
    tk.Label(sales_window, text="Sales Module", font=("Arial", 18)).pack(pady=10)

    # Barcode entry field
    tk.Label(sales_window, text="Barcode:", font=("Arial", 12)).place(x=50, y=50)
    barcode_entry = tk.Entry(sales_window, font=("Arial", 12))
    barcode_entry.place(x=200, y=50, width=200)

    # Trigger for barcode entry
    barcode_entry.bind(
        "<Return>",
        lambda event: fetch_item_by_barcode(barcode_entry, item_combobox, price_label),
    )

    # Inventory item dropdown for manual selection
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

    tk.Label(sales_window, text="Price:", font=("Arial", 12)).place(x=50, y=200)
    price_label = tk.Label(sales_window, text="0.00", font=("Arial", 12))
    price_label.place(x=200, y=200)

    # Add to cart button
    add_to_cart_button = tk.Button(
        sales_window,
        text="Add to Cart",
        font=("Arial", 12),
        command=lambda: add_to_cart(
            item_combobox, quantity_entry, price_label, cart_items, cart_listbox
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
        sales_window,
        text="Checkout",
        font=("Arial", 14),
        command=lambda: checkout(cart_items),
    ).place(x=50, y=400)

    # Close button
    tk.Button(
        sales_window,
        text="Close",
        font=("Arial", 12),
        command=sales_window.destroy,
    ).place(x=700, y=500)

    def fetch_item_by_barcode(entry, combo, price_label):
        """Fetch item details based on barcode input."""
        barcode = entry.get()
        if not barcode:
            messagebox.showwarning("Input Required", "Please enter a barcode.")
            return

        try:
            # Query the database for the item by barcode
            cnx = mysql.connector.connect(**config)
            cursor = cnx.cursor(dictionary=True)
            cursor.execute(
                "SELECT name, price FROM Inventory WHERE barcode = %s", (barcode,)
            )
            item_details = cursor.fetchone()
            cursor.close()
            cnx.close()

            if item_details:
                # Populate item details
                combo.set(item_details["name"])
                price_label.config(text=str(item_details["price"]))
            else:
                messagebox.showerror("Not Found", "Item not found for this barcode.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error fetching item: {err}")

    def add_to_cart(item_combo, qty_entry, price_lbl, cart, listbox):
        item_name = item_combo.get()
        quantity = qty_entry.get()
        price = price_lbl.cget("text")

        if not item_name or not quantity:
            messagebox.showwarning(
                "Incomplete Entry", "Please select an item and enter quantity."
            )
            return

        try:
            subtotal = float(price) * int(quantity)
            cart.append((item_name, quantity, float(price), subtotal))
            listbox.insert(tk.END, f"{item_name} x {quantity} @ {price} = {subtotal}")

            # Clear inputs
            item_combo.set("")
            qty_entry.delete(0, tk.END)
            price_lbl.config(text="0.00")
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity or price.")

    def checkout(cart):
        if not cart:
            messagebox.showwarning(
                "Empty Cart", "Your cart is empty. Add items to proceed."
            )
            return

        total = sum(item[3] for item in cart)
        generate_invoice(cart, total)
        messagebox.showinfo("Checkout", f"Invoice generated. Total amount: {total}")

    def generate_invoice(cart, total):
        """Generate a PDF invoice for the cart."""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="ELAX POS - Invoice", ln=True, align="C")
        pdf.cell(
            200, 10, txt="------------------------------------", ln=True, align="C"
        )

        for item_name, qty, price, subtotal in cart:
            pdf.cell(
                200, 10, txt=f"{item_name} x {qty} @ {price} = {subtotal}", ln=True
            )

        pdf.cell(200, 10, txt="------------------------------------", ln=True)
        pdf.cell(200, 10, txt=f"Total: {total}", ln=True)

        # Save invoice
        invoice_path = "invoice.pdf"
        pdf.output(invoice_path)
        os.startfile(invoice_path, "open")  # Opens the PDF for viewing/printing


def fetch_inventory_items():
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        cursor.execute("SELECT name FROM Inventory")
        items = cursor.fetchall()
        cursor.close()
        cnx.close()
        return [item[0] for item in items]
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching items: {err}")
        return []
