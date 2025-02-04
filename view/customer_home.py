import tkinter as tk
from tkinter import ttk, messagebox
from .product import Product
from .payment import Payment
from decimal import Decimal
from .make_payment import MakePayment
from .staff_home import AutoTreeview

class CustomerHome:
    def __init__(self, root, customer, controller):
        """Initialize CustomerHome interface.
        
        Args:
            root: Root window widget
            customer: Customer instance
            controller: Controller instance for managing data and callbacks
        """
        self.controller = controller
        self.root = root
        self.root.resizable(False, False)
        self.customer = customer
        self.root.title("FHV Company - Customer Home")
        
        self.content_frames = {} # Cache for content frames
        self.current_frame = None # Current frame displayed
        self.current_treeview = None 
        self.loading_label = None
        
        # Setup window layout
        self.setup_window()
        self.create_widgets()

        # Bind window close event
        self.login_window = self.root.master
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Set the default frame to display
        self.show_loading()
        self.place_new_order()

    def setup_window(self):
        """Setup window layout and frames"""
        window_width = 1200
        window_height = 800
        
        # Center window on screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        top_y = 0
        
        # Set window position and size
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{top_y}')
        
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left and right frames
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

    def create_widgets(self):
        """Create and setup all widgets"""
        # Customer Profile Area
        self.profile_frame = ttk.LabelFrame(self.left_frame, text="Customer Profile", padding="10")
        self.profile_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(self.profile_frame, text=str(self.customer)).pack(anchor=tk.W, pady=2)

        # Function Area
        self.function_frame = ttk.LabelFrame(self.left_frame, text="Function Area", padding="10")
        self.function_frame.pack(fill=tk.BOTH, expand=True)
        
        self.buttons_frame = ttk.Frame(self.function_frame)
        self.buttons_frame.pack(fill=tk.X)

        # Function buttons
        self.function_buttons = {
            "Place New Order": self.place_new_order,
            "Make Payment": self.make_payment,
            "Current Orders": self.view_current_orders,
            "Previous Orders": self.view_previous_orders
        }

        # Create buttons
        for text, command in self.function_buttons.items():
            button_frame = ttk.Frame(self.buttons_frame)
            button_frame.pack(fill=tk.X, pady=3)
            ttk.Button(button_frame, text=text, command=command).pack(fill=tk.X, padx=5)

        # Bottom frame
        bottom_frame = ttk.Frame(self.function_frame)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Separator and Logout button
        ttk.Separator(bottom_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        self.logout_button = ttk.Button(
            bottom_frame,
            text="Log Out",
            command=self.on_logout,
            style='Accent.TButton'
        )
        self.logout_button.pack(fill=tk.X)

        # Display Area
        self.display_frame = ttk.LabelFrame(self.right_frame, text="Display Area", padding="10")
        self.display_frame.pack(fill=tk.BOTH, expand=True)

    def show_frame(self, frame_id, title, create_func=None):
        """Generic method to display frames"""
        try:
            self.show_loading()
            
            # Clear display area
            for widget in self.display_frame.winfo_children():
                widget.pack_forget()
            
            # Update title
            self.display_frame.configure(text=title)
            
            # Check if frame exists in cache
            if frame_id not in self.content_frames and create_func:
                frame = create_func()
                if frame: # Cache frame if created successfully
                    self.content_frames[frame_id] = frame # Cache frame
            
            if frame_id in self.content_frames: # Show frame if exists
                self.current_frame = self.content_frames[frame_id]
                self.hide_loading() # Hide loading indicator
                self.current_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            else:
                # Show error message if frame not found
                error_frame = ttk.Frame(self.display_frame)
                ttk.Label(
                    error_frame,
                    text="Failed to load the content. Please try again.",
                    foreground='red'
                ).pack(pady=10)
                error_frame.pack(fill=tk.BOTH, expand=True)
                self.current_frame = error_frame
                
        except Exception as e:
            messagebox.showerror("Error", f"Error showing frame: {str(e)}")
        finally:
            self.hide_loading()

    def show_loading(self): 
        """Display loading indicator"""
        self.hide_loading()
        loading_frame = ttk.Frame(self.display_frame)
        loading_frame.pack(expand=True)
        self.loading_label = ttk.Label(
            loading_frame,
            text="Loading...",
            font=('Helvetica', 12)
        )
        self.loading_label.pack(expand=True)
        self.root.update()

    def hide_loading(self):
        """Hide loading indicator"""
        if self.loading_label:
            self.loading_label.master.destroy()
            self.loading_label = None
            self.root.update()

    def create_new_order_frame(self):
        """Create order frame"""
        try:
            product_frame = ttk.Frame(self.display_frame)
            product_system = Product(product_frame, self.controller, self.customer)
            # Bind root for callback updates
            self.product_system = product_system
            product_system.bind_payment_callback(self.show_payment_window)  # Bind payment callback
            product_system.get_main_frame().pack(fill=tk.BOTH, expand=True)
            return product_frame
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize order system: {str(e)}")
            return None

    def show_payment_window(self, order_data):
        """Display payment window as modal dialog"""
        try:
            payment_window = tk.Toplevel(self.root)
            payment_window.title("Payment")
            
            window_width = 500
            window_height = 600
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x = int((screen_width/2) - (window_width/2))
            y = int((screen_height/2) - (window_height/2))
            payment_window.geometry(f'{window_width}x{window_height}+{x}+{y}')
            
            payment_window.transient(self.root)
            payment_window.grab_set() # Make modal
            payment_window.resizable(False, False)
            
            payment_system = Payment(payment_window, self.controller, self.product_system)
            # Bind payment system to root for callback
            self.controller.root = self
            if order_data: # Set order amounts if available
                payment_system.set_order_amounts(
                    order_data['subtotal'],
                    order_data['discount'],
                    order_data['delivery_fee'],
                    order_data['total']
                )
            
            payment_frame = payment_system.get_main_frame()
            payment_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Override payment window's protocol for proper cleanup
            def on_payment_window_close():
                payment_window.grab_release()
                payment_window.destroy()
                
            payment_window.protocol("WM_DELETE_WINDOW", on_payment_window_close)
            self.root.wait_window(payment_window)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error showing payment window: {str(e)}")

    def get_current_orders_data(self):
        """Get current orders data from controller"""
        headers = ["Order ID", "Customer", "Date", "Status", "Items", 
                  "Subtotal", "Delivery Fee", "Total Amount"]
        
        data = [] # Order data
        # Get current orders for customer
        for order_number, order in self.controller.customer_current_orders(self.customer).items():
            data.append((
                order_number, order["Customer"], order["Date"], order["Status"], 
                order["Items"], order["Subtotal"], order["Delivery Fee"], order["Total Amount"]
            ))
        return headers, data

    def get_previous_orders_data(self):
        """Get previous orders data from controller"""
        headers = ["Order ID", "Customer", "Date", "Status", "Items", 
                  "Subtotal", "Delivery Fee", "Total Amount"]
        
        data = []
        for order_number, order in self.controller.customer_previous_orders(self.customer).items():
            data.append((
                order_number, order["Customer"], order["Date"], order["Status"], 
                order["Items"], order["Subtotal"], order["Delivery Fee"], order["Total Amount"]
            ))
        return headers, data

    def update_profile_display(self):
        """Update customer profile display"""
        try:
            # Clear existing profile content
            for widget in self.profile_frame.winfo_children():
                widget.destroy()
                
            # Add updated profile information
            ttk.Label(self.profile_frame, text=str(self.customer)).pack(anchor=tk.W, pady=2)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error updating profile: {str(e)}")

    def show_treeview_content(self, title, data):
        """Display content in treeview"""
        try:
            for widget in self.display_frame.winfo_children():
                widget.pack_forget()
            
            title_frame = ttk.Frame(self.display_frame)
            title_frame.pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(
                title_frame,
                text=title,
                font=('Helvetica', 14, 'bold')
            ).pack(side=tk.LEFT)
            
            headers, rows = data
            self.current_treeview = AutoTreeview(
                self.display_frame, 
                headers, 
                rows, 
                self.controller
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error displaying content: {str(e)}")

    def create_payment_frame(self):
        """Create payment frame for balance payment.
        
        Returns:
            ttk.Frame: The created payment frame, or None if creation fails
        """
        try:
            payment_frame = ttk.Frame(self.display_frame)
            
            # Create payment system
            payment_system = MakePayment(payment_frame, self.controller)
            
            # Set current balance information from customer data
            payment_system.set_balance_info(
                current_balance=self.customer.cust_balance,
                max_owing=self.customer.max_owing
            )
            
            # Bind root for callback updates
            self.controller.root = self
            
            # Pack the payment frame into the display area
            payment_system.get_main_frame().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            return payment_frame
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize payment system: {str(e)}")
            return None
        
    def make_payment(self):
        """Display payment interface in the main display area.
        
        Uses the show_frame method's caching mechanism to:
        1. Create new payment frame only on first access
        2. Reuse existing frame on subsequent accesses
        """
        self.show_frame('make_payment', "Make Payment", self.create_payment_frame)
        
    def place_new_order(self):
        """Display order system"""
        self.show_frame('new_order', "Place New Order", self.create_new_order_frame)
        
    def view_current_orders(self):
        """Display current orders in treeview"""
        self.show_treeview_content("Current Orders", self.get_current_orders_data())

    def view_previous_orders(self):
        """Display previous orders in treeview"""
        self.show_treeview_content("Previous Orders", self.get_previous_orders_data())
        
    def on_logout(self):
        """Handle logout"""
        if messagebox.askyesno("Logout Confirmation", "Are you sure you want to logout?"):
            try:
                self.root.destroy()
                self.login_window.deiconify()
            except Exception as e:
                messagebox.showerror("Error", f"Error during logout: {str(e)}")

    def on_closing(self):
        """Handle window closing"""
        if messagebox.askyesno("Quit Confirmation", "Are you sure you want to quit the application?"):
            try:
                self.root.destroy()
                self.login_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Error during closing: {str(e)}")