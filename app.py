import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd

class ContactApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Contact Web App Generator")

        self.locations = []
        self.contacts_per_location = {}
        self.current_location_index = 0
        self.password = ""

        self.setup_menu()
        self.setup_main_frame()

    def setup_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Import", command=self.import_xlsx)
        file_menu.add_command(label="Import Template", command=self.create_import_template)
        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)

    def setup_main_frame(self):
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        tk.Label(frame, text="Number of Locations:").grid(row=0, column=0, padx=5, pady=5)
        self.num_locations_entry = tk.Entry(frame)
        self.num_locations_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Button(frame, text="Set Locations", command=self.set_locations).grid(row=0, column=2, padx=5, pady=5)

    def import_xlsx(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if not file_path:
            return
        
        try:
            df = pd.read_excel(file_path)
            required_columns = {'Location', 'Contact Name', 'Contact Number', 'Contact Type'}
            if not required_columns.issubset(df.columns):
                messagebox.showerror("Invalid File", f"The file must contain the following columns: {', '.join(required_columns)}")
                return

            self.locations = df['Location'].unique().tolist()
            self.contacts_per_location = {loc: {"name": loc, "contacts": []} for loc in self.locations}

            for loc in self.locations:
                location_contacts = df[df['Location'] == loc]
                contacts = [{"name": row["Contact Name"], "number": str(row["Contact Number"]), "type": row["Contact Type"]} for _, row in location_contacts.iterrows()]
                self.contacts_per_location[loc]["contacts"] = contacts

            self.show_password_entry()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import file: {e}")

    def create_import_template(self):
        template_data = {
            "Location": [],
            "Contact Name": [],
            "Contact Number": [],
            "Contact Type": []
        }

        fake_locations = ["Fake Location 1", "Fake Location 2", "Fake Location 3"]
        fake_contacts = [
            {"name": "Contact 1", "number": "123456", "type": "home"},
            {"name": "Contact 2", "number": "654321", "type": "cell"},
            {"name": "Contact 3", "number": "111222", "type": "home"}
        ]

        for loc in fake_locations:
            for contact in fake_contacts:
                template_data["Location"].append(loc)
                template_data["Contact Name"].append(contact["name"])
                template_data["Contact Number"].append(contact["number"])
                template_data["Contact Type"].append(contact["type"])

        df = pd.DataFrame(template_data)
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Success", f"Template saved to {file_path}")

    def set_locations(self):
        try:
            num_locations = int(self.num_locations_entry.get())
            self.locations = [f"Location {i+1}" for i in range(num_locations)]
            self.contacts_per_location = {loc: [] for loc in self.locations}

            self.num_locations_entry.config(state=tk.DISABLED)
            self.show_location_entries()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number.")

    def show_location_entries(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        self.location_entries = {}
        for idx, loc in enumerate(self.locations):
            tk.Label(frame, text=f"{loc} Name:").grid(row=idx, column=0, padx=5, pady=5)
            entry = tk.Entry(frame)
            entry.grid(row=idx, column=1, padx=5, pady=5)
            self.location_entries[loc] = entry

        tk.Button(frame, text="Next", command=self.set_contacts).grid(row=len(self.locations), columnspan=2, pady=10)

    def set_contacts(self):
        for loc in self.locations:
            self.contacts_per_location[loc] = {"name": self.location_entries[loc].get(), "contacts": []}

        for widget in self.root.winfo_children():
            widget.destroy()

        self.show_contact_entries()

    def show_contact_entries(self):
        self.contact_entries = {}
        self.current_location_index = 0
        self.show_contact_entries_for_location(self.current_location_index)

    def show_contact_entries_for_location(self, index):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        loc = self.locations[index]
        tk.Label(frame, text=f"Number of Contacts for {loc}:").grid(row=0, column=0, padx=5, pady=5)
        num_contacts_entry = tk.Entry(frame)
        num_contacts_entry.grid(row=0, column=1, padx=5, pady=5)
        self.contact_entries[loc] = num_contacts_entry

        tk.Button(frame, text="Next", command=lambda: self.collect_contacts(index)).grid(row=1, columnspan=2, pady=10)

    def collect_contacts(self, index):
        loc = self.locations[index]
        try:
            num_contacts = int(self.contact_entries[loc].get())
            self.contacts_per_location[loc]["contacts"] = [{"name": "", "number": "", "type": ""} for _ in range(num_contacts)]
            self.show_contact_details_entries(index)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number.")

    def validate_contact_number(self, P):
        if P.isdigit() and len(P) <= 10:
            return True
        elif P == "":
            return True
        else:
            return False

    def show_contact_details_entries(self, index):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        loc = self.locations[index]
        num_contacts = len(self.contacts_per_location[loc]["contacts"])
        self.contact_details_entries = []

        vcmd = (self.root.register(self.validate_contact_number), '%P')

        for i in range(num_contacts):
            tk.Label(frame, text=f"Contact {i+1} Name:").grid(row=i*3, column=0, padx=5, pady=5)
            name_entry = tk.Entry(frame)
            name_entry.grid(row=i*3, column=1, padx=5, pady=5)

            tk.Label(frame, text=f"Contact {i+1} Number:").grid(row=i*3+1, column=0, padx=5, pady=5)
            number_entry = tk.Entry(frame, validate='key', validatecommand=vcmd)
            number_entry.grid(row=i*3+1, column=1, padx=5, pady=5)

            type_var = tk.StringVar()
            tk.Radiobutton(frame, text="Home", variable=type_var, value="home").grid(row=i*3+2, column=0, padx=5, pady=5)
            tk.Radiobutton(frame, text="Cell", variable=type_var, value="cell").grid(row=i*3+2, column=1, padx=5, pady=5)

            self.contact_details_entries.append((name_entry, number_entry, type_var))

        tk.Button(frame, text="Save Contacts", command=lambda: self.save_contacts(index)).grid(row=num_contacts*3, columnspan=2, pady=10)

    def save_contacts(self, index):
        loc = self.locations[index]
        for idx, (name_entry, number_entry, type_var) in enumerate(self.contact_details_entries):
            self.contacts_per_location[loc]["contacts"][idx] = {
                "name": name_entry.get(),
                "number": number_entry.get(),
                "type": type_var.get()
            }

        if index + 1 < len(self.locations):
            self.show_contact_entries_for_location(index + 1)
        else:
            messagebox.showinfo("Success", "All contacts saved!")
            self.show_password_entry()

    def show_password_entry(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        tk.Label(frame, text="Enter a Password for the Web App:").grid(row=0, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(frame, show='*')
        self.password_entry.grid(row=0, column=1, padx=5, pady=5)

        # Add a label to show Caps Lock warning
        self.caps_lock_warning = tk.Label(frame, text="", fg="red")
        self.caps_lock_warning.grid(row=1, column=0, columnspan=2, pady=5)

        # Bind KeyPress event to check for Caps Lock
        self.password_entry.bind('<KeyPress>', self.check_caps_lock)

        tk.Button(frame, text="Generate Files", command=self.save_password_and_generate_files).grid(row=2, columnspan=2, pady=10)

    def check_caps_lock(self, event):
        if event.state & 0x0002:
            self.caps_lock_warning.config(text="Caps Lock is ON")
        else:
            self.caps_lock_warning.config(text="")

    def save_password_and_generate_files(self):
        self.password = self.password_entry.get()
        if not self.password:
            messagebox.showerror("Error", "Password cannot be empty.")
            return

        html_content, flask_app_content, login_html_content = self.generate_combined_html_flask()

        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.join(base_dir, "contact_app")
        templates_dir = os.path.join(project_dir, "templates")

        os.makedirs(templates_dir, exist_ok=True)

        with open(os.path.join(templates_dir, "contacts.html"), "w") as html_file:
            html_file.write(html_content)

        with open(os.path.join(project_dir, "app.py"), "w") as flask_app_file:
            flask_app_file.write(flask_app_content)

        with open(os.path.join(templates_dir, "login.html"), "w") as login_html_file:
            login_html_file.write(login_html_content)

        messagebox.showinfo("Success", "Files generated successfully!")

    def format_phone_number(self, phone_number):
        cleaned = ''.join(filter(str.isdigit, phone_number))
        if len(cleaned) == 10:
            return f"({cleaned[:3]}) {cleaned[3:6]}-{cleaned[6:]}"
        else:
            return phone_number

    def consolidate_contacts(self, contacts):
        consolidated = {}
        for contact in contacts:
            name = contact['name']
            if name not in consolidated:
                consolidated[name] = []
            consolidated[name].append(contact)
        return consolidated

    def generate_combined_html_flask(self):
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contact Information</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background-color: #ffffff; /* Changed background color to white */
        }

        .container {
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            text-align: center;
        }

        select, .contact {
            border-radius: 8px;
        }

        .contact {
            border: 1px solid #ccc;
            font-weight: bold;
            padding: 2px; /* Reduced padding */
            margin: 2px 0; /* Reduced margin */
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .contact div {
            display: flex;
            align-items: center;
            margin-top: 1px; /* Reduced margin between contact numbers */
        }

        .contact img {
            margin-left: 5px; /* Reduced margin between number and icon */
            width: 35px;
            height: auto;
        }

        select {
            width: 200px;  /* Adjust this value to change the width of the combobox */
            padding: 10px; /* Adjust this value to change the padding of the combobox */
            font-size: 16px; /* Adjust this value to change the font size of the combobox */
        }

        /* Add this section to change the color of the phone number font */
        .contact a {
            color: #053856;  /* Change 'red' to your desired color */
        }

        /* Add this section to change the font size and color for contact names */
        .contact p {
            color: #6E98AD;  /* Change 'blue' to your desired color */
            font-size: 18px;  /* Change '18px' to your desired font size */
        }

        .caps-lock-warning {
            display: none;
            color: red;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Contact Information</h1>
        <select id="location-select" onchange="displayContacts()">
            <option value="">--Select a Location--</option>
"""
        for loc in self.locations:
            html_content += f'            <option value="{loc}">{self.contacts_per_location[loc]["name"]}</option>\n'

        html_content += """
        </select>
        <div id="contact-list"></div>
    </div>
    <script>
const contacts = {
"""

        for loc in self.locations:
            html_content += f'    "{loc}": [\n'
            consolidated_contacts = self.consolidate_contacts(self.contacts_per_location[loc]["contacts"])
            for name, contact_list in consolidated_contacts.items():
                numbers = [{'number': self.format_phone_number(contact["number"]), 'type': contact['type']} for contact in contact_list]
                html_content += f'        {{"name": "{name}", "numbers": {numbers}}},\n'
            html_content += "    ],\n"

        html_content += """
};

function displayContacts() {
    const locationSelect = document.getElementById("location-select");
    const contactList = document.getElementById("contact-list");
    const selectedLocation = locationSelect.value;

    contactList.innerHTML = "";

    if (contacts[selectedLocation]) {
        contacts[selectedLocation].forEach(contact => {
            const contactDiv = document.createElement("div");
            contactDiv.classList.add("contact");

            const nameP = document.createElement("p");
            nameP.textContent = `${contact.name}`;
            contactDiv.appendChild(nameP);

            contact.numbers.forEach((numberObj, index) => {
                const numberDiv = document.createElement("div");

                const numberP = document.createElement("p");
                numberP.innerHTML = `<a href="tel:${numberObj.number}">${numberObj.number}</a>`;
                numberDiv.appendChild(numberP);

                const iconImg = document.createElement("img");
                iconImg.src = numberObj.type === 'home' ? "{{ url_for('static', filename='home.svg') }}" : "{{ url_for('static', filename='cell.svg') }}";
                iconImg.alt = numberObj.type;
                numberDiv.appendChild(iconImg);

                contactDiv.appendChild(numberDiv);
            });

            contactList.appendChild(contactDiv);
        });
    }
}

document.addEventListener("DOMContentLoaded", function() {
    const passwordInput = document.querySelector('input[type="password"]');
    const capsLockWarning = document.createElement('div');
    capsLockWarning.classList.add('caps-lock-warning');
    capsLockWarning.textContent = 'Caps Lock is ON';
    passwordInput.parentNode.insertBefore(capsLockWarning, passwordInput.nextSibling);

    passwordInput.addEventListener('keydown', function(event) {
        if (event.getModifierState('CapsLock')) {
            capsLockWarning.style.display = 'block';
        } else {
            capsLockWarning.style.display = 'none';
        }
    });

    passwordInput.addEventListener('keyup', function(event) {
        if (!event.getModifierState('CapsLock')) {
            capsLockWarning.style.display = 'none';
        }
    });
});
    </script>
</body>
</html>
"""

        flask_app_content = f"""
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta
from collections import defaultdict
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secure random key for session encryption

PASSWORD = "{self.password}"
MAX_ATTEMPTS = 3
LOCKOUT_TIME = timedelta(minutes=10)
IP_LOCKOUT_DURATION = timedelta(hours=1)

failed_attempts = defaultdict(list)
locked_ips = {{}}

def is_ip_locked(ip):
    if ip in locked_ips:
        lockout_end = locked_ips[ip]
        if datetime.now() < lockout_end:
            return True
        else:
            del locked_ips[ip]
    return False

def log_failed_attempt(ip):
    failed_attempts[ip].append(datetime.now())
    if len(failed_attempts[ip]) > MAX_ATTEMPTS:
        failed_attempts[ip] = failed_attempts[ip][-MAX_ATTEMPTS:]

    attempts = failed_attempts[ip]
    if len(attempts) == MAX_ATTEMPTS and attempts[-1] - attempts[0] < LOCKOUT_TIME:
        locked_ips[ip] = datetime.now() + IP_LOCKOUT_DURATION
        failed_attempts[ip] = []

@app.route('/', methods=['GET', 'POST'])
def login():
    ip = request.remote_addr

    if is_ip_locked(ip):
        return render_template('login.html', message="Too many failed attempts. Please try again later.", disabled=True)

    if request.method == 'POST':
        password = request.form.get('password')
        if password == PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('contacts'))
        else:
            log_failed_attempt(ip)
            if is_ip_locked(ip):
                return render_template('login.html', message="Too many failed attempts. Please try again later.", disabled=True)
            else:
                return render_template('login.html', message="Incorrect password. Please try again.", disabled=False)

    return render_template('login.html', message="", disabled=False)

@app.route('/contacts')
def contacts():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    return render_template('contacts.html')

if __name__ == '__main__':
    app.run(debug=True)
"""

        login_html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #f5f5f5;
        }
        .login-container {
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        input[type="password"], input[type="submit"] {
            margin: 10px 0;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #ccc;
        }
        .caps-lock-warning {
            display: none;
            color: red;
            font-size: 12px;
        }
        .message {
            color: red;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>Login</h1>
        {% if message %}
        <div class="message">{{ message }}</div>
        {% endif %}
        <form method="post">
            <input type="password" name="password" placeholder="Enter Password" required {% if disabled %}disabled{% endif %}>
            <div class="caps-lock-warning">Caps Lock is ON</div>
            <input type="submit" value="Login" {% if disabled %}disabled{% endif %}>
        </form>
    </div>
    <script>
        document.addEventListener("DOMContentLoaded", function() {
            const passwordInput = document.querySelector('input[type="password"]');
            const capsLockWarning = document.querySelector('.caps-lock-warning');

            passwordInput.addEventListener('keydown', function(event) {
                if (event.getModifierState('CapsLock')) {
                    capsLockWarning.style.display = 'block';
                } else {
                    capsLockWarning.style.display = 'none';
                }
            });

            passwordInput.addEventListener('keyup', function(event) {
                if (!event.getModifierState('CapsLock')) {
                    capsLockWarning.style.display = 'none';
                }
            });
        });
    </script>
</body>
</html>
"""

        return html_content, flask_app_content, login_html_content

if __name__ == "__main__":
    root = tk.Tk()
    app = ContactApp(root)
    root.mainloop()
