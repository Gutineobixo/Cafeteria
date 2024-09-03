import tkinter as tk
from tkinter import messagebox
import datetime
import os
import matplotlib.pyplot as plt
from tkcalendar import DateEntry
from tkinter import ttk 
from idlelib.tooltip import Hovertip

goal_amount = 0

def register_data():
    # Collecting data from the fields
    customer_name = entry_name.get()
    order = entry_order.get()
    order_price = entry_price.get()
    observations = text_observations.get("1.0", tk.END).strip()
    order_date = date_entry.get_date().strftime('%Y%m%d')  # Ensure date is in YYYYMMDD format

    if not customer_name or not order or not order_price:
        messagebox.showwarning("Warning", "All fields must be filled out!")
        return

    # Creating a unique filename using the selected date and time
    filename = f"Order_{customer_name}_{order_date}_{datetime.datetime.now().strftime('%H%M%S')}.txt"

    # Saving the data to a text file
    with open(filename, 'w') as file:
        file.write(f"Customer: {customer_name}\n")
        file.write(f"Order: {order}\n")
        file.write(f"Price: €{order_price}\n")
        file.write(f"Order Date: {order_date}\n")
        file.write(f"Observations: {observations}\n")

    messagebox.showinfo("Success", f"Data successfully registered in {filename}")
    
    # Update progress after registering data
    update_progress()

    # Clear fields
    clear_fields()

# Add the new functions here
def save_goal():
    global goal_amount
    try:
        goal_amount = float(goal_entry.get())
        progress_bar['maximum'] = goal_amount
        messagebox.showinfo("Goal Saved", f"Goal of €{goal_amount:.2f} has been saved!")
    except ValueError:
        messagebox.showwarning("Invalid Input", "Please enter a valid number for the goal.")

def update_progress():
    current_progress = 0.0

    # Calculate the current progress from all registered orders
    for file in os.listdir():
        if file.startswith("Order_"):
            with open(file, 'r') as f:
                content = f.read()
                for line in content.splitlines():
                    if line.startswith("Price: €"):
                        price = float(line.split("€")[1].replace(',', '.'))
                        current_progress += price

    # Update the progress bar
    progress_bar['value'] = current_progress
    if goal_amount > 0:
        progress_percentage = (current_progress / goal_amount) * 100
        progress_label.config(text=f"Progress: {progress_percentage:.2f}%")
        hovertip.text = f"{progress_percentage:.2f}% of the goal achieved"
    else:
        progress_label.config(text="Set a goal to start tracking progress.")
        hovertip.text = "No goal set"

def clear_fields():
    entry_name.delete(0, tk.END)
    entry_order.delete(0, tk.END)
    entry_price.delete(0, tk.END)
    text_observations.delete("1.0", tk.END)
    date_entry.set_date(datetime.datetime.now())

def validate_price(event):
    price = entry_price.get()
    
    # Allow only numbers and one comma or period for decimal
    if not price.replace(',', '', 1).replace('.', '', 1).isdigit():
        entry_price.delete(len(entry_price.get())-1, tk.END)
        messagebox.showwarning("Warning", "Please enter a valid number in the Price field (e.g., 10.50 or 10,50).")

def search_record():
    customer_name = entry_name.get()
    if not customer_name:
        messagebox.showwarning("Warning", "Please enter the customer name to search.")
        return

    found_records = []
    for file in os.listdir():
        if file.startswith(f"Order_{customer_name}_"):
            found_records.append(file)

    if found_records:
        records = "\n".join(found_records)
        messagebox.showinfo("Records Found", f"Found records:\n\n{records}")
    else:
        messagebox.showinfo("No Records Found", "No records found for this customer.")
        
def generate_weekly_report():
    selected_date = date_entry.get_date()
    start_of_week = selected_date - datetime.timedelta(days=selected_date.weekday())
    end_of_week = start_of_week + datetime.timedelta(days=6)
    
    weekly_records = []
    weekly_profit = 0.0

    for file in os.listdir():
        try:
            file_date_str = file.split('_')[2]
            file_date = datetime.datetime.strptime(file_date_str, '%Y%m%d').date()  # Convert to date
            if start_of_week <= file_date <= end_of_week:
                weekly_records.append(file)
        except (IndexError, ValueError):
            continue

    if weekly_records:
        report_name = f"Weekly_Report_{start_of_week.strftime('%Y%m%d')}_to_{end_of_week.strftime('%Y%m%d')}.txt"
        with open(report_name, 'w') as report:
            report.write(f"Weekly Report - {start_of_week.strftime('%d/%m/%Y')} to {end_of_week.strftime('%d/%m/%Y')}\n\n")
            for record in weekly_records:
                with open(record, 'r') as rec:
                    content = rec.read()
                    report.write(content + "\n\n")
                    # Extract the order price and add to the weekly profit
                    for line in content.splitlines():
                        if line.startswith("Price: €"):
                            price = float(line.split("€")[1].replace(',', '.'))
                            weekly_profit += price

            report.write(f"Total Weekly Profit: €{weekly_profit:.2f}\n")

        messagebox.showinfo("Report Generated", f"Weekly report successfully generated: {report_name}")
    else:
        messagebox.showinfo("No Records This Week", "No records found for this week.")

