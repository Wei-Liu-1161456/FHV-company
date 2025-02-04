from datetime import date
from typing import List, Dict, Any
from decimal import Decimal
from abc import ABC, abstractmethod
import pickle
from enum import Enum
from decimal import Decimal, ROUND_DOWN

# Constants for business rules
MAX_PRIVATE_CUSTOMER_OWING = Decimal('100.00')
DEFAULT_CORPORATE_DISCOUNT = Decimal('0.10')
DELIVERY_RADIUS_KM = 20
DELIVERY_FEE = Decimal('10.00')

class Person:
    '''Person class to store basic information about a person'''
    def __init__(self, first_name: str, last_name: str, username: str, password: str):
        """Initialize a person with basic information
        
        Args:
            first_name (str): Person's first name
            last_name (str): Person's last name
            username (str): Username for system login
            password (str): Password for system login
        """
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.password = password

class Staff(Person):
    '''Staff class to store information about a staff member'''
    def __init__(self, first_name: str, last_name: str, username: str, password: str, 
                 dept_name: str, date_joined: date, staff_ID: str):
        """Initialize a staff member
        
        Args:
            first_name (str): Staff's first name
            last_name (str): Staff's last name
            username (str): Username for system login
            password (str): Password for system login
            dept_name (str): Department name
            date_joined (date): Date when staff joined
            staff_ID (str): Unique staff identifier
        """
        super().__init__(first_name, last_name, username, password)
        self.dept_name = dept_name
        self.date_joined = date_joined
        self.staff_ID = staff_ID
    
    def __str__(self):
        """Return string representation of staff member"""
        return (f"Staff ID: {self.staff_ID}\n"
                f"Name: {self.first_name} {self.last_name}\n"
                f"Username: {self.username}\n"
                f"Department: {self.dept_name}\n"
                f"Date Joined: {self.date_joined}")


    def show_current_orders(self) -> Dict[str, Dict[str, Any]]:
            """Show all orders with 'pending' status
            
            Returns:
                Dict[str, Dict[str, Any]]: Dictionary containing pending orders with their details
            """

            # Load orders from pickle file
            try:
                with open('data/orders.pkl', 'rb') as file:
                    orders = pickle.load(file)
                    # Filter orders with pending status
                    pending_orders = {k: v for k, v in orders.items() 
                                    if v.order_status == OrderStatus.PENDING}
                    
                    # Create the result dictionary
                    current_orders = {
                        order.order_number: {
                            "Customer": f"{order.order_customer.first_name} {order.order_customer.last_name}",
                            "Date": order.order_date,
                            "Status": order.order_status.value,
                            "Items": self._get_order_items_string(order),
                            "Subtotal": order.subtotal,
                            "Delivery Fee": order.delivery_fee,
                            "Total Amount": order.total_amount
                        } 
                        # Format order details
                        for order in pending_orders.values()
                    }
                    
                    return current_orders
            except Exception as e:
                return {"Error": f"Error loading orders: {str(e)}"}

    def _get_order_items_string(self, order) -> str:
        """Helper method to format order items as string
        
        Args:
            order: Order object containing items to format
            
        Returns:
            str: Formatted string containing items details
        """

        # Initialize items string
        items_str = ""
        #  Iterate through each item in the order
        for item in order.list_of_items:
            # Check if the item is a premade box
            if hasattr(item, 'quantity'):
                # Format item with quantity
                items_str += f"{item.item_name} x {item.quantity} "
            else:
                # Format individual item
                items_str += f"{item.item_name} "
        return items_str

    def show_previous_orders(self) -> Dict[str, Dict[str, Any]]:
        """Show all orders with 'fulfilled' status
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary containing fulfilled orders with their details
        """

        # Load orders from pickle file
        try:
            with open('data/orders.pkl', 'rb') as file:
                orders = pickle.load(file)
                # Filter fulfilled orders
                fulfilled_orders = {k: v for k, v in orders.items() 
                                if v.order_status == OrderStatus.FULFILLED}
                
                # Create result dictionary
                previous_orders = {
                    order.order_number: {
                        "Customer": f"{order.order_customer.first_name} {order.order_customer.last_name}",
                        "Date": order.order_date,
                        "Status": order.order_status.value,
                        "Items": self._get_order_items_string(order),
                        "Subtotal": order.subtotal,
                        "Delivery Fee": order.delivery_fee,
                        "Total Amount": order.total_amount
                    } 
                    # Format order details
                    for order in fulfilled_orders.values()
                }
                
                return previous_orders
        except Exception as e:
            return {"Error": f"Error loading orders: {str(e)}"}
        
    def show_all_customers(self) -> str:
            """Show all customers (both private and corporate)
            
            Returns:
                str: Formatted string containing all customer information
            """
            try:
                # Load private customers
                with open('data/private_customers.pkl', 'rb') as file:
                    private_customers = pickle.load(file)
                
                # Load corporate customers
                with open('data/corporate_customers.pkl', 'rb') as file:
                    corporate_customers = pickle.load(file)
                
                # Initialize formatted strings for display
                formatted_customers = "\n=== Private Customers ===\n"
                for cust_id, customer in private_customers.items():
                    formatted_customers += (
                        f"\nCustomer ID: {cust_id}\n"
                        f"Name: {customer.first_name} {customer.last_name}\n"
                        f"Address: {customer.cust_address}\n"
                        f"Balance: ${customer.cust_balance}\n"
                        f"Max Owing: ${customer.max_owing}\n"
                    )
                
                formatted_customers += "\n=== Corporate Customers ===\n"
                for cust_id, customer in corporate_customers.items():
                    formatted_customers += (
                        f"\nCustomer ID: {cust_id}\n"
                        f"Name: {customer.first_name} {customer.last_name}\n"
                        f"Address: {customer.cust_address}\n"
                        f"Balance: ${customer.cust_balance}\n"
                        f"Max Owing: ${customer.max_owing}\n"
                        f"Discount Rate: {customer.discount_rate * 100}%\n"
                    )
                
                return formatted_customers
            except Exception as e:
                return "Error loading customers."

    def show_sales_report(self, start_date: date, end_date: date) -> str:
        """Generate a sales report for a specific date range.
        
        Args:
            start_date (date): Start date of the report period
            end_date (date): End date of the report period
            
        Returns:
            str: Formatted sales report containing:
                - Report header with date range
                - Total sales amount
                - Details for each order in the date range
        """
        try:
            # Load orders from pickle file
            with open('data/orders.pkl', 'rb') as file:
                orders = pickle.load(file)
            
            # Filter orders within the date range
            valid_orders = [
                order for order in orders.values()
                if start_date <= order.order_date <= end_date
            ]
            
            # Calculate total sales for the period
            total_sales = sum(order.sales_amount for order in valid_orders)
            
            # Initialize report string
            report = []
            report.append(f"=== Sales Report ({start_date} to {end_date}) ===")
            report.append(f"Total Sales: ${total_sales:.2f}\n")
            
            # Add details for each order
            for order in valid_orders:
                # Order header information
                report.append(f"Order Number: {order.order_number}")
                report.append(f"Customer: {order.order_customer.first_name} {order.order_customer.last_name}")
                report.append(f"Date: {order.order_date}")
                report.append(f"Delivery Method: {order.delivery_method.value}")
                
                # Add order items with proper handling of different types
                report.append("Items:")
                for item in order.list_of_items:
                    if isinstance(item, PremadeBox):
                        # Handle PremadeBox items
                        report.append(f"  - {item.item_name} (Box) x {item.quantity} x ${item.price:.2f}")
                        report.append("    Contents:")
                        # Add box contents
                        for content in item.box_content:
                            if isinstance(content, WeightedVeggie):
                                report.append(f"      * {content.item_name} ({content.weight}kg)")
                            elif isinstance(content, PackVeggie):
                                report.append(f"      * {content.item_name} ({content.num_of_pack} packs)")
                            elif isinstance(content, UnitPriceVeggie):
                                report.append(f"      * {content.item_name} ({content.quantity} units)")
                    else:
                        # Handle individual veggie items
                        if isinstance(item, WeightedVeggie):
                            report.append(f"  - {item.item_name}: {item.weight}kg x ${item.price_per_kilo:.2f}/kg")
                        elif isinstance(item, PackVeggie):
                            report.append(f"  - {item.item_name}: {item.num_of_pack} packs x ${item.price_per_pack:.2f}/pack")
                        elif isinstance(item, UnitPriceVeggie):
                            report.append(f"  - {item.item_name}: {item.quantity} units x ${item.price_per_unit:.2f}/unit")
                
                # Add pricing details
                report.append(f"Subtotal: ${order.subtotal:.2f}")
                if isinstance(order.order_customer, CorporateCustomer):
                    report.append(f"Corporate Discount ({order.order_customer.discount_rate * 100}%): ${order.discount:.2f}")
                report.append(f"Delivery Fee: ${order.delivery_fee:.2f}")
                report.append(f"Final Sales Amount: ${order.sales_amount:.2f}\n")
            
            return '\n'.join(report)
            
        except Exception as e:
            error_msg = f"Error generating sales report: {e}"
            print(error_msg)  # For debugging
            return error_msg

    def show_popular_products(self) -> str:
        """Show popular products based on quantity sold across different categories
        
        Returns:
            str: Formatted string listing popular products and their total quantities sold
        """
        try:
            # Load orders from pickle file
            with open('data/orders.pkl', 'rb') as file:
                orders = pickle.load(file)
            
            # Initialize dictionaries for product quantities
            veggie_sales = {}     # For all veggie products
            premade_box_sales = {} # For premade boxes

            # Count sales for each product
            for order in orders.values():
                for item in order.list_of_items:
                    # Handle veggie products
                    # Check the type of item and update the sales quantity
                    if isinstance(item, WeightedVeggie) or isinstance(item, UnitPriceVeggie) or isinstance(item, PackVeggie):
                        item_name = item.item_name
                        if isinstance(item, WeightedVeggie):
                            veggie_sales[item_name] = veggie_sales.get(item_name, 0) + item.weight
                        elif isinstance(item, UnitPriceVeggie):
                            veggie_sales[item_name] = veggie_sales.get(item_name, 0) + item.quantity
                        elif isinstance(item, PackVeggie):
                            veggie_sales[item_name] = veggie_sales.get(item_name, 0) + item.num_of_pack
                    
                    # Handle premade boxes
                    if isinstance(item, PremadeBox):
                        box_name = item.item_name
                        # Count the premade box
                        premade_box_sales[box_name] = premade_box_sales.get(box_name, 0) + item.quantity
                        
                        # Count box contents
                        for content in item.box_content:
                            content_name = content.item_name
                            if isinstance(content, WeightedVeggie):
                                veggie_sales[content_name] = veggie_sales.get(content_name, 0) + content.weight
                            elif isinstance(content, UnitPriceVeggie):
                                veggie_sales[content_name] = veggie_sales.get(content_name, 0) + content.quantity
                            elif isinstance(content, PackVeggie):
                                veggie_sales[content_name] = veggie_sales.get(content_name, 0) + content.num_of_pack

            # Sort sales data
            sorted_veggie_sales = sorted(veggie_sales.items(), key=lambda x: x[1], reverse=True)
            sorted_premade_box_sales = sorted(premade_box_sales.items(), key=lambda x: x[1], reverse=True)

            # Format the report
            formatted_products = "\n=== Popular Products by Category ===\n"
            formatted_products += "\n[Veggie Products]\n"
            # Add veggie sales
            for item_name, total_quantity in sorted_veggie_sales:
                formatted_products += f"{item_name}: {total_quantity:.2f} sold\n"

            formatted_products += "\n[Premade Boxes]\n"
            # Add premade box sales
            for box_name, quantity in sorted_premade_box_sales:
                formatted_products += f"{box_name}: {quantity} sold\n"

            return formatted_products
        
        except Exception as e:
            return f"Error generating popular products report: {e}"
        
    def fulfill_order(self, order_number: str) -> bool:
            """Update order status from pending to fulfilled
            
            Args:
                order_number (str): The order number to fulfill
                
            Returns:
                bool: True if successful, False otherwise
            """
            try:
                with open('data/orders.pkl', 'rb') as file:
                    orders = pickle.load(file)
                
                # Check if order exists
                order = orders.get(order_number)
                if not order:
                    return False
                
                # Update order status
                order.order_status = OrderStatus.FULFILLED
                orders[order_number] = order
                
                # Save updated orders
                with open('data/orders.pkl', 'wb') as file:
                    pickle.dump(orders, file)
                
                return True
            except Exception as e:
                print(f"Error fulfilling order: {e}")
                return False

