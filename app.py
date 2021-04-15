from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import date, timezone

app = Flask(__name__)

ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:AdiSha206@localhost/my_car_rental'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Cars inventory table
class Cars_inventory(db.Model):
    __tablename__ = "Cars_inventory"

    car_number = db.Column(db.String(10), primary_key=True)
    manufacturer = db.Column(db.String(200))
    price = db.Column(db.Integer)
    price_per_day = db.Column(db.Integer)
    is_available = db.Column(db.Boolean, default=True)
    rental_date = db.Column(db.Date, default=None)

    def __init__(self, car_number, manufacturer, price, price_per_day):
        self.car_number = car_number
        self.manufacturer = manufacturer
        self.price = price
        self.price_per_day = price_per_day
        self.is_available = True
        self.rental_date = None

# Rentals table
class Rentals(db.Model):
    __tablename__ = "Rentals"

    customer_id = db.Column(db.String(9))
    customer_first_name = db.Column(db.String(200))
    customer_last_name = db.Column(db.String(200))
    car_number = db.Column(db.String(10), primary_key=True)
    rental_date = db.Column(db.Date, default=date.today())

    def __init__(self, customer_id, customer_first_name, customer_last_name, car_number):
        self.customer_id = customer_id
        self.customer_first_name = customer_first_name
        self.customer_last_name = customer_last_name
        self.car_number = car_number
        self.rental_date = date.today()

@app.route('/')
def index():
    return render_template('index.html')

# Directing the user to the right page
@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        if request.form['button'] == "Cars inventory management":
            return render_template('carsManagement.html')
        elif request.form['button'] == "Rental management":
            return render_template('rentalManagement.html')
        elif request.form['button'] == "Statistics":
            return render_template('statistics.html')
    
    return render_template('index.html')

# Directing the user to the right page
@app.route('/carMenu', methods=['POST'])
def carMenu():
    if request.method == 'POST':
        if request.form['carMenu'] == "Show cars inventory":
            cars = Cars_inventory.query.all()
            return render_template('showCarsInventory.html', cars=cars)
        elif request.form['carMenu'] == "Add new car":
            return render_template('addNewCar.html')
        elif request.form['carMenu'] == "Remove car":
            return render_template('removeCar.html')
    
    return render_template('carsManagement.html')

# Adding a new car to the inventory
# If one or more fields are invalid -> Sends a corresponding message
@app.route('/addNewCar', methods=['POST'])
def addNewCar():
    if request.method == 'POST':
        car_number = request.form['number']
        manufacturer = request.form['manufacturer']
        price = request.form['price']
        price_per_day = request.form['price per day']
        
        # Checking the input values
        if len(car_number) != 9 and len(car_number) != 10:
            return render_template('addNewCar.html', message='Invalid car number')

        if db.session.query(Cars_inventory).filter(Cars_inventory.car_number == car_number).count() > 0:
            return render_template('addNewCar.html', message='Car with that number already exists')

        if manufacturer == 'Select manufacturer':
            return render_template('addNewCar.html', message='Invalid manufacturer')

        if price == '' or not price.isnumeric():
            return render_template('addNewCar.html', message='Invalid price')

        if price_per_day == '' or not price_per_day.isnumeric():
            return render_template('addNewCar.html', message='Invalid price per day')

        car = Cars_inventory(car_number, manufacturer, price, price_per_day)

        try:
            db.session.add(car)
            db.session.commit()
            return render_template('carsManagement.html', message='Car added successfully')
        except:
            return 'There was an error adding the car to the inventory'

# Removing a car from the inventory by car number
# If the number is invalid or the number doesn't exist -> Sends a corresponding message
@app.route('/removeCar', methods=['POST'])
def removeCar():
    car_number = request.form['number']
    
    if len(car_number) != 9 and len(car_number) != 10:
        return render_template('removeCar.html', message='Invalid car number')

    if db.session.query(Cars_inventory).filter(Cars_inventory.car_number == car_number).count() == 0:
        return render_template('removeCar.html', message='Car with that number doesn\'t exist')

    car_to_delete = Cars_inventory.query.get_or_404(car_number)

    try:
        db.session.delete(car_to_delete)
        db.session.commit()
        return render_template('carsManagement.html', message='Car removed successfully')
    except:
        return 'There was an error deleting the car from the inventory'

