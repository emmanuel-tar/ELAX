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


class CartItem:
    def __init__(self, name, price, quantity=1):
        self.name = name
        self.price = float(price)
        self.quantity = int(quantity)

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return (
            f"{self.name} x {self.quantity} @ ${self.price:.2f} = ${self.subtotal:.2f}"
        )


def create_numpad(parent, entry_widget):
    """Create a numeric keypad"""
    numpad_frame = tk.Frame(parent)
    numbers = ["7", "8", "9", "4", "5", "6", "1", "2", "3", "0", "00", "."]

    row = 0
    col = 0
    for num in numbers:
        tk.Button(
            numpad_frame,
            text=num,
            width=4,
            height=2,
            command=lambda n=num: entry_widget.insert(tk.END, n),
        ).grid(row=row, column=col, padx=2, pady=2)
        col += 1
        if col > 2:
            col = 0
            row += 1

    return numpad_frame


def open_sales_window():
    cart_items = []

    # Create main window
    sales_window = tk.Toplevel()
    sales_window.title("Sales - ELAX POS")
    sales_window.geometry("1024x768")

    def update_total_display():
        """Update the total amount display"""
        total = sum(item.subtotal for item in cart_items)
        total_label.config(text=f"Total: ${total:.2f}")
        # Update cart display
        cart_listbox.delete(0, tk.END)
        for item in cart_items:
            cart_listbox.insert(tk.END, str(item))

    def add_to_cart(item_name, price):
        """Add or update item in cart"""
        # Check if item already exists in cart
        existing_item = next(
            (item for item in cart_items if item.name == item_name), None
        )

        try:
            quantity = int(amount_entry.get()) if amount_entry.get() else 1
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity")
            return

        if existing_item:
            existing_item.quantity += quantity
        else:
            cart_items.append(CartItem(item_name, price, quantity))

        amount_entry.delete(0, tk.END)
        update_total_display()

    def remove_selected_item():
        """Remove selected item from cart"""
        selection = cart_listbox.curselection()
        if selection:
            index = selection[0]
            del cart_items[index]
            update_total_display()

    def update_selected_quantity():
        """Update quantity of selected item"""
        selection = cart_listbox.curselection()
        if not selection:
            messagebox.showwarning(
                "Selection Required", "Please select an item to update"
            )
            return

        try:
            new_quantity = int(amount_entry.get())
            if new_quantity <= 0:
                raise ValueError("Quantity must be positive")

            index = selection[0]
            cart_items[index].quantity = new_quantity
            update_total_display()
            amount_entry.delete(0, tk.END)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    # Top bar with search
    top_frame = tk.Frame(sales_window)
    top_frame.pack(fill=tk.X, padx=5, pady=5)

    # Menu button and icon
    tk.Button(top_frame, text="☰", width=3).pack(side=tk.LEFT, padx=5)

    # Search frame
    search_frame = tk.Frame(top_frame)
    search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    search_entry = tk.Entry(search_frame)
    search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def handle_search_result(event):
        """Handle item selection from search results"""
        selection = search_results_list.curselection()
        if selection:
            item_str = search_results_list.get(selection[0])
            name = item_str.split(" - ")[0]
            price = float(item_str.split("Price: $")[1])
            add_to_cart(name, price)

    # Search results list
    search_results_frame = tk.Frame(sales_window)
    search_results_frame.pack(fill=tk.X, padx=5)
    search_results_list = tk.Listbox(search_results_frame, height=5)
    search_results_list.pack(fill=tk.X)
    search_results_list.bind("<<ListboxSelect>>", handle_search_result)

    def search_items():
        query = search_entry.get()
        try:
            connection = mysql.connector.connect(**config)
            cursor = connection.cursor()
            cursor.execute(
                "SELECT name, quantity, price FROM inventory WHERE name LIKE %s",
                ("%" + query + "%",),
            )
            results = cursor.fetchall()

            search_results_list.delete(0, tk.END)
            for row in results:
                item_name, quantity, price = row
                search_results_list.insert(
                    tk.END, f"{item_name} - Qty: {quantity} - Price: ${price:.2f}"
                )

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    search_button = tk.Button(search_frame, text="🔍", width=3, command=search_items)
    search_button.pack(side=tk.LEFT, padx=2)

    # Main content area
    content_frame = tk.Frame(sales_window)
    content_frame.pack(fill=tk.BOTH, expand=True, padx=5)

    # Left panel for cart
    left_panel = tk.Frame(content_frame)
    left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Cart listbox
    cart_listbox = tk.Listbox(left_panel, font=("Arial", 12))
    cart_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

    # Total display
    total_label = tk.Label(left_panel, text="Total: $0.00", font=("Arial", 14, "bold"))
    total_label.pack(pady=5)

    # Cart action buttons
    cart_buttons = tk.Frame(left_panel)
    cart_buttons.pack(fill=tk.X, pady=5)
    tk.Button(cart_buttons, text="Update Qty", command=update_selected_quantity).pack(
        side=tk.LEFT, padx=2
    )
    tk.Button(cart_buttons, text="Remove", command=remove_selected_item).pack(
        side=tk.LEFT, padx=2
    )
    tk.Button(cart_buttons, text="Hold").pack(side=tk.LEFT, padx=2)
    tk.Button(cart_buttons, text="Recall").pack(side=tk.LEFT, padx=2)

    # Right panel for numpad and payment
    right_panel = tk.Frame(content_frame, width=200)
    right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=5)

    # Payment info
    payment_frame = tk.Frame(right_panel)
    payment_frame.pack(fill=tk.X, pady=5)
    tk.Label(payment_frame, text="Quantity/Amount").pack()
    amount_entry = tk.Entry(payment_frame)
    amount_entry.pack(fill=tk.X, pady=5)

    # Numpad
    numpad = create_numpad(right_panel, amount_entry)
    numpad.pack(pady=5)

    # Bottom action buttons
    bottom_frame = tk.Frame(sales_window)
    bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

    def handle_action(action):
        """Handle bottom action button clicks"""
        if action == "Checkout":
            if cart_items:
                total = sum(item.subtotal for item in cart_items)
                generate_invoice(cart_items, total)
                messagebox.showinfo(
                    "Checkout", f"Invoice generated. Total amount: ${total:.2f}"
                )
                cart_items.clear()
                update_total_display()
            else:
                messagebox.showwarning("Empty Cart", "Please add items to cart first")
        elif action == "Back":
            sales_window.destroy()
        elif action == "Logout":
            sales_window.destroy()

    action_buttons = ["Post", "Logout", "CMD", "Back", "Checkout"]
    for btn_text in action_buttons:
        tk.Button(
            bottom_frame,
            text=btn_text,
            width=10,
            height=2,
            command=lambda t=btn_text: handle_action(t),
        ).pack(side=tk.LEFT, padx=5)


def generate_invoice(cart_items, total):
    """Generate a PDF invoice for the cart."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="ELAX POS - Invoice", ln=True, align="C")
    pdf.cell(200, 10, txt="------------------------------------", ln=True, align="C")

    for item in cart_items:
        pdf.cell(200, 10, txt=str(item), ln=True)

    pdf.cell(200, 10, txt="------------------------------------", ln=True)
    pdf.cell(200, 10, txt=f"Total: ${total:.2f}", ln=True)

    invoice_path = "invoice.pdf"
    pdf.output(invoice_path)
    os.startfile(invoice_path, "open")
