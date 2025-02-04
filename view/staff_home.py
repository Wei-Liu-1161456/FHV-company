import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from decimal import Decimal, ROUND_DOWN

class AutoTreeview(ttk.Treeview):
    def __init__(self, parent, headers, data, controller=None, mode="readonly", *args, **kwargs):
        """Initialize Treeview with automatic configuration.
        
        Args:
            parent: The parent widget that will contain this Treeview.
            headers: List of column headers for the Treeview.
            data: Initial data to populate the Treeview.
            controller: Optional controller to handle user interactions.
            mode: Mode of the Treeview; can be "readonly" or "editable".
            *args, **kwargs: Additional arguments passed to the parent class.
        """
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        self.mode = mode
        self["columns"] = headers
        self.heading("#0", text="", anchor="w")
        self.column("#0", width=0, stretch=tk.NO)

        for header in headers:
            self.heading(header, text=header, anchor="w")
            if header == "Items":
                self.column(header, anchor="w", stretch=True, width=300, minwidth=200)
            else:
                self.column(header, anchor="w", stretch=True, width=100)

        self.tooltip = None
        self.bind('<Motion>', self._on_motion)
        self.bind('<Leave>', self._on_leave)

        # Create single event binding only when mode is editable
        if self.mode == "editable":
            self.bind("<Double-Button-1>", self._on_double_click, add="+")  # Changed from Double-1
            self.bind("<Button-3>", self._show_context_menu, add="+")

        self.update_data(data)

        self.scroll_y = ttk.Scrollbar(parent, orient="vertical", command=self.yview)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.scroll_x = ttk.Scrollbar(parent, orient="horizontal", command=self.xview)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.config(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)
        self.pack(fill=tk.BOTH, expand=True)

    def update_data(self, data):
        """Update the Treeview with new data.
        
        Args:
            data: List of rows, where each row is a list of values to display.
        """
        # Clear existing items from the Treeview
        for item in self.get_children():
            self.delete(item)

        # Insert new data into the Treeview
        for row in data:
            row_values = []
            for i, value in enumerate(row):
                if value is None:
                    row_values.append("N/A")  # Replace None with "N/A"
                elif i == 4:  # Special handling for Items column
                    # No length restriction; insert the full value
                    row_values.append(str(value))
                else:
                    row_values.append(str(value))  # Convert other values to string
            self.insert("", "end", values=row_values)  # Insert the row into the Treeview

    def _on_motion(self, event):
        """Handle mouse motion events to show tooltips.
        
        Args:
            event: The mouse event containing position information.
        """
        cell = self.identify_row(event.y)  # Identify which row is under the mouse
        if cell and self.identify_column(event.x) == '#5':  # Check if it's the Items column
            values = self.item(cell)['values']  # Get values for the identified row
            if values and len(values) >= 5:  # Ensure Items data exists
                # Create or update the tooltip if it doesn't exist
                if not self.tooltip:
                    self.tooltip = tk.Toplevel()  # Create a new top-level window for the tooltip
                    self.tooltip.wm_overrideredirect(True)  # Remove window decorations
                    self.tooltip_label = tk.Label(self.tooltip, justify=tk.LEFT,
                                                   background="#ffffe0", relief='solid', borderwidth=1)
                    self.tooltip_label.pack()  # Pack the label into the tooltip window

                # Set tooltip position and content
                x, y, _, _ = self.bbox(cell, '#5')  # Get the bounding box for the cell
                x_root = event.x_root + 10  # X position for tooltip
                y_root = event.y_root + 10  # Y position for tooltip
                self.tooltip_label.config(text=str(values[4]))  # Set tooltip text to Items value
                self.tooltip.geometry(f"+{x_root}+{y_root}")  # Position the tooltip
                self.tooltip.deiconify()  # Show the tooltip
        elif self.tooltip:
            self.tooltip.withdraw()  # Hide tooltip if mouse is not over the Items column

    def _on_leave(self, event):
        """Handle mouse leave events to hide tooltips.
        
        Args:
            event: The mouse event containing position information.
        """
        if self.tooltip:
            self.tooltip.withdraw()  # Hide the tooltip when the mouse leaves

    def _on_double_click(self, event):
        """Handle double-click events on Treeview items.
        
        Args:
            event: The mouse event containing position information.
        """
        item = self.identify_row(event.y)  # Identify the row that was double-clicked
        if item:
            self._process_item(item)  # Process the item

    def _show_context_menu(self, event):
        """Show a context menu on right-clicking an item in the Treeview.
        
        Args:
            event: The mouse event containing position information.
        """
        item = self.identify_row(event.y)  # Identify the row under the mouse
        if item:
            menu = tk.Menu(self, tearoff=0)  # Create a context menu
            menu.add_command(label="Process Order", command=lambda: self._process_item(item))  # Add command to process the order
            menu.post(event.x_root, event.y_root)  # Display the menu at the mouse position

    def _process_item(self, item_id):
        """Process the item when the order is fulfilled.
        
        Args:
            item_id: The ID of the item to process.
        """
        values = self.item(item_id)["values"]  # Get the values of the selected item
        order_id = values[0]  # Extract the order ID

        # Ask the user to confirm fulfilling the order
        if messagebox.askyesno(
            "Fulfill Order", 
            f"Fulfill this order?\n\n"
            f"Order ID: {order_id}\n"
            f"Customer: {values[1]}\n"
            f"Date: {values[2]}\n"
            f"Status: {values[3]}\n"
            f"Items: {values[4]}\n"
            f"Subtotal: ${Decimal(values[5]).quantize(Decimal('0.01'), rounding=ROUND_DOWN)}\n"
            f"Delivery Fee: ${Decimal(values[6]).quantize(Decimal('0.01'), rounding=ROUND_DOWN)}\n"
            f"Total: ${Decimal(values[7]).quantize(Decimal('0.01'), rounding=ROUND_DOWN)}"
        ):
            # Call the controller method to process the order
            success = self.controller.staff_fulfill_order(order_id)

            if success:
                self.delete(item_id)  # Remove the item from the Treeview
                messagebox.showinfo("Success", "Order fulfilled successfully!")  # Show success message