# Directing the user to the right page
@app.route('/rentalMenu', methods=['POST'])
def rentalMenu():
    if request.method == 'POST':
        if request.form['rentalMenu'] == "Rent a car":
            return render_template('rentCar.html')
        elif request.form['rentalMenu'] == "Show currently rented cars":
            rentals = db.session.query(Rentals).all()
            return render_template('showRentedCars.html', rentals=rentals)
        elif request.form['rentalMenu'] == "End car rental":
            return render_template('endCarRental.html')
    
    return render_template('rentalManagement.html')

# Renting a car
# If one or more fields are invalid or the car is already rented -> Sends a corresponding message
@app.route('/rentCar', methods=['POST'])
def rentCar():
    if request.method == 'POST':
        customer_id = request.form['customer id']
        customer_fname = request.form['customer fname']
        customer_lname = request.form['customer lname']
        car_number = request.form['number']

        # Checking the input values
        if customer_id == '' or len(customer_id) != 9 or not customer_id.isnumeric():
            return render_template('rentCar.html', message='Invalid customer ID')

        if customer_fname == '':
            return render_template('rentCar.html', message='Invalid customer first name')

        if customer_lname == '':
            return render_template('rentCar.html', message='Invalid customer last name')

        if len(car_number) != 9 and len(car_number) != 10:
            return render_template('rentCar.html', message='Invalid car number')

        if db.session.query(Rentals).filter(Rentals.car_number == car_number).count() > 0:
            return render_template('rentCar.html', message='That car is already rented')

        if db.session.query(Cars_inventory).filter(Cars_inventory.car_number == car_number).count() == 0:
            return render_template('rentCar.html', message='Car with that number doesn\'t exists')
        
        rental = Rentals(customer_id, customer_fname, customer_lname, car_number)

        try:
            db.session.add(rental)
            car = Cars_inventory.query.get_or_404(car_number)
            car.is_available = False
            car.rental_date = date.today()
            db.session.commit()
            return render_template('rentalManagement.html', message='Car rented successfully')
        except:
            return 'There was an error renting the car'

# Ending rental by car number
# If the number is invalid or the number doesn't exist -> Sends a corresponding message
@app.route('/endCarRental', methods=['POST'])
def endCarRental():
    car_number = request.form['number']
    
    if len(car_number) != 9 and len(car_number) != 10:
        return render_template('endCarRental.html', message='Invalid car number')

    if db.session.query(Rentals).filter(Rentals.car_number == car_number).count() == 0:
        return render_template('endCarRental.html', message='Car with that number isn\'t rented (or doesn\'t exist)')
    
    rental_to_end = Rentals.query.get_or_404(car_number)

    try:
        db.session.delete(rental_to_end)
        car = Cars_inventory.query.get_or_404(car_number)
        car.is_available = True
        car.rental_date = None
        db.session.commit()

        rental_days = (date.today() - rental_to_end.rental_date).days
        total_cost = (rental_days * car.price_per_day) + car.price
        message = 'Rental ended successfully! the cost is: ' + str(total_cost) + ' shekels'
        return render_template('rentalManagement.html', message=message)
    except:
        return 'There was an error ending the car rental'

# Redirects the user to the main page
@app.route('/returnToMain', methods=['POST'])
def returnToMain():
    if request.method == 'POST':
        return render_template('index.html')
    
# Redirects the user to the cars management page
@app.route('/returnToCarsManagement', methods=['POST'])
def returnToCarsManagement():
    if request.method == 'POST':
        return render_template('carsManagement.html')
    
# Redirects the user to the rental management page
@app.route('/returnToRentalManagement', methods=['POST'])
def returnToRentalManagement():
    if request.method == 'POST':
        return render_template('rentalManagement.html')

if __name__ == '__main__':
    app.run()