class DeliveryMethod(Enum):
    """Enum for delivery methods"""
    PICKUP = "pickup"
    DELIVERY = "delivery"

class Customer(Person):
    def __init__(self, first_name: str, last_name: str, username: str, password: str, 
                 cust_address: str, cust_balance: Decimal, max_owing: Decimal, cust_id: str):
        """Initialize a customer
        
        Args:
            first_name (str): Customer's first name
            last_name (str): Customer's last name
            username (str): Username for system login
            password (str): Password for system login
            cust_address (str): Customer's delivery address
            cust_balance (Decimal): Current balance
            max_owing (Decimal): Maximum allowed owing amount
            cust_id (str): Unique customer identifier
        """
        super().__init__(first_name, last_name, username, password)
        self.cust_address = cust_address
        self.cust_balance = cust_balance
        self.max_owing = max_owing
        self.list_of_orders = []
        self.list_of_payments = []
        self.cust_id = cust_id
        # Determine delivery availability based on address
        try:
            distance = int(''.join(filter(str.isdigit, self.cust_address)))
            self.can_delivery = distance <= DELIVERY_RADIUS_KM
        except ValueError:
            self.can_delivery = False

    def __str__(self) -> str:
        """Return string representation of customer"""
        return (f"Customer ID: {self.cust_id}\n"
                f"Name: {self.first_name} {self.last_name}\n"
                f"Username: {self.username}\n"
                f"Address: {self.cust_address}\n"
                f"Balance: -${self.cust_balance:.2f}\n"
                f"Max Owing: ${self.max_owing:.2f}\n"
                f"Delivery Available: {'Yes' if self.can_delivery else 'No'}\n")

    def can_place_order(self, order_amount: Decimal) -> bool:
        """Check if customer can place order based on total amount and max owing limit
        
        Args:
            order_amount (Decimal): Amount of the potential order
            
        Returns:
            bool: True if customer can place order, False otherwise
        """
        try:
            with open('data/private_customers.pkl', 'rb') as file:
                customers = pickle.load(file)
                customer = customers.get(self.cust_id)
                if customer:
                    potential_balance = customer.cust_balance + order_amount
                    can_place = potential_balance <= customer.max_owing
                    return can_place
                return False
        except Exception as e:
            print(f"Error checking order possibility: {e}")
            return False


    def make_payment(self, *, payment_amount: Decimal, payment_date: date, 
                    payment_method: str, **kwargs) -> bool:
        """Make payment using credit or debit card"""
        try:
            # Initialize payments if file doesn't exist
            try:
                with open('data/payments.pkl', 'rb') as file:
                    payments = pickle.load(file)
            except FileNotFoundError:
                payments = {}
                
            # Create payment record
            if payment_method == "credit":
                payment = CreditCardPayment(
                    payment_amount=payment_amount,
                    payment_date=payment_date,
                    card_number=kwargs['card_number'],
                    card_type=kwargs['card_type'],
                    card_expiry_date=kwargs['card_expiry_date'], 
                    cvv=kwargs['cvv'],
                    card_holder=kwargs['card_holder']
                )
            elif payment_method == "debit":
                payment = DebitCardPayment(
                    payment_amount=payment_amount,
                    payment_date=payment_date,
                    bank_name=kwargs['bank_name'],
                    debit_card_num=kwargs['debit_card_num']
                )
            else:
                raise ValueError(f"Unsupported payment method: {payment_method}")

            # Save payment record
            payments[payment.payment_id] = payment
            with open('data/payments.pkl', 'wb') as file:
                pickle.dump(payments, file)

            return True
        except Exception as e:
            print(f"Error in make_payment: {str(e)}")
            return False


    def check_out_with_payment(self, order_data: dict, payment_method: str, *, 
                    card_number: str = None,
                    card_type: str = None, 
                    card_expiry_date: date = None,
                    cvv: str = None,
                    card_holder: str = None,
                    bank_name: str = None,
                    debit_card_num: str = None) -> bool:
        """Process checkout with immediate payment"""
        try:
            # Create Order instance first
            items = []
            for cart_item in order_data['cart_items']:
                item_type = cart_item['type']
                name = cart_item['name']
                price = cart_item['price']
                quantity = cart_item['quantity']
                
                if item_type == 'weight':
                    item = WeightedVeggie(name, quantity, price)
                elif item_type == 'unit':
                    item = UnitPriceVeggie(name, int(quantity), price)
                elif item_type == 'pack':
                    item = PackVeggie(name, int(quantity), price)
                elif item_type == 'box':
                    item = PremadeBox(name, int(quantity), price)
                    if cart_item['contents']:
                        contents = []
                        for content in cart_item['contents'].split(', '):
                            veg_name = content.split(' x ')[0]
                            contents.append(Veggie(veg_name))
                        item.set_content(contents)
                
                item.calculate_total()
                items.append(item)

            # Create order instance
            order = Order(
                order_customer=order_data['user'],
                order_date=date.today(),
                delivery_method=DeliveryMethod.DELIVERY if order_data['is_delivery'] else DeliveryMethod.PICKUP
            )
            order.set_items(items)

            # Process payment based on method
            if payment_method == "account":
                if not self.can_place_order(order.total_amount):
                    return False
                if not self.charge_to_account(order.total_amount):
                    return False
            else:
                # Handle credit/debit card payment
                success = self.make_payment(
                    payment_amount=order.total_amount,
                    payment_date=date.today(),
                    payment_method=payment_method,
                    card_number=card_number,
                    card_type=card_type,
                    card_expiry_date=card_expiry_date,
                    cvv=cvv,
                    card_holder=card_holder,
                    bank_name=bank_name,
                    debit_card_num=debit_card_num
                )
                
                if not success:
                    print("Payment processing failed")
                    return False

            try:
                # Load and save order
                with open('data/orders.pkl', 'rb') as file:
                    orders = pickle.load(file)
            except FileNotFoundError:
                orders = {}

            try:
                # Load and save customer
                with open('data/private_customers.pkl', 'rb') as file:
                    customers = pickle.load(file)
            except FileNotFoundError:
                customers = {}

            # Update order and save
            order.order_status = OrderStatus.PENDING
            self.list_of_orders.append(order)
            orders[order.order_number] = order
            customers[self.cust_id] = self

            # Save updates
            with open('data/orders.pkl', 'wb') as file:
                pickle.dump(orders, file)
            with open('data/private_customers.pkl', 'wb') as file:
                pickle.dump(customers, file)

            return True

        except Exception as e:
            print(f"Error in check_out_with_payment: {str(e)}")
            return False


    def check_out_with_payment(self, order_data: dict, payment_method: str, *, 
                    card_number: str = None,
                    card_type: str = None, 
                    card_expiry_date: date = None,
                    cvv: str = None,
                    card_holder: str = None,
                    bank_name: str = None,
                    debit_card_num: str = None) -> bool:
        """Process checkout with immediate payment"""
        try:
            # Create Order instance first
            items = []
            for cart_item in order_data['cart_items']:
                item_type = cart_item['type']
                name = cart_item['name']
                price = cart_item['price']
                quantity = cart_item['quantity']
                
                if item_type == 'weight':
                    item = WeightedVeggie(name, quantity, price)
                elif item_type == 'unit':
                    item = UnitPriceVeggie(name, int(quantity), price)
                elif item_type == 'pack':
                    item = PackVeggie(name, int(quantity), price)
                elif item_type == 'box':
                    item = PremadeBox(name, int(quantity), price)
                    if cart_item['contents']:
                        contents = []
                        for content in cart_item['contents'].split(', '):
                            # Extract veggie name and create appropriate veggie instance
                            veg_name = content.split(' x ')[0]
                            contents.append(UnitPriceVeggie(veg_name, 1, Decimal('0.00')))
                        item.set_content(contents)
                
                item.calculate_total()
                items.append(item)

            # Create order instance
            order = Order(
                order_customer=self,  # Use self as customer
                order_date=date.today(),
                delivery_method=DeliveryMethod.DELIVERY if order_data['is_delivery'] else DeliveryMethod.PICKUP
            )
            order.set_items(items)

            # Process payment based on method
            if payment_method == "account":
                if not self.can_place_order(order.total_amount):
                    return False
                if not self.charge_to_account(order.total_amount):
                    return False
            else:
                # Handle credit/debit card payment
                success = self.make_payment(
                    payment_amount=order.total_amount,
                    payment_date=date.today(),
                    payment_method=payment_method,
                    card_number=card_number,
                    card_type=card_type,
                    card_expiry_date=card_expiry_date,
                    cvv=cvv,
                    card_holder=card_holder,
                    bank_name=bank_name,
                    debit_card_num=debit_card_num
                )
                
                if not success:
                    print("Payment processing failed")
                    return False

            # Initialize dictionaries if files don't exist
            try:
                with open('data/orders.pkl', 'rb') as file:
                    orders = pickle.load(file)
            except FileNotFoundError:
                orders = {}

            try:
                with open('data/private_customers.pkl', 'rb') as file:
                    customers = pickle.load(file)
            except FileNotFoundError:
                customers = {}

            # Update order and save
            order.order_status = OrderStatus.PENDING
            self.list_of_orders.append(order)
            orders[order.order_number] = order
            customers[self.cust_id] = self

            # Save updates
            with open('data/orders.pkl', 'wb') as file:
                pickle.dump(orders, file)
            with open('data/private_customers.pkl', 'wb') as file:
                pickle.dump(customers, file)

            return True

        except Exception as e:
            print(f"Error in check_out_with_payment: {str(e)}")
            return False

    def charge_to_account(self, amount: Decimal) -> bool:
            """Charge amount to customer account
            
            Args:
                amount (Decimal): Amount to charge
                
            Returns:
                bool: True if charge successful, False otherwise
            """
            try:
                with open('data/private_customers.pkl', 'rb') as file:
                    customers = pickle.load(file)
                    if self.cust_id not in customers:
                        return False
                    
                    self.cust_balance += amount
                    customers[self.cust_id] = self
                    
                    with open('data/private_customers.pkl', 'wb') as file:
                        pickle.dump(customers, file)
                
                    return True
            except Exception as e:
                print(f"Error charging to account: {e}")
                return False

    def view_current_orders(self) -> Dict[str, Dict[str, Any]]:
        """View customer's current (pending) orders in a formatted dictionary
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary containing customer's pending orders with their details
        """
        try:
            with open('data/orders.pkl', 'rb') as file:
                orders = pickle.load(file)
                # Filter orders for current customer and pending status
                pending_orders = {
                    k: v for k, v in orders.items() 
                    if v.order_customer.cust_id == self.cust_id 
                    and v.order_status == OrderStatus.PENDING
                }
                
                # Create the result dictionary with the same format as staff view
                current_orders = {
                    order.order_number: {
                        "Customer": f"{order.order_customer.first_name} {order.order_customer.last_name}",
                        "Date": order.order_date,
                        "Status": order.order_status.value,
                        "Items": self._get_order_items_string(order),
                        "Subtotal": order.subtotal,
                        "Delivery Fee": order.delivery_fee,
                        "Total Amount": order.total_amount
                    } 
                    for order in pending_orders.values()
                }
                
                return current_orders
        except Exception as e:
            return {"Error": f"Error loading orders: {str(e)}"}

    def view_previous_orders(self) -> Dict[str, Dict[str, Any]]:
        """View customer's previous (fulfilled) orders in a formatted dictionary
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary containing customer's fulfilled orders with their details
        """
        try:
            with open('data/orders.pkl', 'rb') as file:
                orders = pickle.load(file)
                # Filter orders for current customer and fulfilled status
                fulfilled_orders = {
                    k: v for k, v in orders.items() 
                    if v.order_customer.cust_id == self.cust_id 
                    and v.order_status == OrderStatus.FULFILLED
                }
                
                # Create the result dictionary with the same format as staff view
                previous_orders = {
                    order.order_number: {
                        "Customer": f"{order.order_customer.first_name} {order.order_customer.last_name}",
                        "Date": order.order_date,
                        "Status": order.order_status.value,
                        "Items": self._get_order_items_string(order),
                        "Subtotal": order.subtotal,
                        "Delivery Fee": order.delivery_fee,
                        "Total Amount": order.total_amount
                    } 
                    for order in fulfilled_orders.values()
                }
                
                return previous_orders
        except Exception as e:
            return {"Error": f"Error loading orders: {str(e)}"}

    def _get_order_items_string(self, order) -> str:
        """Helper method to format order items as string
        
        Args:
            order: Order object containing items to format
            
        Returns:
            str: Formatted string containing items details
        """
        items_str = ""
        for item in order.list_of_items:
            if hasattr(item, 'quantity'):
                items_str += f"{item.item_name} x {item.quantity} "
            else:
                items_str += f"{item.item_name} "
        return items_str.strip()

    def process_payment(self, payment_amount: Decimal) -> bool:
            """Process payment to reduce customer balance
            
            Args:
                payment_amount (Decimal): Amount to reduce from balance
                
            Returns:
                bool: True if payment successful, False otherwise
            """
            try:
                with open('data/private_customers.pkl', 'rb') as file:
                    customers = pickle.load(file)
                    if self.cust_id not in customers:
                        return False
                    
                    # Ensure payment amount doesn't exceed current balance
                    if payment_amount > abs(self.cust_balance):
                        return False
                        
                    # Reduce balance by payment amount
                    self.cust_balance -= payment_amount  
                    customers[self.cust_id] = self
                    
                    with open('data/private_customers.pkl', 'wb') as file:
                        pickle.dump(customers, file)
                    
                    return True
            except Exception as e:
                print(f"Error processing payment: {e}")
                return False