class DateSelector(ttk.Frame):
    def __init__(self, parent, label_text):
        super().__init__(parent)
        
        # Get current date
        today = date.today()
        self.current_year = today.year
        self.current_month = today.month
        self.current_day = today.day
        
        # Create date selection frame
        date_frame = ttk.Frame(self)
        date_frame.pack(side=tk.LEFT, padx=5)
        
        # Add label
        ttk.Label(date_frame, text=label_text).pack(side=tk.LEFT, padx=5)
        
        # Year selector
        self.year_var = tk.StringVar(value=str(self.current_year))
        self.year_cb = ttk.Combobox(date_frame, textvariable=self.year_var, width=6)
        self.year_cb['values'] = list(range(2020, self.current_year + 1))
        self.year_cb.pack(side=tk.LEFT, padx=2)
        
        # Month selector
        self.month_var = tk.StringVar(value=str(self.current_month))
        self.month_cb = ttk.Combobox(date_frame, textvariable=self.month_var, width=4)
        self.month_cb['values'] = list(range(1, 13))
        self.month_cb.pack(side=tk.LEFT, padx=2)
        
        # Day selector
        self.day_var = tk.StringVar(value=str(self.current_day))
        self.day_cb = ttk.Combobox(date_frame, textvariable=self.day_var, width=4)
        self.day_cb['values'] = list(range(1, 32))
        self.day_cb.pack(side=tk.LEFT, padx=2)
        
        # Bind events
        self.month_cb.bind('<<ComboboxSelected>>', self._update_days)
        self.year_cb.bind('<<ComboboxSelected>>', self._update_days)
    
    def _update_days(self, event=None):
        """Update days based on selected month and year"""
        try:
            year = int(self.year_var.get())
            month = int(self.month_var.get())
            
            # Get the last day of the selected month
            if month in [4, 6, 9, 11]:
                last_day = 30
            elif month == 2:
                if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                    last_day = 29
                else:
                    last_day = 28
            else:
                last_day = 31
            
            # Update days combobox
            self.day_cb['values'] = list(range(1, last_day + 1))
            
            # Adjust day if current selection is invalid
            current_day = int(self.day_var.get())
            if current_day > last_day:
                self.day_var.set(str(last_day))
        
        except ValueError:
            pass
    
    def get_date(self):
        """Get selected date as date object"""
        try:
            year = int(self.year_var.get())
            month = int(self.month_var.get())
            day = int(self.day_var.get())
            return date(year, month, day)
        except ValueError:
            return None

