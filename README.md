# KrushiMitra - Agricultural Store Management System

KrushiMitra is a comprehensive web application designed to manage agricultural stores, tracking inventory, sales, customers, suppliers, and deliveries. Built with Flask and MySQL, it provides a complete solution for agricultural businesses.

**Developed by: Snehal Mane**  

## Features

- **User Authentication**: Secure login with role-based access (admin/staff)
- **Dashboard**: Overview of key metrics and recent transactions
- **Products Management**: Track products, prices, and supplier relationships
- **Customer Management**: Store customer information and track purchases
- **Supplier Management**: Manage supplier information and track deliveries
- **Sales Management**: Record sales, generate invoices, and track transaction history
- **Delivery Management**: Track deliveries from suppliers
- **Reporting**: Generate reports and analytics on business performance

## ER Diagram

The database schema follows this ER diagram:

- Users (id, username, password, role)
- Customers (customer_id, name, address, phone)
- Suppliers (supplier_id, name, address, phone)
- Products (product_id, name, price)
- Product_Supplier (product_id, supplier_id) - Junction table
- Deliveries (delivery_id, supplier_id, delivery_date, quantity)
- Sales (sale_id, customer_id, sale_date)
- Sales_Items (item_id, sale_id, product_id, quantity, price)

## Installation

### Prerequisites

- Python 3.8 or higher
- MySQL 5.7 or higher
- pip (Python package installer)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/KrushiMitra.git
   cd KrushiMitra
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```
   python KrushiMitra/setup_db.py
   ```

5. Run the application:
   ```
   python KrushiMitra/app.py
   ```

6. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

### Default Login Credentials

- Admin User:
  - Username: admin
  - Password: admin123

- Staff User:
  - Username: user
  - Password: user123

## Technologies Used

- **Backend**: Flask (Python)
- **Database**: MySQL
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Libraries**: Flask-MySQLdb

## Project Structure

```
KrushiMitra/
├── app.py                 # Main application file
├── db_config.py           # Database configuration
├── db_setup.sql           # SQL script for database setup
├── setup_db.py            # Script to set up the database
├── static/                # Static files (CSS, JS, images)
│   └── css/
│       └── style.css      # Custom CSS styles
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   ├── welcome.html       # Welcome page
│   ├── login.html         # Login page
│   ├── dashboard.html     # Dashboard
│   ├── products.html      # Products list
│   ├── customers.html     # Customers list
│   └── ...                # Other templates
└── requirements.txt       # Project dependencies
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Bootstrap for the UI components
- Flask for the web framework
- MySQL for the database 
