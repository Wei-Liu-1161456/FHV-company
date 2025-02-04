import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from decimal import Decimal, ROUND_DOWN

class Payment:
    def __init__(self, parent, controller=None, product_system=None):
        """
        Initialize Payment class
        Args:
            parent: parent window widget
            controller: controller instance for managing data and callbacks
        """
        try:
            self.controller = controller
            self.main_frame = ttk.LabelFrame(parent, text="Payment Information")
            self.product_system = product_system
            self._init_variables()
            
            # Create notebook for payment methods
            self.notebook = ttk.Notebook(self.main_frame)
            self.notebook.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
            
            # Create frames for different payment methods
            self.account_frame = ttk.Frame(self.notebook)
            self.credit_frame = ttk.Frame(self.notebook)
            self.debit_frame = ttk.Frame(self.notebook)
            
            # Add frames to notebook
            self.notebook.add(self.account_frame, text='Charge to Account')
            self.notebook.add(self.credit_frame, text='Credit Card')
            self.notebook.add(self.debit_frame, text='Debit Card')
            
            # Setup UI for each payment method
            self._setup_order_summary()
            self._setup_account_payment()
            self._setup_credit_payment()
            self._setup_debit_payment()
            
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Error initializing payment system: {str(e)}")
            raise

    def _init_variables(self):
        """Initialize all variables for the payment interface"""
        # Order amount variables
        self.subtotal_var = tk.StringVar(value="$0.00")
        self.discount_var = tk.StringVar(value="$0.00")
        self.delivery_fee_var = tk.StringVar(value="$0.00")
        self.total_amount_var = tk.StringVar(value="$0.00")
        
        # Credit Card variables
        self.credit_card_number = tk.StringVar()
        self.credit_card_type = tk.StringVar()
        self.credit_expiry_month = tk.StringVar()
        self.credit_expiry_year = tk.StringVar()
        self.credit_cvv = tk.StringVar()
        self.credit_holder = tk.StringVar()
        
        # Debit Card variables
        self.debit_bank_name = tk.StringVar()
        self.debit_card_number = tk.StringVar()

    def _setup_order_summary(self):
        """Setup the order summary section showing amounts"""
        for frame in [self.account_frame, self.credit_frame, self.debit_frame]:
            info_frame = ttk.LabelFrame(frame, text="Order Summary")
            info_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Display current date
            current_date = date.today().strftime("%Y-%m-%d")
            ttk.Label(info_frame, text=f"Date: {current_date}").grid(
                row=0, column=0, columnspan=2, sticky='w', padx=5, pady=2
            )
            
            # Display order amount details
            ttk.Label(info_frame, text="Subtotal:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
            ttk.Label(info_frame, textvariable=self.subtotal_var).grid(row=1, column=1, sticky='e', padx=5, pady=2)
            
            ttk.Label(info_frame, text="Discount:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
            ttk.Label(info_frame, textvariable=self.discount_var).grid(row=2, column=1, sticky='e', padx=5, pady=2)
            
            ttk.Label(info_frame, text="Delivery Fee:").grid(row=3, column=0, sticky='w', padx=5, pady=2)
            ttk.Label(info_frame, textvariable=self.delivery_fee_var).grid(row=3, column=1, sticky='e', padx=5, pady=2)
            
            ttk.Separator(info_frame, orient='horizontal').grid(row=4, column=0, columnspan=2, sticky='ew', padx=5, pady=2)
            
            ttk.Label(info_frame, text="Total Amount:").grid(row=5, column=0, sticky='w', padx=5, pady=2)
            ttk.Label(info_frame, textvariable=self.total_amount_var).grid(row=5, column=1, sticky='e', padx=5, pady=2)

    def _setup_account_payment(self):
        """Setup the charge to account payment section"""
        main_container = ttk.Frame(self.account_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        message = "The amount will be charged to your account.\nPlease confirm to proceed."
        ttk.Label(main_container, text=message, justify=tk.CENTER).pack(pady=20)
        
        button_frame = ttk.Frame(main_container)
        button_frame.pack(side=tk.BOTTOM, pady=10)
        
        ttk.Button(button_frame, text="Confirm Payment",
                  command=self._confirm_account_payment).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel",
                  command=self._on_cancel).pack(side=tk.LEFT, padx=5)

    def _setup_credit_payment(self):
        """Setup the credit card payment section"""
        main_container = ttk.Frame(self.credit_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Card Number with validation
        ttk.Label(main_container, text="Card Number:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        card_frame = ttk.Frame(main_container)
        card_frame.grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        
        vcmd = (self.main_frame.register(self._validate_card_input), '%P')
        ttk.Entry(
            card_frame,
            textvariable=self.credit_card_number,
            validate='key',
            validatecommand=vcmd
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(card_frame, text="(16 digits)").pack(side=tk.LEFT, padx=5)
        
        # Card Type
        ttk.Label(main_container, text="Card Type:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        ttk.Combobox(
            main_container,
            textvariable=self.credit_card_type,
            values=['VISA', 'MasterCard', 'American Express'],
            state='readonly'
        ).grid(row=1, column=1, sticky='ew', padx=5, pady=2)
        
        # Expiry Date
        ttk.Label(main_container, text="Expiry Date:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        date_frame = ttk.Frame(main_container)
        date_frame.grid(row=2, column=1, sticky='ew', padx=5, pady=2)
        
        ttk.Combobox(
            date_frame,
            textvariable=self.credit_expiry_month,
            values=[f"{i:02d}" for i in range(1, 13)],
            width=5,
            state='readonly'
        ).pack(side=tk.LEFT, padx=2)
        ttk.Combobox(
            date_frame,
            textvariable=self.credit_expiry_year,
            values=[str(i) for i in range(2025, 2035)],
            width=6,
            state='readonly'
        ).pack(side=tk.LEFT, padx=2)
        
        # CVV with validation
        ttk.Label(main_container, text="CVV:").grid(row=3, column=0, sticky='w', padx=5, pady=2)
        cvv_frame = ttk.Frame(main_container)
        cvv_frame.grid(row=3, column=1, sticky='w', padx=5, pady=2)
        
        vcmd_cvv = (self.main_frame.register(self._validate_cvv_input), '%P')
        ttk.Entry(
            cvv_frame,
            textvariable=self.credit_cvv,
            width=5,
            validate='key',
            validatecommand=vcmd_cvv
        ).pack(side=tk.LEFT)
        ttk.Label(cvv_frame, text="(3 digits)").pack(side=tk.LEFT, padx=5)
        
        # Card Holder
        ttk.Label(main_container, text="Card Holder:").grid(row=4, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(
            main_container,
            textvariable=self.credit_holder
        ).grid(row=4, column=1, sticky='ew', padx=5, pady=2)
        
        # Buttons
        button_frame = ttk.Frame(main_container)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Confirm Payment",
                  command=self._confirm_credit_payment).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel",
                  command=self._on_cancel).pack(side=tk.LEFT, padx=5)

    def _setup_debit_payment(self):
        """Setup the debit card payment section"""
        main_container = ttk.Frame(self.debit_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bank selection
        ttk.Label(main_container, text="Bank Name:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        ttk.Combobox(
            main_container,
            textvariable=self.debit_bank_name,
            values=['Bank A', 'Bank B', 'Bank C'],
            state='readonly'
        ).grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        
        # Card Number with validation
        ttk.Label(main_container, text="Card Number:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        card_frame = ttk.Frame(main_container)
        card_frame.grid(row=1, column=1, sticky='ew', padx=5, pady=2)
        
        vcmd = (self.main_frame.register(self._validate_card_input), '%P')
        ttk.Entry(
            card_frame,
            textvariable=self.debit_card_number,
            validate='key',
            validatecommand=vcmd
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(card_frame, text="(16 digits)").pack(side=tk.LEFT, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(main_container)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Confirm Payment",
                  command=self._confirm_debit_payment).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel",
                  command=self._on_cancel).pack(side=tk.LEFT, padx=5)

    def _validate_card_input(self, new_val):
        """Validate card number input - only allow digits up to 16"""
        if not new_val:  # Allow deletion
            return True
        return new_val.isdigit() and len(new_val) <= 16

    def _validate_cvv_input(self, new_val):
        """Validate CVV input - only allow digits up to 3"""
        if not new_val:  # Allow deletion
            return True
        return new_val.isdigit() and len(new_val) <= 3

    def _confirm_credit_payment(self):
        """Handle credit card payment confirmation"""
        try:
            # Get form values
            card_type = self.credit_card_type.get()
            card_number = self.credit_card_number.get()
            cvv = self.credit_cvv.get()
            holder = self.credit_holder.get()
            month = self.credit_expiry_month.get()
            year = self.credit_expiry_year.get()
            
            # Validate required fields
            if not all([card_type, card_number, cvv, holder, month, year]):
                messagebox.showwarning("Validation Error", "Please fill in all required fields")
                return
            
            # Validate exact length
            if len(card_number) != 16:
                messagebox.showwarning("Validation Error", "Card number must be exactly 16 digits")
                return
                
            if len(cvv) != 3:
                messagebox.showwarning("Validation Error", "CVV must be exactly 3 digits")
                return
            
            if hasattr(self.controller, 'temp_order_data'):
                payment_date = date.today()
                card_expiry_date = date(int(year), int(month), 1)
                
                # Call check_out_with_payment method with all necessary parameters
                success = self.controller.temp_order_data['user'].check_out_with_payment(
                    order_data=self.controller.temp_order_data,
                    payment_method="credit",
                    card_number=card_number,
                    card_type=card_type,
                    card_expiry_date=card_expiry_date,
                    cvv=cvv,
                    card_holder=holder
                )
                
                if success:
                    messagebox.showinfo("Success", "Credit card payment processed successfully.")
                    # Clear cart after successful payment
                    self.product_system.clear_cart()
                    # Update profile display
                    if hasattr(self.controller, 'root'):
                        self.controller.root.update_profile_display()
                    self._on_cancel()
                else:
                    messagebox.showerror("Error", "Payment processing failed. Please verify your card details and try again.")
            else:
                raise ValueError("Order data not found. Please try again.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error processing credit card payment: {str(e)}")

    def _confirm_debit_payment(self):
        """Handle debit card payment confirmation"""
        try:
            # Get form values
            bank_name = self.debit_bank_name.get()
            card_number = self.debit_card_number.get()
            
            # Validate required fields
            if not bank_name:
                messagebox.showwarning("Validation Error", "Please select a bank")
                return
            
            if not card_number:
                messagebox.showwarning("Validation Error", "Please enter card number")
                return
            
            # Validate exact length
            if len(card_number) != 16:
                messagebox.showwarning("Validation Error", "Card number must be exactly 16 digits")
                return
            
            if hasattr(self.controller, 'temp_order_data'):
                # Call check_out_with_payment method with all necessary parameters
                success = self.controller.temp_order_data['user'].check_out_with_payment(
                    order_data=self.controller.temp_order_data,
                    payment_method="debit",
                    bank_name=bank_name,
                    debit_card_num=card_number
                )
                
                if success:
                    messagebox.showinfo("Success", "Debit card payment processed successfully.")
                    # Clear cart after successful payment
                    self.product_system.clear_cart()
                    # Update profile display
                    if hasattr(self.controller, 'root'):
                        self.controller.root.update_profile_display()
                    self._on_cancel()
                else:
                    messagebox.showerror("Error", "Payment processing failed. Please verify your card details and try again.")
            else:
                raise ValueError("Order data not found. Please try again.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error processing debit card payment: {str(e)}")

    def _confirm_account_payment(self):
        """Handle account payment confirmation"""
        try:
            if hasattr(self.controller, 'temp_order_data'):
                customer = self.controller.temp_order_data['user']
                order_amount = self.controller.temp_order_data['total']
                current_balance = customer.cust_balance
                potential_balance = current_balance + order_amount
                max_owing = customer.max_owing

                # Format all amounts
                current_balance_fmt = current_balance.quantize(Decimal('0.00'), rounding=ROUND_DOWN)
                potential_balance_fmt = potential_balance.quantize(Decimal('0.00'), rounding=ROUND_DOWN)
                order_amount_fmt = order_amount.quantize(Decimal('0.00'), rounding=ROUND_DOWN)
                max_owing_fmt = max_owing.quantize(Decimal('0.00'), rounding=ROUND_DOWN)

                # Call check_out_with_payment method
                success = customer.check_out_with_payment(
                    order_data=self.controller.temp_order_data,
                    payment_method="account"
                )
                print(self.controller.temp_order_data)
                if success:
                    messagebox.showinfo("Success", "Payment has been charged to your account.")
                    self.product_system.clear_cart()
                    # Update profile display
                    if hasattr(self.controller, 'root'):
                        self.controller.root.update_profile_display()
                    self._on_cancel()
                else:
                    messagebox.showerror(
                        "Error", 
                        f"Unable to charge to account:\n\n"
                        f"Current balance: -${current_balance_fmt}\n"
                        f"This order amount: ${order_amount_fmt}\n"
                        f"Potential balance after order: \n-${potential_balance_fmt}\n"
                        f"Maximum owing limit: -${max_owing_fmt}\n\n"
                        f"The potential balance would exceed your credit limit.\n"
                        f"Please either:\n"
                        f"1. Decrease your order first, or\n"
                        f"2. Use credit/debit card for this order."
                    )
            else:
                raise ValueError("Order data not found. Please try again.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error processing account payment: {str(e)}")

    def _on_cancel(self):
        """Handle payment cancellation and cleanup"""
        try:
            # Get the toplevel window containing this payment frame
            payment_window = self.main_frame.master
            
            # Release the grab before destroying the window
            payment_window.grab_release()
            
            # Destroy the window
            payment_window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error during payment cancellation: {str(e)}")

    def set_order_amounts(self, subtotal: Decimal, discount: Decimal, delivery_fee: Decimal, total: Decimal):
        """Set the order amount display
        
        Args:
            subtotal (Decimal): Order subtotal amount
            discount (Decimal): Discount amount
            delivery_fee (Decimal): Delivery fee
            total (Decimal): Total order amount
        """
        self.subtotal_var.set(f"${subtotal.quantize(Decimal('0.01'), rounding=ROUND_DOWN)}")
        self.discount_var.set(f"-${discount.quantize(Decimal('0.01'), rounding=ROUND_DOWN)}")
        self.delivery_fee_var.set(f"${delivery_fee.quantize(Decimal('0.01'), rounding=ROUND_DOWN)}")
        self.total_amount_var.set(f"${total.quantize(Decimal('0.01'), rounding=ROUND_DOWN)}")

    def get_main_frame(self):
        """Return main frame for integration with other interfaces"""
        return self.main_frame