class SalesReportFrame(ttk.Frame):
    def __init__(self, parent, on_date_submit):
        super().__init__(parent)
        self.on_date_submit = on_date_submit
        self.create_widgets()
        
    def create_widgets(self):
        # Date selection frame
        date_frame = ttk.LabelFrame(self, text="Date Range Selection", padding="10")
        date_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Start date selector
        self.start_date = DateSelector(date_frame, "Start Date:")
        self.start_date.pack(side=tk.LEFT)
        
        # End date selector
        self.end_date = DateSelector(date_frame, "End Date:")
        self.end_date.pack(side=tk.LEFT)
        
        # Submit button
        submit_frame = ttk.Frame(date_frame)
        submit_frame.pack(side=tk.LEFT, padx=20)
        ttk.Button(submit_frame, text="Generate Report",
                  command=self._on_submit).pack(side=tk.LEFT)
    
    def _on_submit(self):
        start_date = self.start_date.get_date()
        end_date = self.end_date.get_date()
        
        if not start_date or not end_date:
            messagebox.showerror("Error", "Please select valid dates!")
            return
        
        # Validate dates
        if start_date > end_date:
            messagebox.showerror("Error", "Start date cannot be after end date!")
            return
        
        if end_date > date.today():
            messagebox.showerror("Error", "End date cannot be in the future!")
            return
        
        self.on_date_submit(start_date, end_date)

