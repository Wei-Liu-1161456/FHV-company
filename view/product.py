import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from .my_widgts import ValidatedSpinbox

class Product:
    def __init__(self, parent, controller, user):
        '''Initialize the Product class with main frame, notebook, and product data
        
        Args:
            parent: Parent tkinter widget
            controller: Main application controller
            user: Current user object
        '''
        try:
            # Get data from controller
            self.controller = controller
            self.user = user

            # Initialize product data lists
            self.all_veggies_list = self.controller.all_veggies_list  # List of all vegetables
            self.veggies_weight_list = self.controller.veggies_weight_list  # Weight-based vegetables
            self.veggies_unit_list = self.controller.veggies_unit_list  # Unit-based vegetables  
            self.veggies_pack_list = self.controller.veggies_pack_list  # Pack-based vegetables

            # Initialize box configuration dictionaries
            self.smallbox_default_dict = self.controller.smallbox_default_dict
            self.mediumbox_default_dict = self.controller.mediumbox_default_dict
            self.largebox_default_dict = self.controller.largebox_default_dict

            # Set box sizes
            self.small_size = 3
            self.medium_size = 4
            self.large_size = 5
            
            # Create main frame and notebook
            self.main_frame = ttk.Frame(parent)
            self.notebook = ttk.Notebook(self.main_frame)
            self.notebook.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
            
            # Create notebook tabs
            self.veggie_frame = ttk.Frame(self.notebook)
            self.box_frame = ttk.Frame(self.notebook)
            self.notebook.add(self.veggie_frame, text='Veggies')
            self.notebook.add(self.box_frame, text='Premade Boxes')
            
            # Set default values
            self.veggie_type_var = tk.StringVar(value='weight/kg')
            self.box_size_var = tk.StringVar(value='small')
            
            # Setup UI components
            self._setup_veggie_products()  # Individual vegetable selection
            self._setup_box_products()     # Premade box selection
            self._setup_process_order()    # Delivery and checkout options
            self._setup_cart()             # Shopping cart display
            
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Error initializing product system: {str(e)}")
            raise

    def _setup_veggie_products(self):
        """Set up the individual vegetable product selection interface"""
        # Main container using grid layout
        main_container = ttk.Frame(self.veggie_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        main_container.grid_columnconfigure(0, weight=1)

        # Veggie type selection area
        type_frame = ttk.Frame(main_container)
        type_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

        for i, veggie_type in enumerate(['weight/kg', 'unit', 'pack']):
            ttk.Radiobutton(
                type_frame,
                text=veggie_type,
                value=veggie_type,
                variable=self.veggie_type_var,
                command=self._update_veggie_products
            ).grid(row=0, column=i, padx=5)

        # Product selection area
        product_frame = ttk.Frame(main_container)
        product_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        product_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(product_frame, text="Product:").grid(row=0, column=0, padx=5)
        self.veggie_product_var = tk.StringVar()
        self.veggie_product_combo = ttk.Combobox(
            product_frame,
            textvariable=self.veggie_product_var,
            state='readonly',
            width=40
        )
        self.veggie_product_combo.grid(row=0, column=1, sticky='ew', padx=5)

        # Quantity selection area
        quantity_frame = ttk.Frame(main_container)
        quantity_frame.grid(row=2, column=0, sticky='ew', padx=5, pady=5)

        ttk.Label(quantity_frame, text="Quantity:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.veggie_quantity_spinbox = ValidatedSpinbox(quantity_frame)
        self.veggie_quantity_spinbox.model = 'float'
        self.veggie_quantity_spinbox.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.veggie_quantity_spinbox.set('1')

        # Button area
        button_frame = ttk.Frame(main_container)
        button_frame.grid(row=4, column=0, sticky='ew', padx=5, pady=5)

        ttk.Button(
            button_frame,
            text="Add to Cart",
            command=self._add_veggie_to_cart
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Clear Cart",
            command=self.clear_cart
        ).pack(side=tk.LEFT, padx=5)

        self._update_veggie_products()

    def _setup_box_products(self):
        """Set up the premade box selection interface"""
        main_container = ttk.Frame(self.box_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Box size selection
        size_frame = ttk.Frame(main_container)
        size_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        
        for i, size in enumerate(['small', 'medium', 'large']):
            price = getattr(self, f"{size}box_default_dict")['price']
            ttk.Radiobutton(
                size_frame,
                text=f"{size.capitalize()} (${float(price):.2f})",
                value=size,
                variable=self.box_size_var,
                command=self._update_b_contents
            ).grid(row=0, column=i, padx=5)
        
        # Box contents selection area
        self.contents_label_frame = ttk.LabelFrame(main_container, text="Box Contents")
        self.contents_label_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        
        self.contents_frame = ttk.Frame(self.contents_label_frame)
        self.contents_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.contents_frame.grid_columnconfigure(1, weight=1)
        
        # Create item selection widgets
        self.item_widgets = []
        for i in range(5):
            label = ttk.Label(self.contents_frame, text=f"Item {i+1}:")
            label.grid(row=i, column=0, padx=5, pady=2, sticky='w')
            
            combo = ttk.Combobox(self.contents_frame, state='readonly', width=40)
            combo['values'] = self.all_veggies_list
            combo.grid(row=i, column=1, padx=5, pady=2, sticky='ew')
            
            self.item_widgets.append((label, combo))
            
            if i >= 3:
                label.grid_remove()
                combo.grid_remove()
        
        # Quantity selection area
        quantity_frame = ttk.Frame(main_container)
        quantity_frame.grid(row=2, column=0, sticky='ew', padx=5, pady=5)

        ttk.Label(quantity_frame, text="Quantity:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.box_quantity_spinbox = ValidatedSpinbox(quantity_frame)
        self.box_quantity_spinbox.model = 'int'
        self.box_quantity_spinbox.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.box_quantity_spinbox.set('1')

        # Action buttons
        ttk.Button(
            quantity_frame,
            text="Add to Cart",
            command=self._add_to_cart_b
        ).grid(row=0, column=2, padx=5)

        ttk.Button(
            quantity_frame,
            text="Clear Cart",
            command=self.clear_cart
        ).grid(row=0, column=3, padx=5)
        
        self._update_b_contents()

    def _setup_process_order(self):
        """Set up the order processing interface with delivery options and checkout"""
        process_order_frame = ttk.LabelFrame(self.main_frame, text="Process Order")
        process_order_frame.pack(padx=10, pady=5, fill=tk.X)

        main_container = ttk.Frame(process_order_frame)
        main_container.pack(fill='x', padx=5, pady=5)

        # Delivery option area
        delivery_frame = ttk.Frame(main_container)
        delivery_frame.pack(fill='x', anchor='w')

        delivery_label = ttk.Label(delivery_frame, text="Delivery Option:")
        delivery_label.grid(row=0, column=0, padx=5, sticky="w")

        self.delivery_var = tk.BooleanVar(value=False)
        self.delivery_option_checkbutton = ttk.Checkbutton(
            delivery_frame, 
            variable=self.delivery_var,
            width=0
        )
        self.delivery_option_checkbutton.grid(row=0, column=1, padx=5, sticky="w")

        self.delivery_status_label = tk.Label(delivery_frame, text="")
        self.delivery_status_label.grid(row=0, column=2, padx=5, sticky="w")

        # Configure delivery availability
        if not self.user.can_delivery:
            self.delivery_option_checkbutton.config(state=tk.DISABLED)
            self.delivery_status_label.config(
                text=f"Sorry, Delivery not available for your address: {self.user.cust_address} km"
            )
        else:
            self.delivery_status_label.config(
                text=f"Delivery available for your address: {self.user.cust_address} km"
            )

        # Checkout button area
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill='x', pady=5, anchor='w')
        
        ttk.Button(
            button_frame,
            text="Check Out Order",
            command=self._check_out_order
        ).pack(side='left', padx=5)

    def _setup_cart(self):
        """Set up the shopping cart display interface"""
        cart_frame = ttk.LabelFrame(self.main_frame, text="Cart Details")
        cart_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        main_container = ttk.Frame(cart_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        
        # Create scrollable tree view container
        tree_frame = ttk.Frame(main_container)
        tree_frame.grid(row=0, column=0, sticky='nsew')
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal")
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create treeview for cart items
        self.cart_tree = ttk.Treeview(
            tree_frame,
            columns=('Product', 'Quantity', 'Price', 'Subtotal', 'Contents'),
            show='headings',
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        
        v_scrollbar.config(command=self.cart_tree.yview)
        h_scrollbar.config(command=self.cart_tree.xview)
        
        # Configure columns
        self.cart_tree.heading('Product', text='Product')
        self.cart_tree.heading('Quantity', text='Quantity')
        self.cart_tree.heading('Price', text='Price')
        self.cart_tree.heading('Subtotal', text='Subtotal')
        self.cart_tree.heading('Contents', text='Box Contents')
        
        self.cart_tree.column('Product', width=150, minwidth=150)
        self.cart_tree.column('Quantity', width=60, minwidth=60)
        self.cart_tree.column('Price', width=100, minwidth=100)
        self.cart_tree.column('Subtotal', width=100, minwidth=100)
        self.cart_tree.column('Contents', width=400, minwidth=800)
        
        self.cart_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _update_veggie_products(self):
        """Update the vegetable product dropdown based on selected type"""
        current_type = self.veggie_type_var.get()
        
        # Update quantity input type
        self.veggie_quantity_spinbox.model = 'float' if current_type == 'weight/kg' else 'int'

        # Type mapping for list selection
        type_mapping = {
            'weight/kg': 'weight',
            'unit': 'unit',
            'pack': 'pack'
        }
        
        # Get corresponding product list
        list_name = f'veggies_{type_mapping[current_type]}_list'
        options = getattr(self, list_name)
        
        # Update combobox values
        if options:
            self.veggie_product_combo['values'] = options
            self.veggie_product_combo.set(options[0])
        else:
            self.veggie_product_combo['values'] = []
            self.veggie_product_combo.set('')

    def _update_b_contents(self):
        """Update the box contents based on selected box size"""
        current_size = self.box_size_var.get()
        box_dict = getattr(self, f"{current_size}box_default_dict")
        num_items = getattr(self, f"{current_size}_size")
        
        # Update visibility and values for item widgets
        for i, (label, combo) in enumerate(self.item_widgets):
            if i < num_items:
                # Show widgets and set default value
                label.grid()
                combo.grid()
                
                # Set default content from box configuration
                default_content = box_dict['contents'][i]
                for option in self.all_veggies_list:
                    if default_content.split(' x ')[0] in option:
                        combo.set(option)
                        break
            else:
                # Hide excess widgets
                label.grid_remove()
                combo.grid_remove()

    def _add_veggie_to_cart(self):
        """Add individual vegetable product to the shopping cart."""
        try:
            # Validate product selection
            product = self.veggie_product_var.get()
            if not product:
                messagebox.showwarning("Warning", "Please select a product")
                return

            # Get and validate quantity
            quantity = Decimal(self.veggie_quantity_spinbox.get())
            if quantity <= 0:
                messagebox.showwarning("Warning", "Quantity must be greater than zero")
                return
            
            # Calculate price and subtotal
            name, price = product.split(' - $')
            price = Decimal(price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            subtotal = (price * quantity).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            # Add item to cart display
            self.cart_tree.insert('', 'end', values=(
                name,
                quantity,
                f"${float(price):.2f}",
                f"${float(subtotal):.2f}",
                ""  # No contents for individual products
            ))
        except (ValueError, InvalidOperation) as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error adding to cart: {str(e)}")

    def _add_to_cart_b(self):
        """Add premade box to the shopping cart"""
        try:
            # Get box configuration
            size = self.box_size_var.get()
            quantity = int(self.box_quantity_spinbox.get())
            box_dict = getattr(self, f"{size}box_default_dict")
            price = box_dict['price']
            
            # Calculate subtotal
            subtotal = (price * Decimal(quantity)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            # Get selected contents
            contents = []
            num_items = getattr(self, f"{size}_size")
            for i, (_, combo) in enumerate(self.item_widgets[:num_items]):
                item_name = combo.get().split(' - $')[0]
                contents.append(f"{item_name} x 1")
            
            contents_str = ", ".join(contents)
            
            # Add box to cart display
            self.cart_tree.insert('', 'end', values=(
                f"{size.capitalize()} Box",
                quantity,
                f"${float(price):.2f}",
                f"${float(subtotal):.2f}",
                contents_str
            ))
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error adding to cart: {str(e)}")

    def _check_out_order(self):
        """Process checkout and prepare order data"""
        try:
            # Validate cart contents
            if not self.cart_tree.get_children():
                messagebox.showwarning("Warning", "Cart is empty")
                return
            
            # Initialize order data
            self.cart_dict = []
            subtotal = Decimal('0.00')
            
            # Process cart items
            for item in self.cart_tree.get_children():
                values = self.cart_tree.item(item)['values']
                
                name = values[0]
                quantity = Decimal(values[1])
                price = Decimal(values[2].replace('$', ''))
                subtotal_item = Decimal(values[3].replace('$', ''))
                contents = values[4] if values[4] else ""
                
                subtotal += subtotal_item
                
                # Create item record
                cart_item = {
                    'type': 'box' if 'Box' in name else self._determine_item_type(name),
                    'name': name,
                    'quantity': quantity,
                    'price': price,
                    'subtotal': subtotal_item,
                    'contents': contents
                }
                self.cart_dict.append(cart_item)
            
            # Calculate discount
            discount = Decimal('0.00')
            # First check if user has a discount rate attribute
            if hasattr(self.user, 'discount_rate'):
                discount = subtotal * self.user.discount_rate
            # If no discount_rate attribute, check if user type is corporate
            elif hasattr(self.controller, 'user_type') and self.controller.user_type == "corporate":
                discount = subtotal * Decimal('0.10')
                
            # Calculate fees and total
            delivery_fee = Decimal('10.00') if self.delivery_var.get() else Decimal('0.00')
            total = subtotal - discount + delivery_fee
            
            # Store order data in controller
            self.controller.temp_order_data = {
                'cart_items': self.cart_dict,
                'user': self.user,
                'subtotal': subtotal,
                'delivery_fee': delivery_fee,
                'discount': discount,
                'total': total,
                'is_delivery': self.delivery_var.get(),
            }
            
            # Show payment interface
            if hasattr(self, 'payment_callback'):
                self.payment_callback(self.controller.temp_order_data)
            else:
                messagebox.showwarning("Warning", "Payment system not properly initialized")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error checking out order: {str(e)}")

    def _determine_item_type(self, name):
        """
        Determine product type based on name
        
        Args:
            name (str): Product name
            
        Returns:
            str: Product type ('weight', 'unit', 'pack', 'box', or 'unknown')
        """
        if name in ["Small Box", "Medium Box", "Large Box"]:
            return 'box'
        
        if "by weight/kg" in name:
            return 'weight'
        elif "by unit" in name:
            return 'unit'
        elif "by pack" in name:
            return 'pack'
        
        return 'unknown'

    def clear_cart(self):
        """Clear all items from shopping cart"""
        try:
            for item in self.cart_tree.get_children():
                self.cart_tree.delete(item)
        except Exception as e:
            messagebox.showerror("Error", f"Error clearing cart: {str(e)}")

    def get_main_frame(self):
        """Return main frame for integration with other interfaces"""
        return self.main_frame

    def bind_payment_callback(self, callback):
        """
        Bind callback function for payment processing
        
        Args:
            callback: Function to call when proceeding to payment
        """
        self.payment_callback = callback