class CorporateCustomer(Customer):
    def __init__(self, first_name: str, last_name: str, username: str, password: str, 
                 cust_address: str, cust_balance: Decimal, max_owing: Decimal, 
                 discount_rate: Decimal, corporate_cust_id: str):
        """Initialize a corporate customer
        
        Args:
            first_name (str): Customer's first name
            last_name (str): Customer's last name
            username (str): Username for system login
            password (str): Password for system login
            cust_address (str): Customer's delivery address
            cust_balance (Decimal): Current balance
            max_owing (Decimal): Maximum allowed owing amount
            discount_rate (Decimal): Corporate discount rate
            corporate_cust_id (str): Unique corporate customer identifier
        """
        super().__init__(first_name, last_name, username, password, 
                        cust_address, cust_balance, max_owing, corporate_cust_id)
        self.discount_rate = discount_rate

    def __str__(self) -> str:
        """String representation including discount rate"""
        base_str = super().__str__()
        return base_str[:-1] + f"\nDiscount Rate: {self.discount_rate:.0%}\n"

    def can_place_order(self, order_amount: Decimal) -> bool:
        """Check if corporate customer can place order based on total amount and max owing limit
        
        Args:
            order_amount (Decimal): Amount of the potential order
            
        Returns:
            bool: True if customer can place order, False otherwise
        """
        try:
            with open('data/corporate_customers.pkl', 'rb') as file:
                customers = pickle.load(file)
                customer = customers.get(self.cust_id)
                if customer:
                    potential_balance = customer.cust_balance + order_amount
                    can_place = potential_balance <= customer.max_owing
                    return can_place
                return False
        except Exception as e:
            print(f"Error checking order possibility: {e}")
            return False
        
    def process_payment(self, payment_amount: Decimal) -> bool:
            """Process payment to reduce corporate customer balance
            
            Args:
                payment_amount (Decimal): Amount to reduce from balance
                
            Returns:
                bool: True if payment successful, False otherwise
            """
            try:
                with open('data/corporate_customers.pkl', 'rb') as file:
                    customers = pickle.load(file)
                    if self.cust_id not in customers:
                        return False
                    
                    # Ensure payment amount doesn't exceed current balance
                    if payment_amount > abs(self.cust_balance):
                        return False
                        
                    # Reduce balance by payment amount
                    self.cust_balance -= payment_amount  # Add positive amount to negative balance
                    customers[self.cust_id] = self
                    
                    with open('data/corporate_customers.pkl', 'wb') as file:
                        pickle.dump(customers, file)
                    
                    return True
            except Exception as e:
                print(f"Error processing corporate payment: {e}")
                return False

    def check_out_with_payment(self, order_data: dict, payment_method: str, *, 
                card_number: str = None,
                card_type: str = None, 
                card_expiry_date: date = None,
                cvv: str = None,
                card_holder: str = None,
                bank_name: str = None,
                debit_card_num: str = None) -> bool:
        """Process checkout with immediate payment for corporate customer"""
        try:
            # Create Order instance first
            items = []
            for cart_item in order_data['cart_items']:
                item_type = cart_item['type']
                name = cart_item['name']
                price = cart_item['price']
                quantity = cart_item['quantity']
                
                if item_type == 'weight':
                    item = WeightedVeggie(name, quantity, price)
                elif item_type == 'unit':
                    item = UnitPriceVeggie(name, int(quantity), price)
                elif item_type == 'pack':
                    item = PackVeggie(name, int(quantity), price)
                elif item_type == 'box':
                    item = PremadeBox(name, int(quantity), price)
                    if cart_item['contents']:
                        contents = []
                        for content in cart_item['contents'].split(', '):
                            # Extract veggie name and create appropriate veggie instance
                            veg_name = content.split(' x ')[0]
                            contents.append(UnitPriceVeggie(veg_name, 1, Decimal('0.00')))
                        item.set_content(contents)
                
                item.calculate_total()
                items.append(item)

            # Create order instance with corporate customer
            order = Order(
                order_customer=self,  # Use self as customer
                order_date=date.today(),
                delivery_method=DeliveryMethod.DELIVERY if order_data['is_delivery'] else DeliveryMethod.PICKUP
            )
            order.set_items(items)

            # Process payment based on method
            if payment_method == "account":
                if not self.can_place_order(order.total_amount):
                    return False
                if not self.charge_to_account(order.total_amount):
                    return False
            else:
                # Handle credit/debit card payment
                success = self.make_payment(
                    payment_amount=order.total_amount,
                    payment_date=date.today(),
                    payment_method=payment_method,
                    card_number=card_number,
                    card_type=card_type,
                    card_expiry_date=card_expiry_date,
                    cvv=cvv,
                    card_holder=card_holder,
                    bank_name=bank_name,
                    debit_card_num=debit_card_num
                )
                
                if not success:
                    print("Payment processing failed")
                    return False

            # Initialize dictionaries if files don't exist
            try:
                with open('data/orders.pkl', 'rb') as file:
                    orders = pickle.load(file)
            except FileNotFoundError:
                orders = {}

            try:
                with open('data/corporate_customers.pkl', 'rb') as file:
                    customers = pickle.load(file)
            except FileNotFoundError:
                customers = {}

            # Update order and save
            order.order_status = OrderStatus.PENDING
            self.list_of_orders.append(order)
            orders[order.order_number] = order
            customers[self.cust_id] = self

            # Save updates
            with open('data/orders.pkl', 'wb') as file:
                pickle.dump(orders, file)
            with open('data/corporate_customers.pkl', 'wb') as file:
                pickle.dump(customers, file)

            return True

        except Exception as e:
            print(f"Error in check_out_with_payment: {str(e)}")
            return False

    def charge_to_account(self, amount: Decimal) -> bool:
        """Charge amount to corporate customer account
        
        Args:
            amount (Decimal): Amount to charge
            
        Returns:
            bool: True if charge successful, False otherwise
        """
        try:
            with open('data/corporate_customers.pkl', 'rb') as file:
                customers = pickle.load(file)
                if self.cust_id not in customers:
                    return False
                
                self.cust_balance += amount
                customers[self.cust_id] = self
                
                with open('data/corporate_customers.pkl', 'wb') as file:
                    pickle.dump(customers, file)
                
                return True
        except Exception as e:
            print(f"Error charging to corporate account: {e}")
            return False

