import sys
import os
import tkinter as tk
from tkinter import messagebox, ttk
import pickle
from model import Person, Staff, Customer, CorporateCustomer
from .customer_home import CustomerHome
from .staff_home import StaffHome

class Login:
    """Login class handles user authentication and provides the login interface"""

    def __init__(self, controller):
        """Initialize the login interface and user data
        
        Args:
            controller: Main application controller instance
        """
        # Get the controller and user data
        self.controller = controller
        self.private_customers = self.controller.private_customers
        self.corporate_customers = self.controller.corporate_customers
        self.staff_members = self.controller.staff_members

        # Create and configure the main window
        self.root = tk.Tk()
        self.root.title("FHV Company - Login")
        self.root.resizable(False, False)  # Disable window resizing
        
        # Get user information from controller
        self.private_customers = controller.private_customers
        self.corporate_customers = controller.corporate_customers
        self.staff_members = controller.staff_members

        # Set up the user interface
        self.create_widgets()

    def get_user_info(self):
        """Collect and format user credentials for display"""
        user_info = []
        
        # Format and add staff credentials
        for staff in self.staff_members.values():
                user_info.append(f"{staff.username}, {staff.password}")

        # Format and add private customer credentials
        for customer in self.private_customers.values():
            user_info.append(f"{customer.username}, {customer.password}")

        # Format and add corporate customer credentials
        for customer in self.corporate_customers.values():
            user_info.append(f"{customer.username}, {customer.password}")

        return user_info

    def login(self):
        """Handle user login process"""
        # Get entered credentials
        username = self.entry_username.get()
        password = self.entry_password.get()
        
        # Validate credentials and get user type
        user, user_type = self.controller.user_login(username, password)
        
        if user:
            # Hide login window
            self.root.withdraw()
            
            # Create new window for home interface
            new_window = tk.Toplevel(self.root)
            
            # Open appropriate home interface based on user type
            if user_type == "staff":
                StaffHome(new_window, user, self.controller)
            else:
                CustomerHome(new_window, user, self.controller)
        else:
            messagebox.showerror("Login Failed", 
                               "Invalid username or password.")
            
    def on_closing(self, window):
        """Handle window closing event"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            window.destroy()
            self.root.destroy()

    def exit_application(self):
        """Exit the application"""
        self.root.quit()

    def create_widgets(self):
        """Create and layout all UI elements"""
        # Configure window dimensions
        window_width = 400
        window_height = 460

        # Calculate center position
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)

        # Set window geometry
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        # Create main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create username input area
        frame_username = ttk.Frame(main_frame)
        frame_username.pack(pady=5)
        ttk.Label(frame_username, text="Username:").pack(side=tk.LEFT)
        self.entry_username = ttk.Entry(frame_username)
        self.entry_username.insert(0, "staffJD")  # Default test username
        self.entry_username.pack(side=tk.LEFT, padx=5)

        # Create password input area
        frame_password = ttk.Frame(main_frame)
        frame_password.pack(pady=5)
        ttk.Label(frame_password, text="Password:").pack(side=tk.LEFT)
        self.entry_password = ttk.Entry(frame_password, show="*")
        self.entry_password.insert(0, "12345")  # Default test password
        self.entry_password.pack(side=tk.LEFT, padx=5)

        # Create button area
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Log In", command=self.login).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exit", command=self.exit_application).pack(side=tk.LEFT)

        # Display available usernames and passwords section
        ttk.Label(main_frame, text="Available Usernames and Passwords for Testing:").pack(pady=5)
        hint_text = tk.Text(main_frame, height=10, width=40, wrap=tk.WORD)
        hint_text.pack(pady=5)

        # Display available credentials
        user_info = self.get_user_info()
        for info in user_info:
            hint_text.insert(tk.END, f"{info}\n")
            
        # Add system notes at the end of credentials
        hint_text.insert(tk.END, "\nNotes:\n")
        hint_text.insert(tk.END, "This system is developed by mac OS, please run it on mac OS. ")
        # hint_text.insert(tk.END, "The function of canceling orders is missing.")
        
        hint_text.config(state='disabled')  # Make text read-only

    def run(self):
        """Start the login window main loop"""
        self.root.mainloop()