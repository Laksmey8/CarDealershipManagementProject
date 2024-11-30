from tkinter import ttk, messagebox
import tkinter as tk
import sqlite3
import os

# Database initialization
db_path = 'data/dealership_database.sqlite'
db_dir = os.path.dirname(db_path)
if db_dir and not os.path.exists(db_dir):
    os.makedirs(db_dir, exist_ok=True)

conn = sqlite3.connect(db_path)

def initialize_database():
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS inventory (
            car_id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_model CHAR(50) NOT NULL,
            car_type CHAR(50) NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 1,
            license_plate CHAR(20) UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_id INTEGER NOT NULL,
            customer_name CHAR(50) NOT NULL,
            contact CHAR(15) NOT NULL,
            sale_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (car_id) REFERENCES inventory(car_id)
        );
    ''')
    conn.commit()

def add_car(car_model, car_type, price, stock, license_plate):
    try:
        cursor = conn.execute('''
            INSERT INTO inventory (car_model, car_type, price, stock, license_plate)
            VALUES (?, ?, ?, ?, ?)
        ''', (car_model, car_type, price, stock, license_plate))
        conn.commit()
        car_id = cursor.lastrowid  # Get the ID of the newly inserted row
        return f"Car '{car_model}' added successfully! Car ID: {car_id}"
    except sqlite3.IntegrityError:
        return f"Error: License plate must be unique."
    except sqlite3.Error as e:
        return f"Database error: {e}"

def sell_car(car_id, customer_name, contact):
    try:
        cursor = conn.execute('SELECT stock FROM inventory WHERE car_id = ?', (car_id,))
        car = cursor.fetchone()

        if not car:
            return f"Sale failed: Car with ID {car_id} not found in inventory."

        stock = car[0]
        if stock <= 0:
            return f"Sale failed: Car with ID {car_id} is out of stock."

        conn.execute('''
            INSERT INTO sales (car_id, customer_name, contact)
            VALUES (?, ?, ?)
        ''', (car_id, customer_name, contact))

        conn.execute('''
            UPDATE inventory
            SET stock = stock - 1
            WHERE car_id = ?
        ''', (car_id,))

        conn.commit()
        return f"Sale recorded successfully for customer '{customer_name}'!"
    except sqlite3.Error as e:
        return f"Error during sale: {e}"

def search_inventory(car_model=''):
    try:
        if car_model:
            result = conn.execute('SELECT * FROM inventory WHERE car_model LIKE ?', (f"%{car_model}%",)).fetchall()
        else:
            result = conn.execute('SELECT * FROM inventory').fetchall()
        return result if result else "No matching cars found."
    except sqlite3.Error as e:
        return f"Error during search: {e}"

def check_availability():
    try:
        result = conn.execute('SELECT car_model, stock FROM inventory').fetchall()
        if not result:
            return "No cars in inventory."
        return "\n".join([f"{car_model}: {stock} in stock" for car_model, stock in result])
    except sqlite3.Error as e:
        return f"Error checking availability: {e}"

# Tkinter GUI Setup
root = tk.Tk()
root.title("Car Dealership Management System")
root.geometry("600x400")

notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

add_car_frame = ttk.Frame(notebook)
sell_car_frame = ttk.Frame(notebook)
search_frame = ttk.Frame(notebook)
availability_frame = ttk.Frame(notebook)

notebook.add(add_car_frame, text="Add Car")
notebook.add(sell_car_frame, text="Sell Car")
notebook.add(search_frame, text="Search Inventory")
notebook.add(availability_frame, text="Availability")

# Add Car GUI
ttk.Label(add_car_frame, text="Car Model:").grid(row=0, column=0, padx=5, pady=5)
car_model_entry = ttk.Entry(add_car_frame)
car_model_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(add_car_frame, text="Car Type:").grid(row=1, column=0, padx=5, pady=5)
car_type_combobox = ttk.Combobox(add_car_frame, values=["Car", "SUV", "Truck", "Electric Car"])
car_type_combobox.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(add_car_frame, text="Price ($) :").grid(row=2, column=0, padx=5, pady=5)
price_entry = ttk.Entry(add_car_frame)
price_entry.grid(row=2, column=1, padx=5, pady=5)

ttk.Label(add_car_frame, text="Stock:").grid(row=3, column=0, padx=5, pady=5)
stock_entry = ttk.Entry(add_car_frame)
stock_entry.grid(row=3, column=1, padx=5, pady=5)

ttk.Label(add_car_frame, text="License Plate:").grid(row=4, column=0, padx=5, pady=5)
license_plate_entry = ttk.Entry(add_car_frame)
license_plate_entry.grid(row=4, column=1, padx=5, pady=5)

def add_car_gui():
    car_model = car_model_entry.get()
    car_type = car_type_combobox.get()
    price = price_entry.get()
    stock = stock_entry.get()
    license_plate = license_plate_entry.get()

    if not car_model or not car_type or not price or not stock or not license_plate:
        messagebox.showerror("Error", "All fields are required.")
        return

    try:
        price = float(price)
        stock = int(stock)
        result = add_car(car_model, car_type, price, stock, license_plate)
        messagebox.showinfo("Add Car", result)
    except ValueError:
        messagebox.showerror("Error", "Invalid price or stock value. Please enter numeric values.")

ttk.Button(add_car_frame, text="Add Car", command=add_car_gui).grid(row=5, columnspan=2, pady=10)

# Sell Car GUI
ttk.Label(sell_car_frame, text="Car ID:").grid(row=0, column=0, padx=5, pady=5)
car_id_entry = ttk.Entry(sell_car_frame)
car_id_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(sell_car_frame, text="Customer Name:").grid(row=1, column=0, padx=5, pady=5)
customer_name_entry = ttk.Entry(sell_car_frame)
customer_name_entry.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(sell_car_frame, text="Contact:").grid(row=2, column=0, padx=5, pady=5)
contact_entry = ttk.Entry(sell_car_frame)
contact_entry.grid(row=2, column=1, padx=5, pady=5)

def sell_car_gui():
    car_id = car_id_entry.get()
    customer_name = customer_name_entry.get()
    contact = contact_entry.get()

    if not car_id or not customer_name or not contact:
        messagebox.showerror("Error", "All fields are required.")
        return

    try:
        car_id = int(car_id)
        result = sell_car(car_id, customer_name, contact)
        messagebox.showinfo("Sell Car", result)
    except ValueError:
        messagebox.showerror("Error", "Invalid Car ID. Please enter a numeric value.")

ttk.Button(sell_car_frame, text="Sell Car", command=sell_car_gui).grid(row=3, columnspan=2, pady=10)

# Search Inventory GUI
ttk.Label(search_frame, text="Car Model:").grid(row=0, column=0, padx=5, pady=5)
search_entry = ttk.Entry(search_frame)
search_entry.grid(row=0, column=1, padx=5, pady=5)

def search_inventory_gui():
    car_model = search_entry.get()
    result = search_inventory(car_model)
    if isinstance(result, str):
        messagebox.showinfo("Search Inventory", result)
    else:
        message = "\n".join([f"ID: {r[0]}, Model: {r[1]}, Type: {r[2]}, Price: ${r[3]}, Stock: {r[4]}" for r in result])
        messagebox.showinfo("Search Inventory", message)

ttk.Button(search_frame, text="Search", command=search_inventory_gui).grid(row=1, columnspan=2, pady=10)

# Availability GUI
def show_availability():
    result = check_availability()
    messagebox.showinfo("Availability", result)

ttk.Button(availability_frame, text="Check Availability", command=show_availability).pack(pady=10)

# Initialize database and run the application
initialize_database()
root.mainloop()