class OrderStatus(Enum):
    """Enum for order status"""
    PENDING = "pending"
    FULFILLED = "fulfilled"

class Payment:
    payment_id = 1000
    
    def __init__(self, *, payment_amount: Decimal, payment_date: date):
        """Initialize Payment
        
        Args:
            payment_amount (Decimal): Amount of payment
            payment_date (date): Date of payment
        """
        self.payment_id = f"PAY{Payment.payment_id}"
        Payment.payment_id += 1
        self.payment_amount = Decimal(str(payment_amount))
        self.payment_date = payment_date

class CreditCardPayment(Payment):
    def __init__(self, *, payment_amount: Decimal, payment_date: date,
                 card_number: str, card_type: str, card_expiry_date: date,
                 cvv: str, card_holder: str):
        """Initialize CreditCardPayment
        
        Args:
            payment_amount (Decimal): Amount of payment
            payment_date (date): Date of payment
            card_number (str): Credit card number
            card_type (str): Type of credit card
            card_expiry_date (date): Card expiry date
            cvv (str): Card verification value
            card_holder (str): Name of the card holder
        """
        super().__init__(payment_amount=payment_amount, payment_date=payment_date)
        self.card_number = card_number
        self.card_type = card_type
        self.card_expiry_date = card_expiry_date
        self.cvv = cvv
        self.card_holder = card_holder

