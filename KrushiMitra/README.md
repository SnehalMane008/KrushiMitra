# KrushiMitra - Agricultural Store Management System

KrushiMitra is a comprehensive management system designed for agricultural stores. It helps farmers and agricultural businesses manage their inventory, sales, customers, and suppliers efficiently.

**Established: April 9, 2025**  
**Developed by: Dreamers - Students from AISSMS IOIT, AI&DS Department**  
**Project Guide: Dr. Sayali Belhe, Assistant Professor at AISSMS IOIT**

**जय जवान जय किसान**

## Features

- **User Authentication**: Secure login and registration with email OTP verification
- **Inventory Management**: Keep track of products, stock levels, and prices
- **Customer Management**: Maintain customer information and purchase history
- **Supplier Management**: Track suppliers and manage product deliveries
- **Sales Tracking**: Record and monitor all sales transactions
- **Reports & Analytics**: Get insights into business performance

## System Requirements

- Python 3.8+
- MySQL 5.7+
- Web browser with JavaScript enabled

## Installation

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd Krushi2.0
```

### Step 2: Set Up Python Environment
```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install flask mysql-connector-python
```

### Step 3: Set Up MySQL Database
```bash
# Log in to MySQL
mysql -u root -p

# Create the database
CREATE DATABASE agri_store;
exit;
```

### Step 4: Configure the Application
Update the email configuration in `KrushiMitra/app.py`:
```python
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'  # Replace with your Gmail
app.config['MAIL_PASSWORD'] = 'your-app-password'     # Replace with your app password
```
Note: To use Gmail for sending emails, you need to create an App Password in your Google Account security settings.

### Step 5: Initialize the Database
```bash
cd KrushiMitra
python fix_db.py
cd ..
```

### Step 6: Run the Application
```bash
python -m KrushiMitra.app
```

## How to Use

1. **Access the Application**: Open your browser and navigate to http://127.0.0.1:5000
2. **Register or Login**: Use the registration system or login with default admin credentials
   - Username: admin
   - Password: admin123
3. **Dashboard**: View key metrics and recent sales
4. **Manage Products**: Add, update, and track your product inventory
5. **Manage Customers**: Keep customer records up to date
6. **Manage Suppliers**: Track information about your product suppliers
7. **Record Sales**: Create new sales records and track inventory

## Default Accounts

- **Admin User**:
  - Username: admin
  - Password: admin123
  - Role: admin
  
- **Staff User**:
  - Username: user
  - Password: user123
  - Role: staff

## Project Structure

- `KrushiMitra/app.py`: Main application file
- `KrushiMitra/fix_db.py`: Database setup script
- `KrushiMitra/templates/`: HTML templates for the UI
- `KrushiMitra/static/`: Static assets (CSS, JavaScript, images)

## Troubleshooting

- **Database Connection Issues**: Verify MySQL credentials and ensure the MySQL server is running
- **Email Sending Failures**: Check your Gmail app password and make sure less secure app access is enabled
- **Port Conflicts**: If port 5000 is in use, change the port in app.py

## Running in VS Code

1. Open VS Code
2. Open the project folder (File > Open Folder)
3. Open a terminal in VS Code (View > Terminal)
4. Run the steps from the Installation section above

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: MySQL
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Icons**: Bootstrap Icons
- **Interactivity**: jQuery, DataTables

## License

This project is developed as an academic project by students of AISSMS IOIT.

## Acknowledgments

- Special thanks to Dr. Sayali Belhe for guiding this project
- AISSMS IOIT for providing the educational platform 