# Graph configuration function (as before)

def generate_weekly_chart():
    # Get the selected date from the date entry widget
    selected_date = date_entry.get_date()

    # Calculate the start and end of the week based on the selected date
    start_of_week = selected_date - datetime.timedelta(days=selected_date.weekday())
    end_of_week = start_of_week + datetime.timedelta(days=6)

    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekly_profit = [0.0] * 7

    # Iterate over the days in the selected week
    for i in range(7):
        day = (start_of_week + datetime.timedelta(days=i)).strftime('%Y%m%d')
        for file in os.listdir():
            if file.startswith(f"Order_") and day in file:
                with open(file, 'r') as rec:
                    content = rec.read()
                    for line in content.splitlines():
                        if line.startswith("Price: €"):
                            price = float(line.split("€")[1].replace(',', '.'))
                            weekly_profit[i] += price

    plt.figure(figsize=(10, 6))
    plt.bar(days_of_week, weekly_profit, color='#4CAF50', edgecolor='white')

    # Graph customization
    plt.xlabel('Day of the Week', fontsize=14, color='#333333', labelpad=15)
    plt.ylabel('Profit in €', fontsize=14, color='#333333', labelpad=15)
    plt.title(f'Total Weekly Profit ({start_of_week.strftime("%d/%m/%Y")} - {end_of_week.strftime("%d/%m/%Y")})', fontsize=18, color='#333333', pad=20)
    plt.xticks(fontsize=12, color='#333333')
    plt.yticks(fontsize=12, color='#333333')

    # Remove graph borders for a minimalist design
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_color('#DDDDDD')
    plt.gca().spines['bottom'].set_color('#DDDDDD')
    
    # Add value labels on the bars
    for i, v in enumerate(weekly_profit):
        plt.text(i, v + 0.02, f"€{v:.2f}", ha='center', va='bottom', fontsize=12, color='#333333')

    # Light background for a smooth effect
    plt.gca().set_facecolor('#F9F9F9')
    plt.grid(True, which='major', axis='y', linestyle='--', color='#DDDDDD')

    plt.tight_layout()
    plt.show()


# Graphical interface configuration
root = tk.Tk()
root.title("Order Registration - Cafeteria")

# Configure responsiveness
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=2)
root.grid_rowconfigure(4, weight=1)

# Labels and entries for registration
tk.Label(root, text="Customer:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
entry_name = tk.Entry(root)
entry_name.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

tk.Label(root, text="Order:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_order = tk.Entry(root)
entry_order.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

tk.Label(root, text="Price:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
entry_price = tk.Entry(root)
entry_price.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
entry_price.bind("<KeyRelease>", validate_price)

tk.Label(root, text="Order Date:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
date_entry = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2, year=datetime.datetime.now().year)
date_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

tk.Label(root, text="Observations:").grid(row=4, column=0, padx=10, pady=5, sticky="nw")
text_observations = tk.Text(root, height=5, width=30)
text_observations.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

# Goal Setting Section
tk.Label(root, text="Set Financial Goal:").grid(row=8, column=0, padx=10, pady=5, sticky="w")
goal_entry = tk.Entry(root)
goal_entry.grid(row=8, column=1, padx=10, pady=5, sticky="ew")

progress_label = tk.Label(root, text="Set a goal to start tracking progress.")
progress_label.grid(row=10, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

# Progress Bar Section
progress_label = tk.Label(root, text="Set a goal to start tracking progress.")
progress_label.grid(row=10, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.grid(row=11, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.grid(row=11, column=0, columnspan=2, padx=10, pady=5, sticky="ew")


# Buttons
btn_register = tk.Button(root, text="Register", command=register_data)
btn_register.grid(row=5, column=0, padx=10, pady=10, sticky="ew")

btn_search = tk.Button(root, text="Search Record", command=search_record)
btn_search.grid(row=5, column=1, padx=10, pady=10, sticky="ew")

btn_report = tk.Button(root, text="Generate Weekly Report", command=generate_weekly_report)
btn_report.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

btn_chart = tk.Button(root, text="View Weekly Profit", command=generate_weekly_chart)
btn_chart.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

btn_save_goal = tk.Button(root, text="Save Goal", command=save_goal)
btn_save_goal.grid(row=9, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

# Change this button to refresh the progress bar
btn_refresh_chart = tk.Button(root, text="Refresh Progress", command=update_progress)
btn_refresh_chart.grid(row=12, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

hovertip = Hovertip(progress_bar, "No goal set", hover_delay=100)

# Main loop of the graphical interface
root.mainloop()