class DebitCardPayment(Payment):
    def __init__(self, *, payment_amount: Decimal, payment_date: date,
                 bank_name: str, debit_card_num: str):
        """Initialize DebitCardPayment
        
        Args:
            payment_amount (Decimal): Amount of payment
            payment_date (date): Date of payment
            bank_name (str): Name of the bank
            debit_card_num (str): Debit card number
        """
        super().__init__(payment_amount=payment_amount, payment_date=payment_date)
        self.bank_name = bank_name
        self.debit_card_num = debit_card_num

class Order:
    order_id = 1000
    
    def __init__(self, order_customer: 'Customer', order_date: date, delivery_method: DeliveryMethod):
        """Initialize an order
        
        Args:
            order_customer (Customer): Customer placing the order
            order_date (date): Date of order
            delivery_method (DeliveryMethod): Method of delivery
        """
        self.order_number = f"ORD{Order.order_id}"
        Order.order_id += 1
        self.order_customer = order_customer
        self.order_date = order_date
        self.order_status = OrderStatus.PENDING
        self.list_of_items: List[Item] = []
        self.delivery_method = delivery_method
        self.delivery_fee = DELIVERY_FEE if delivery_method == DeliveryMethod.DELIVERY else Decimal('0.00')
        self.subtotal = Decimal('0.00')  # Total before discount
        self.discount = Decimal('0.00')  # Corporate customer discount amount
        self.sales_amount = Decimal('0.00')  # After discount
        self.total_amount = Decimal('0.00')  # Final total including delivery

    def __str__(self) -> str:
        """String representation of the order"""
        lines = [
            f"Order Number: {self.order_number}",
            f"Customer: {self.order_customer}",
            f"Order Date: {self.order_date}",
            f"Status: {self.order_status.value}",
            f"Delivery Method: {self.delivery_method.value}",
            f"Delivery Fee: ${self.delivery_fee:.2f}",
            "\nItems List:"
        ]
        
        if self.list_of_items:
            for item in self.list_of_items:
                item_lines = str(item).split('\n')
                lines.extend(f"    {line}" for line in item_lines)
        else:
            lines.append("    No items")
        
        lines.extend([
            f"\nSubtotal: ${self.subtotal:.2f}",
            f"Discount: ${self.discount:.2f}",
            f"Sales Amount: ${self.sales_amount:.2f}",
            f"Total Amount: ${self.total_amount:.2f}"
        ])
        
        return '\n'.join(lines)

    def set_items(self, items: List['Item']):
        """Set all order items at once and calculate amounts
        
        Args:
            items (List[Item]): List of items to add to order
        """
        self.list_of_items = items
        self.calculate_all_amounts()

    def calculate_subtotal(self):
        """Calculate subtotal from all items"""
        self.subtotal = sum(item.total_price for item in self.list_of_items).quantize(Decimal('0.01'), rounding=ROUND_DOWN)

    def calculate_discount(self):
        """Calculate discount if customer is corporate"""
        if isinstance(self.order_customer, CorporateCustomer):
            self.discount = (self.subtotal * self.order_customer.discount_rate).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        else:
            self.discount = Decimal('0.00')

    def calculate_sales_amount(self):
        """Calculate sales amount (subtotal - discount)"""
        self.sales_amount = self.subtotal - self.discount

    def calculate_total_amount(self):
        """Calculate final total amount including delivery fee"""
        self.total_amount = self.sales_amount + self.delivery_fee

    def calculate_all_amounts(self):
        """Calculate all amounts in the correct order"""
        self.calculate_subtotal()
        self.calculate_discount()
        self.calculate_sales_amount()
        self.calculate_total_amount()