class StaffHome:
    def __init__(self, root, staff, controller):
        """Initialize Staff Home window"""
        self.controller = controller
        self.root = root
        self.root.resizable(False, False)
        self.staff = staff
        self.root.title("FHV Company - Staff Home")
        self.current_frame = None
        self.text_widget = None
        self.current_treeview = None
        
        # Add sales report related attributes
        self.report_frame = None
        self.report_text = None
        self.date_selection = None
        
        self.setup_window()
        self.create_widgets()
        self.login_window = self.root.master
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_window(self):
        """Set up window properties and layout main frames"""
        window_width = 1200
        window_height = 700
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

    def create_widgets(self):
        """Create and arrange all widgets in the window"""
        # Staff Profile area
        self.profile_frame = ttk.LabelFrame(self.left_frame, text="Staff Details", padding="10")
        self.profile_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(self.profile_frame, text=str(self.staff)).pack(anchor=tk.W, pady=2)

        # Function Area section
        self.function_frame = ttk.LabelFrame(self.left_frame, text="Function Area", padding="10")
        self.function_frame.pack(fill=tk.BOTH, expand=True)
        
        self.buttons_frame = ttk.Frame(self.function_frame)
        self.buttons_frame.pack(fill=tk.X)

        # Function buttons configuration
        self.function_buttons = {
            "All Products": lambda: self.show_text_content("All Products", self.controller.staff_all_products()),
            "Current Orders": lambda: self.show_treeview_content("Current Orders", self.get_current_orders_data(), True),
            "Previous Orders": lambda: self.show_treeview_content("Previous Orders", self.get_previous_orders_data(), False),
            "All Customers": lambda: self.show_text_content("All Customers", self.controller.staff_all_customers()),
            "Sales Report": lambda: self.staff_sales_reports(),
            "Popular Items": lambda: self.show_text_content("Popular Items", self.controller.staff_popular_items())
        }

        for text, command in self.function_buttons.items():
            button = ttk.Button(self.buttons_frame, text=text, command=command)
            button.pack(fill=tk.X, pady=2, padx=5)

        # Bottom frame with logout button
        bottom_frame = ttk.Frame(self.function_frame)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

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

        # Show welcome message
        self.show_text_content("Welcome", f"Welcome, {self.staff.first_name}!")

    def get_current_orders_data(self):
        """Get current orders data"""
        headers = ["Order ID", "Customer", "Date", "Status", "Items", "Subtotal", "Delivery Fee", "Total Amount"]
        
        data = []
        for order_number, order in self.controller.staff_current_orders().items():
            data.append((order_number, order["Customer"], order["Date"], order["Status"], 
                        order["Items"], order["Subtotal"], order["Delivery Fee"], order["Total Amount"]))
        return headers, data

    def get_previous_orders_data(self):
        """Get previous orders data"""
        headers = ["Order ID", "Customer", "Date", "Status", "Items", "Subtotal", "Delivery Fee", "Total Amount"]
        
        data = []
        for order_number, order in self.controller.staff_previous_orders().items():
            data.append((order_number, order["Customer"], order["Date"], order["Status"], 
                        order["Items"], order["Subtotal"], order["Delivery Fee"], order["Total Amount"]))
        return headers, data

    def show_text_content(self, title, content):
        """Display content in text widget"""
        try:
            for widget in self.display_frame.winfo_children():
                widget.pack_forget()
            
            ttk.Label(
                self.display_frame,
                text=title,
                font=('Helvetica', 14, 'bold')
            ).pack(pady=(0, 10))
            
            # Create text widget with scrollbars
            text_container = ttk.Frame(self.display_frame)
            text_container.pack(fill=tk.BOTH, expand=True)
            
            v_scrollbar = ttk.Scrollbar(text_container)
            v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            h_scrollbar = ttk.Scrollbar(text_container, orient=tk.HORIZONTAL)
            h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            
            text_widget = tk.Text(
                text_container,
                wrap=tk.NONE,
                width=50,
                height=20,
                yscrollcommand=v_scrollbar.set,
                xscrollcommand=h_scrollbar.set,
                font=('Helvetica', 10)
            )
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            v_scrollbar.config(command=text_widget.yview)
            h_scrollbar.config(command=text_widget.xview)
            
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.END, content)
            text_widget.config(state='disabled')

        except Exception as e:
            messagebox.showerror("Error", f"Error displaying content: {str(e)}")

    def show_treeview_content(self, title, data, editable=False):
        """Display content in treeview"""
        try:
            for widget in self.display_frame.winfo_children():
                widget.pack_forget()
            
            # Title container
            title_frame = ttk.Frame(self.display_frame)
            title_frame.pack(fill=tk.X, pady=(0, 10))
            
            # Title
            ttk.Label(
                title_frame,
                text=title,
                font=('Helvetica', 14, 'bold')
            ).pack(side=tk.LEFT)
            
            # Add instruction for editable treeview
            if editable:
                ttk.Label(
                    title_frame,
                    text="(Double-click or right-click to fuflill order)",
                    font=('Helvetica', 14, 'bold'),
                    foreground='red'
                ).pack(side=tk.LEFT, padx=(10, 0))
            
            headers, rows = data
            mode = "editable" if editable else "readonly"
            self.current_treeview = AutoTreeview(self.display_frame, headers, rows, self.controller, mode=mode)

        except Exception as e:
            messagebox.showerror("Error", f"Error displaying content: {str(e)}")

    def staff_sales_reports(self):
        """Display sales report with date selection"""
        try:
            # Clear existing content
            for widget in self.display_frame.winfo_children():
                widget.pack_forget()
            
            # Title
            ttk.Label(
                self.display_frame,
                text="Sales Report",
                font=('Helvetica', 14, 'bold')
            ).pack(pady=(0, 10))
            
            # Create date selection frame if it doesn't exist
            if not self.date_selection:
                self.date_selection = SalesReportFrame(self.display_frame, self.update_sales_report)
            self.date_selection.pack(fill=tk.X)
            
            # Add separator between date selection and report
            ttk.Separator(self.display_frame, orient='horizontal').pack(fill=tk.X, pady=10)
            
            # Create report frame if it doesn't exist
            if not self.report_frame:
                self.report_frame = ttk.Frame(self.display_frame)
                
                # Create text widget with scrollbars for report content
                text_container = ttk.Frame(self.report_frame)
                text_container.pack(fill=tk.BOTH, expand=True)
                
                v_scrollbar = ttk.Scrollbar(text_container)
                v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                
                h_scrollbar = ttk.Scrollbar(text_container, orient=tk.HORIZONTAL)
                h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
                
                self.report_text = tk.Text(
                    text_container,
                    wrap=tk.NONE,
                    width=50,
                    height=20,
                    yscrollcommand=v_scrollbar.set,
                    xscrollcommand=h_scrollbar.set,
                    font=('Helvetica', 10)
                )
                self.report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
                
                v_scrollbar.config(command=self.report_text.yview)
                h_scrollbar.config(command=self.report_text.xview)
            
            self.report_frame.pack(fill=tk.BOTH, expand=True)
            
            # Set/Reset initial text
            self.report_text.config(state='normal')
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(tk.END, "Please select a date range and click 'Generate Report' to view the sales report.")
            self.report_text.config(state='disabled')

        except Exception as e:
            messagebox.showerror("Error", f"Error displaying sales report: {str(e)}")

    def update_sales_report(self, start_date, end_date):
        """Update sales report with new date range"""
        try:
            if self.report_text:  # Only update if text widget exists
                # Get report content from controller
                report_content = self.controller.staff_sales_report(start_date, end_date)
                
                # Update text widget with new content
                self.report_text.config(state='normal')
                self.report_text.delete(1.0, tk.END)
                self.report_text.insert(tk.END, report_content)
                self.report_text.config(state='disabled')

        except Exception as e:
            messagebox.showerror("Error", f"Error updating sales report: {str(e)}")

    def on_logout(self):
        """Handle logout action"""
        if messagebox.askyesno("Logout Confirmation", "Are you sure you want to logout?"):
            self.root.destroy()
            self.login_window.deiconify()

    def on_closing(self):
        """Handle window close event"""
        if messagebox.askyesno("Quit Confirmation", "Are you sure you want to quit the application?"):
            self.root.destroy()
            self.login_window.destroy()