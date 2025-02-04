import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from decimal import Decimal, ROUND_DOWN

class MakePayment:
    def __init__(self, parent, controller=None):
        """
        Initialize Payment class
        Args:
            parent: parent window widget
            controller: controller instance for managing data and callbacks
        """
        try:
            self.controller = controller
            self.main_frame = ttk.Frame(parent)
            
            # Store controller's current user
            self.current_user = self.controller.user if hasattr(self.controller, 'user') else None
            
            # Initialize all variables first
            self._init_variables()
            
            # Create notebook for payment methods
            self.notebook = ttk.Notebook(self.main_frame)
            self.notebook.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
            
            # Create frames for different payment methods
            self.credit_frame = ttk.Frame(self.notebook)
            self.debit_frame = ttk.Frame(self.notebook)
            
            # Add frames to notebook
            self.notebook.add(self.credit_frame, text='Credit Card')
            self.notebook.add(self.debit_frame, text='Debit Card')
            
            # Store hint labels and input widgets for both pages
            self.hint_labels = {}
            self.payment_entries = {}
            self.input_widgets = {
                'credit': [],
                'debit': []
            }
            
            # Setup UI for each payment method
            self._setup_balance_summary()
            
            # Create frames but don't populate them yet
            self.credit_content = None
            self.debit_content = None
            
            # Bind tab change event to lazy loading
            self.notebook.bind('<<NotebookTabChanged>>', self._on_tab_changed)

            # Bind visibility event to update interface state
            self.main_frame.bind('<Visibility>', self._on_page_show)
            
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Error initializing payment system: {str(e)}")
            raise

    def _on_page_show(self, event):
        """Handle page visibility event to update interface state"""
        try:
            if self.controller and hasattr(self.controller, 'user'):
                # Get current balance and max owing limit
                current_balance = self.controller.user.cust_balance
                max_owing = self.controller.user.max_owing
                
                # Update balance information and interface state
                self.set_balance_info(current_balance, max_owing)
        except Exception as e:
            messagebox.showerror("Error", f"Error updating balance information: {str(e)}")

    def _on_balance_changed(self, *args):
        """Handle balance changes and update interface state accordingly"""
        self._update_interface_state()        

    def _init_variables(self):
        """Initialize all variables for the payment interface"""
        # Balance information variables
        self.current_balance_var = tk.StringVar(value="0.00")
        self.current_balance_var.trace_add('write', self._on_balance_changed)  # Add trace for balance changes
        self.max_owing_var = tk.StringVar(value="0.00")
        self.payment_amount_var = tk.StringVar(value="1.00")
        
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

    def _on_tab_changed(self, event):
        """Handle tab change event for lazy loading of content"""
        current_tab = self.notebook.select()
        tab_id = self.notebook.index(current_tab)
        
        # Load content for selected tab if not already loaded
        if tab_id == 0 and not self.credit_content:  # Credit Card tab
            self._setup_credit_payment()
        elif tab_id == 1 and not self.debit_content:  # Debit Card tab
            self._setup_debit_payment()

    def _setup_balance_summary(self):
        """Setup the balance summary section showing account balance information"""

        # Create a frame to hold all widgets
        for frame_name, frame in [('credit', self.credit_frame), ('debit', self.debit_frame)]:
            info_frame = ttk.LabelFrame(frame, text="Balance Information")
            info_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Add widgets to display balance information
            current_date = date.today().strftime("%Y-%m-%d")
            ttk.Label(info_frame, text=f"Date: {current_date}").grid(
                row=0, column=0, columnspan=2, sticky='w', padx=5, pady=2
            )
            
            # Add balance information
            ttk.Label(info_frame, text="Current Balance:").grid(
                row=1, column=0, sticky='w', padx=5, pady=2
            )
            balance_label = ttk.Label(info_frame, textvariable=self.current_balance_var)
            balance_label.grid(row=1, column=1, sticky='e', padx=5, pady=2)
            
            # Add max owing limit
            ttk.Label(info_frame, text="MaxOwing Limit:").grid(
                row=2, column=0, sticky='w', padx=5, pady=2
            )
            ttk.Label(info_frame, textvariable=self.max_owing_var).grid(
                row=2, column=1, sticky='e', padx=5, pady=2
            )
            
            # Add separator
            ttk.Separator(info_frame, orient='horizontal').grid(
                row=3, column=0, columnspan=2, sticky='ew', padx=5, pady=2
            )
            
            # Add payment amount entry
            ttk.Label(info_frame, text="Payment Amount:").grid(
                row=4, column=0, sticky='w', padx=5, pady=2
            )
            
            # Add payment entry with validation
            vcmd = (self.main_frame.register(self._validate_input), '%d', '%P', '%s', '%S')
            payment_entry = ttk.Entry(
                info_frame,
                textvariable=self.payment_amount_var,
                validate='key',
                validatecommand=vcmd
            )
            
            payment_entry.grid(row=4, column=1, sticky='e', padx=5, pady=2)
            
            # Store payment entry for easy access
            self.payment_entries[frame_name] = payment_entry
            
            hint_label = ttk.Label(info_frame, 
                                 text="No outstanding balance to pay",
                                 foreground="red")
            hint_label.grid(row=5, column=0, columnspan=2, sticky='w', padx=5, pady=2)
            hint_label.grid_remove()  # Hide initially
            
            # Store hint label for easy access
            self.hint_labels[frame_name] = hint_label

    def _setup_credit_payment(self):
            """Setup the credit card payment section"""

            # Lazy initialization of content if needed
            if self.credit_content:
                return
            
            # Create a frame to hold all widgets
            self.credit_content = ttk.Frame(self.credit_frame)
            self.credit_content.pack(fill=tk.BOTH, expand=True)
            
            # Create a container frame to hold all widgets
            main_container = ttk.Frame(self.credit_content)
            main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Create a list to store all widgets for easy access
            credit_widgets = []
            
            # Card Number with validation
            ttk.Label(main_container, text="Card Number:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
            card_frame = ttk.Frame(main_container)
            card_frame.grid(row=0, column=1, sticky='ew', padx=5, pady=2)
            
            # Validate card number input
            vcmd = (self.main_frame.register(self._validate_card_input), '%P')
            card_entry = ttk.Entry(
                card_frame,
                textvariable=self.credit_card_number,
                validate='key',
                validatecommand=vcmd
            )

            # Add card entry to frame
            card_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            ttk.Label(card_frame, text="(16 digits)").pack(side=tk.LEFT, padx=5)
            credit_widgets.append(card_entry)
            
            # Card Type
            ttk.Label(main_container, text="Card Type:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
            card_type_combo = ttk.Combobox(
                main_container,
                textvariable=self.credit_card_type,
                values=['VISA', 'MasterCard', 'American Express'],
                state='readonly'
            )

            # Add card type combo to frame
            card_type_combo.grid(row=1, column=1, sticky='ew', padx=5, pady=2)
            credit_widgets.append(card_type_combo)
            
            # Expiry Date
            ttk.Label(main_container, text="Expiry Date:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
            date_frame = ttk.Frame(main_container)
            date_frame.grid(row=2, column=1, sticky='ew', padx=5, pady=2)
            
            # Add month and year combo boxes
            month_combo = ttk.Combobox(
                date_frame,
                textvariable=self.credit_expiry_month,
                values=[f"{i:02d}" for i in range(1, 13)],
                width=5,
                state='readonly'
            )
            month_combo.pack(side=tk.LEFT, padx=2)
            credit_widgets.append(month_combo)
            
            # Add year combo box
            year_combo = ttk.Combobox(
                date_frame,
                textvariable=self.credit_expiry_year,
                values=[str(i) for i in range(2024, 2035)],
                width=6,
                state='readonly'
            )
            year_combo.pack(side=tk.LEFT, padx=2)
            credit_widgets.append(year_combo)
            
            # CVV with validation
            ttk.Label(main_container, text="CVV:").grid(row=3, column=0, sticky='w', padx=5, pady=2)
            cvv_frame = ttk.Frame(main_container)
            cvv_frame.grid(row=3, column=1, sticky='w', padx=5, pady=2)
            
            cvv_vcmd = (self.main_frame.register(self._validate_cvv_input), '%P')
            cvv_entry = ttk.Entry(
                cvv_frame,
                textvariable=self.credit_cvv,
                width=5,
                validate='key',
                validatecommand=cvv_vcmd # Validate CVV input
            )
            cvv_entry.pack(side=tk.LEFT)
            ttk.Label(cvv_frame, text="(3 digits)").pack(side=tk.LEFT, padx=5)
            credit_widgets.append(cvv_entry)
            
            # Card Holder
            ttk.Label(main_container, text="Card Holder:").grid(row=4, column=0, sticky='w', padx=5, pady=2)
            holder_entry = ttk.Entry(
                main_container,
                textvariable=self.credit_holder
            )
            holder_entry.grid(row=4, column=1, sticky='ew', padx=5, pady=2)
            credit_widgets.append(holder_entry)
            
            # Buttons
            button_frame = ttk.Frame(main_container)
            button_frame.grid(row=5, column=0, columnspan=2, pady=20)
            
            confirm_button = ttk.Button(
                button_frame,
                text="Confirm Payment",
                command=self._confirm_credit_payment # Confirm credit card payment
            )
            confirm_button.pack(side=tk.LEFT, padx=5)
            credit_widgets.append(confirm_button)
            
            cancel_button = ttk.Button(
                button_frame,
                text="Cancel",
                command=self._on_cancel # Cancel payment
            )
            cancel_button.pack(side=tk.LEFT, padx=5)
            credit_widgets.append(cancel_button)
            
            # Store all credit card widgets for easy access
            self.input_widgets['credit'] = credit_widgets

    def _validate_cvv_input(self, new_val):
        """Validate CVV input - only allow digits up to 3"""
        if not new_val:  # Allow deletion
            return True
        return new_val.isdigit() and len(new_val) <= 3

    def _setup_debit_payment(self):
            """Setup the debit card payment section"""
            if self.debit_content: # Lazy initialization
                return
                
            # Create a frame to hold all widgets    
            self.debit_content = ttk.Frame(self.debit_frame)
            self.debit_content.pack(fill=tk.BOTH, expand=True)
            
            # Create a container frame to hold all widgets
            main_container = ttk.Frame(self.debit_content)
            main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Create a list to store all widgets for easy access
            debit_widgets = []
            
            # Bank selection
            ttk.Label(main_container, text="Bank Name:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
            bank_combo = ttk.Combobox(
                main_container,
                textvariable=self.debit_bank_name,
                values=['Bank A', 'Bank B', 'Bank C'],
                state='readonly'
            )
            bank_combo.grid(row=0, column=1, sticky='ew', padx=5, pady=2)
            debit_widgets.append(bank_combo)
            
            # Card Number with validation
            ttk.Label(main_container, text="Card Number:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
            card_frame = ttk.Frame(main_container)
            card_frame.grid(row=1, column=1, sticky='ew', padx=5, pady=2)
            
            # Validate card number input
            vcmd = (self.main_frame.register(self._validate_card_input), '%P')
            card_entry = ttk.Entry(
                card_frame,
                textvariable=self.debit_card_number,
                validate='key',
                validatecommand=vcmd # Validate card number input
            )
            card_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            ttk.Label(card_frame, text="(16 digits)").pack(side=tk.LEFT, padx=5)
            debit_widgets.append(card_entry)
            
            # Buttons
            button_frame = ttk.Frame(main_container)
            button_frame.grid(row=2, column=0, columnspan=2, pady=20)
            
            # Add buttons to confirm or cancel payment
            confirm_button = ttk.Button(
                button_frame,
                text="Confirm Payment",
                command=self._confirm_debit_payment
            )
            confirm_button.pack(side=tk.LEFT, padx=5)
            debit_widgets.append(confirm_button)
            
            cancel_button = ttk.Button(
                button_frame,
                text="Cancel",
                command=self._on_cancel # Cancel payment
            )
            cancel_button.pack(side=tk.LEFT, padx=5)
            debit_widgets.append(cancel_button)

            # Store all debit card widgets for easy access
            self.input_widgets['debit'] = debit_widgets

            try:
                balance_str = self.current_balance_var.get().strip('-$')
                current_balance = Decimal(balance_str) if balance_str else Decimal('0')
                
                if current_balance == 0:
                    for widget in debit_widgets:
                        if isinstance(widget, ttk.Combobox):
                            widget.config(state='disabled')
                        else:
                            widget.config(state='disabled')
            except:
                pass

    def _validate_input(self, action, value_if_allowed, prior_value, text):
        """Validate input for payment amount"""
        if action == '0':  # Deletion
            return True
            
        if value_if_allowed == "":  # Empty field
            return True
            
        try:
            # Validate input as a number with up to 2 decimal places
            if not all(c.isdigit() or c == '.' for c in value_if_allowed):
                return False
                
            # Validate number of decimal places    
            if value_if_allowed.count('.') > 1:
                return False
            #
            # Validate number of decimal places    
            if '.' in value_if_allowed:
                decimals = len(value_if_allowed.split('.')[1])
                if decimals > 2:
                    return False
                    
            value = Decimal(value_if_allowed) if value_if_allowed else Decimal('0')
            current_balance = abs(Decimal(self.current_balance_var.get()))  # Use absolute value
            
            # Validate minimum payment amount
            if value < Decimal('1'):
                return False

            # Validate maximum payment amount    
            if value > current_balance:
                self.payment_amount_var.set(str(current_balance))
                return False
                
            return True
            
        except:
            return False


    def _validate_card_input(self, new_val):
        """Validate card number input - only allow digits up to 16"""
        if not new_val:  # Allow deletion
            return True
        return new_val.isdigit() and len(new_val) <= 16

    def _disable_inputs(self):
        """Disable all input widgets when no balance is due"""
        
        # Disable all stored input widgets for both payment methods
        for frame_type, widgets in self.input_widgets.items():
            for widget in widgets:
                widget.config(state='disabled')
            
            # Disable payment entry
            if frame_type in self.payment_entries:
                self.payment_entries[frame_type].config(state='disabled')
            
            # Show hint label
            if frame_type in self.hint_labels:
                self.hint_labels[frame_type].grid()

    def _enable_inputs(self):
        """Enable all input widgets when there is a balance due"""
        
        # Enable all stored input widgets for both payment methods
        for frame_type, widgets in self.input_widgets.items():
            for widget in widgets: # Enable all widgets
                if isinstance(widget, ttk.Combobox): # Enable combo boxes
                    widget.config(state='readonly') # Set to read-only
                else:
                    widget.config(state='normal')
            
            # Enable payment entry
            if frame_type in self.payment_entries:
                self.payment_entries[frame_type].config(state='normal')
            
            # Hide hint label
            if frame_type in self.hint_labels:
                self.hint_labels[frame_type].grid_remove()

    def _update_interface_state(self):
        """Update interface state based on current balance"""
        try:
            # Get current balance as Decimal
            balance_str = self.current_balance_var.get().strip('-$')
            current_balance = Decimal(balance_str) if balance_str else Decimal('0')
            
            # Update payment amount field state
            for payment_entry in self.payment_entries.values():
                if current_balance == 0:
                    payment_entry.config(state='disabled')
                    self.payment_amount_var.set("")
                else:
                    payment_entry.config(state='normal')
                    if not self.payment_amount_var.get():
                        self.payment_amount_var.set("1.00")

            # Lazy initialization of content if needed
            current_tab = self.notebook.select()
            tab_id = self.notebook.index(current_tab)
            
            if tab_id == 0 and not self.credit_content:
                self._setup_credit_payment()
            elif tab_id == 1 and not self.debit_content:
                self._setup_debit_payment()

            # Update input widgets state for both payment methods
            for frame_type, widgets in self.input_widgets.items():
                for widget in widgets:
                    if current_balance == 0:
                        # Disable all inputs when balance is 0
                        widget.config(state='disabled')
                    else:
                        # Enable inputs with appropriate states
                        if isinstance(widget, ttk.Combobox):
                            widget.config(state='readonly')
                        else:
                            widget.config(state='normal')

            # Update hint labels
            for frame_type, hint_label in self.hint_labels.items():
                if current_balance == 0:
                    hint_label.grid()
                else:
                    hint_label.grid_remove()

        except Exception as e:
            messagebox.showerror("Error", f"Error updating interface state: {str(e)}")

    def _process_payment(self, payment_type, payment_details):
        """Process payment and update interface
        
        Args:
            payment_type: String indicating payment type ('credit' or 'debit')
            payment_details: Dictionary containing payment details
        """
        try:
            # Get payment amount (as positive number)
            payment_str = self.payment_amount_var.get().strip('$')
            if not payment_str:
                messagebox.showwarning("Validation Error", "Please enter payment amount")
                return False

            payment_amount = Decimal(payment_str)
            current_balance = abs(Decimal(self.current_balance_var.get().strip('-$')))
            
            # Use controller's customer reference
            if hasattr(self.controller, 'user'):
                # Call controller's customer_make_payment method
                success = self.controller.customer_make_payment(
                    payment_amount
                )
                
                if success:
                    # Update display
                    new_balance = current_balance - payment_amount
                    self.current_balance_var.set(f"-${new_balance}")
                    
                    # Update interface state
                    self._update_interface_state()
                    
                    # Update customer home profile if available
                    if hasattr(self.controller, 'root'):
                        self.controller.root.update_profile_display()
                    
                    # Clear input fields after successful payment
                    self._clear_input_fields(payment_type)
                    
                    return True
                else:
                    messagebox.showerror("Error", "Payment processing failed")
                    return False
            else:
                raise ValueError("User data not found. Please try again.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error processing payment: {str(e)}")
            return False
    
    def _clear_input_fields(self, payment_type):
            """Clear input fields after successful payment
            
            Args:
                payment_type: String indicating which form to clear ('credit' or 'debit')
            """

            # Clear input fields based on payment type
            if payment_type == 'credit':
                self.credit_card_number.set('')
                self.credit_card_type.set('')
                self.credit_expiry_month.set('')
                self.credit_expiry_year.set('')
                self.credit_cvv.set('')
                self.credit_holder.set('')
            else:  # debit
                self.debit_bank_name.set('')
                self.debit_card_number.set('')

    def _confirm_credit_payment(self):
        """Handle credit card payment confirmation"""
        try:

            # Get form values
            payment_details = {
                'card_number': self.credit_card_number.get(),
                'card_type': self.credit_card_type.get(),
                'card_expiry_date': date(
                    int(self.credit_expiry_year.get()),
                    int(self.credit_expiry_month.get()),
                    1
                ),
                'cvv': self.credit_cvv.get(),
                'card_holder': self.credit_holder.get()
            }
            
            # Validate required fields
            if not all(payment_details.values()):
                messagebox.showwarning("Validation Error", "Please fill in all required fields")
                return
            
            # Validate exact length
            if len(payment_details['card_number']) != 16:
                messagebox.showwarning("Validation Error", "Card number must be exactly 16 digits")
                return

            # Validate exact length    
            if len(payment_details['cvv']) != 3:
                messagebox.showwarning("Validation Error", "CVV must be exactly 3 digits")
                return

            # Process payment
            if self._process_payment('credit', payment_details):
                messagebox.showinfo("Success", "Credit card payment processed successfully.")

        except Exception as e:
            messagebox.showerror("Error", f"Error processing credit card payment: {str(e)}")


    def _confirm_debit_payment(self):
        """Handle debit card payment confirmation"""
        try:
            # Get form values
            payment_details = {
                'bank_name': self.debit_bank_name.get(),
                'debit_card_num': self.debit_card_number.get()
            }
            
            # Validate required fields
            if not payment_details['bank_name']:
                messagebox.showwarning("Validation Error", "Please select a bank")
                return
            
            if not payment_details['debit_card_num']:
                messagebox.showwarning("Validation Error", "Please enter card number")
                return
            
            # Validate exact length
            if len(payment_details['debit_card_num']) != 16:
                messagebox.showwarning("Validation Error", "Card number must be exactly 16 digits")
                return

            # Process payment
            if self._process_payment('debit', payment_details):
                messagebox.showinfo("Success", "Debit card payment processed successfully.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error processing debit card payment: {str(e)}")

    def _on_cancel(self):
        """Reset all input fields to initial state"""
        try:
            # Reset payment amount to min payment (1.00)
            current_balance = abs(Decimal(self.current_balance_var.get()))
            if current_balance > 0:
                self.payment_amount_var.set("1.00")
            
            # Clear all credit card fields
            self.credit_card_number.set('')
            self.credit_card_type.set('')
            self.credit_expiry_month.set('')
            self.credit_expiry_year.set('')
            self.credit_cvv.set('')
            self.credit_holder.set('')
            
            # Clear all debit card fields
            self.debit_bank_name.set('')
            self.debit_card_number.set('')
            
        except Exception as e:
            messagebox.showerror("Error", f"Error resetting fields: {str(e)}")

    def set_balance_info(self, current_balance: Decimal, max_owing: Decimal):
        """Set the balance information display and update UI state
        
        Args:
            current_balance (Decimal): Current account balance
            max_owing (Decimal): Maximum allowed owing amount
        """
        try:
            # Format balances as strings with currency symbol and negative sign
            new_balance = abs(current_balance).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
            max_owing_str = abs(max_owing).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
                        
            # Only update if balance has changed
            if new_balance != self.current_balance_var.get():
                self.current_balance_var.set(new_balance)
                self.max_owing_var.set(max_owing_str)
                
                # Set initial payment amount to 1.00 or total balance if less
                if abs(current_balance) < Decimal('1.00'):
                    self.payment_amount_var.set(str(abs(current_balance)))
                else:
                    self.payment_amount_var.set("1.00")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error setting balance information: {str(e)}")


    def get_main_frame(self):
        """Return main frame for integration with other interfaces"""
        return self.main_frame