class Item(ABC):
    def __init__(self, name: str):
        """Initialize an item
        
        Args:
            name (str): Name of the item
        """
        self.item_name = name
        self.total_price = Decimal('0.00')

    @abstractmethod
    def calculate_total(self):
        """Calculate total price of the item"""
        pass

class Veggie(Item):
    def __init__(self, veg_name: str):
        """Initialize a vegetable item
        
        Args:
            veg_name (str): Name of the vegetable
        """
        super().__init__(veg_name)
    
    def __str__(self):
        """String representation of vegetable item"""
        return f"Name: {self.item_name}\n"

class WeightedVeggie(Veggie):
    def __init__(self, veg_name: str, weight: Decimal, weight_per_kilo: Decimal):
        """Initialize a weighted vegetable item
        
        Args:
            veg_name (str): Name of the vegetable
            weight (Decimal): Weight in kilograms
            weight_per_kilo (Decimal): Price per kilogram
        """
        super().__init__(veg_name)
        self.weight = Decimal(str(weight))
        self.price_per_kilo = Decimal(str(weight_per_kilo))

    def calculate_total(self):
        """Calculate total price based on weight"""
        self.total_price = (self.weight * self.price_per_kilo).quantize(Decimal('0.01'), rounding=ROUND_DOWN)

    def __str__(self):
        """String representation of weighted vegetable item"""
        return super().__str__() + f"Weight: {self.weight} kg\nPrice per kilo: ${self.price_per_kilo}"
    
