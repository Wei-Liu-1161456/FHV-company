from typing import Dict, List
from decimal import Decimal
from view.login import Login
import os
from decimal import ROUND_HALF_UP
import pickle
from model import *

# The Company class is the controller class that manages the data and business logic of the application
class Company:
    def __init__(self):
        '''Initializes the Company class with product data, box configurations, and user data'''

        # Initialize product data lists
        self.all_veggies_list = []  # Store all vegetables
        self.veggies_weight_list = []  # Store vegetables sold by weight
        self.veggies_unit_list = []    # Store vegetables sold by unit
        self.veggies_pack_list = []    # Store vegetables sold by pack
        self._parse_veggies()
        
        # Initialize box configurations
        self.smallbox_default_dict = {'price': Decimal('0'), 'contents': []}
        self.mediumbox_default_dict = {'price': Decimal('0'), 'contents': []}
        self.largebox_default_dict = {'price': Decimal('0'), 'contents': []}
        self._parse_premadeboxes()

        # Load user data from pickle files
        self.private_customers = self.load_data("data/private_customers.pkl")
        self.corporate_customers = self.load_data("data/corporate_customers.pkl")
        self.staff_members = self.load_data("data/staffs.pkl")

    def load_data(self, filename):
        """Load data from pickle files"""
        with open(filename, 'rb') as file:
            return pickle.load(file)

    def _parse_veggies(self):
        """Parse vegetables data from veggies.txt"""
        try:
            if not os.path.exists('static/veggies.txt'):
                raise FileNotFoundError("static/veggies.txt file not found")
                
            with open('static/veggies.txt', 'r') as f:
                lines = f.readlines()
            
            current_type = None
            for line in lines:
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                    
                if line.startswith('['):
                    current_type = line[1:-1]  # Remove brackets
                elif '=' in line and current_type:
                    name, price = line.split('=')
                    name = name.strip()
                    price_decimal = Decimal(price.strip()).quantize(
                        Decimal('0.01'), rounding=ROUND_HALF_UP
                    )
                    formatted_item = f"{name} - ${float(price_decimal):.2f}"
                    
                    # Add to appropriate lists based on sales type
                    self.all_veggies_list.append(formatted_item)
                    
                    if 'weight/kg' in name:
                        self.veggies_weight_list.append(formatted_item)
                    elif 'unit' in name:
                        self.veggies_unit_list.append(formatted_item)
                    elif 'pack' in name:
                        self.veggies_pack_list.append(formatted_item)

        except FileNotFoundError as e:
            print(f"File Error: {str(e)}")
            raise
            
    def _parse_premadeboxes(self):
        """Parse premade box configurations from premadeboxes.txt"""
        try:
            if not os.path.exists('static/premadeboxes.txt'):
                raise FileNotFoundError("static/premadeboxes.txt file not found")
                
            with open('static/premadeboxes.txt', 'r') as f:
                lines = f.readlines()
            
            current_size = None
            for line in lines:
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                    
                if line.startswith('['):
                    current_size = line[1:-1].lower()
                elif '=' in line and current_size:
                    key, value = line.split('=')
                    key = key.lower()
                    
                    if key == 'price':
                        # Save box price
                        box_dict = getattr(self, f"{current_size}box_default_dict")
                        box_dict['price'] = Decimal(value.strip()).quantize(
                            Decimal('0.01'), rounding=ROUND_HALF_UP
                        )
                    elif key.startswith('item'):
                        # Save box contents
                        box_dict = getattr(self, f"{current_size}box_default_dict")
                        box_dict['contents'].append(value.strip())
                        
        except FileNotFoundError as e:
            print(f"File Error: {str(e)}")
            raise

    def get_user(self, username, user_type):
        """Get user object based on username and user type from corresponding pickle file"""
        if user_type == "staff":
            for staff in self.staff_members.values():
                if staff.username == username:
                    self.user = staff
        if user_type == "private":
            for private_customer in self.private_customers.values():
                if private_customer.username == username:
                    self.private_customers = private_customer
        if user_type == "corporate":
            for corporate_customer in self.corporate_customers.values():
                if corporate_customer.username == username:
                    self.user = corporate_customer

    # Login verification function
    def user_login(self,username,password):
        """Handle user login process"""
        
        # Check staffs
        for staff in self.staff_members.values():  # Changed to iterate through staffs
            if (staff.username == username and 
                staff.password == password):
                self.user = staff
                return staff, "staff"

        # Check private customers
        for customer in self.private_customers.values():
            if (customer.username == username and 
                customer.password == password):
                self.user = customer
                return customer, "customer"
        
        # Check corporate customers
        for customer in self.corporate_customers.values():
            if (customer.username == username and 
                customer.password == password):
                self.user = customer
                return customer, "customer"
        
        return None, None
    
    # Staff Methods        
    def staff_all_products(self):
        '''the products txt files are the data of the company, not belong to the staff.
        So the staff shouldn't parse the products data from its model.'''

        """Allow staff to view all products"""
        text = "Products Catalog \n"
        text += "\n All Vegetables:\n"
        text += "\n".join([f"• {item}" for item in self.all_veggies_list])
        
        text += "\n\n Pre-made Boxes:\n"
        text += f"\n Small Box (${float(self.smallbox_default_dict['price']):.2f})\n"
        text += f"  Contents: {', '.join(self.smallbox_default_dict['contents'])}"
        
        text += f"\n Medium Box (${float(self.mediumbox_default_dict['price']):.2f})\n"
        text += f"  Contents: {', '.join(self.mediumbox_default_dict['contents'])}"
        
        text += f"\n Large Box (${float(self.largebox_default_dict['price']):.2f})\n"
        text += f"  Contents: {', '.join(self.largebox_default_dict['contents'])}"

        return text

    def staff_current_orders(self):
        """Allow staff to view and manage current orders"""
        return self.user.show_current_orders()
    
    def staff_fullfill_order(self, order_id):
        """Process and fulfill customer orders"""
        return self.user.fulfill_order(order_id)

    def staff_previous_orders(self):
        """Allow staff to view previous orders"""
        return self.user.show_previous_orders()

    def staff_all_customers(self):
        """Allow staff to view all customers"""
        return self.user.show_all_customers()

    def staff_sales_report(self, start_date, end_date):
        """Generate and view sales reports"""
        return self.user.show_sales_report(start_date, end_date)

    def staff_popular_items(self):
        """View popular items"""
        return self.user.show_popular_products()

    def staff_fulfill_order(self, order_id):
        """Process and fulfill customer orders"""
        return self.user.fulfill_order(order_id)

    # Customer Methods
    def check_out_with_payment(self, data):
        """Process customer checkout and payment"""
        return self.user.check_out_with_payment(data)

    def customer_make_payment(self,amount):
        """Process customer payment"""
        return self.user.process_payment(amount)

    def customer_current_orders(self, customer):
        """Allow customers to view their current orders"""
        return customer.view_current_orders()

    def customer_previous_orders(self,customer):
        """Allow customers to view their order history"""
        return customer.view_previous_orders()