class PackVeggie(Veggie):
    def __init__(self, veg_name: str, num_of_pack: int, price_per_pack: Decimal):
        """Initialize a pack vegetable item
        
        Args:
            veg_name (str): Name of the vegetable
            num_of_pack (int): Number of packs
            price_per_pack (Decimal): Price per pack
        """
        super().__init__(veg_name)
        self.num_of_pack = num_of_pack
        self.price_per_pack = Decimal(str(price_per_pack))

    def calculate_total(self):
        """Calculate total price based on number of packs"""
        self.total_price = (self.num_of_pack * self.price_per_pack).quantize(Decimal('0.01'), rounding=ROUND_DOWN)

    def __str__(self):
        """String representation of pack vegetable item"""
        return super().__str__() + f"Number of packs: {self.num_of_pack}\nPrice per pack: ${self.price_per_pack}"

class UnitPriceVeggie(Veggie):
    def __init__(self, veg_name: str, quantity: int, price_per_unit: Decimal):
        """Initialize a unit-priced vegetable item
        
        Args:
            veg_name (str): Name of the vegetable
            quantity (int): Number of units
            price_per_unit (Decimal): Price per unit
        """
        super().__init__(veg_name)
        self.quantity = quantity
        self.price_per_unit = Decimal(str(price_per_unit))
    
    def calculate_total(self):
        """Calculate total price based on quantity"""
        self.total_price = (self.quantity * self.price_per_unit).quantize(Decimal('0.01'), rounding=ROUND_DOWN)

    def __str__(self):
        """String representation of unit-priced vegetable item"""
        return super().__str__() + f"Quantity: {self.quantity}\nPrice per unit: ${self.price_per_unit}"

class PremadeBox(Item):
    def __init__(self, box_size: str, quantity: int, price: Decimal):
        """Initialize a premade box item
        
        Args:
            box_size (str): Size/name of the box
            quantity (int): Number of boxes
            price (Decimal): Price per box
        """
        super().__init__(box_size)
        self.box_content: List['Item'] = []
        self.quantity = quantity
        self.price = price

    def set_content(self, content: List['Item']):
        """Set the contents of the box
        
        Args:
            content (List[Item]): List of items in the box
        """
        self.box_content = content

    def calculate_total(self):
        """Calculate total price based on quantity"""
        self.total_price = (self.quantity * self.price).quantize(Decimal('0.01'), rounding=ROUND_DOWN)

    def __str__(self):
        """String representation of premade box item"""
        return (f"Box Size: {self.item_name}\n"
                f"Quantity: {self.quantity}\n"
                f"Price: ${self.price}\n"
                f"Contents: {', '.join([item.item_name for item in self.box_content])}")