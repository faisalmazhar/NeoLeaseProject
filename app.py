# app.py

from flask import Flask, render_template, request, abort
from models import db, CarListing
import logging
app = Flask(__name__)
from utils import parse_price  # or put the function above directly in app.py

# Use the same connection style as your CSV script
# app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost:5432/neolease_db"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://neolease_db_user:DKuNZ0Z4OhuNKWvEFaAuWINgr7BfgyTE@dpg-cvslkuvdiees73fiv97g-a.oregon-postgres.render.com:5432/neolease_db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# ------------------ Define Routes Below ------------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/calculator')
def general_calculator():
    # Maybe just show a generic form or instructions
    return render_template('calculator_general.html')



# @app.route("/calculator/<int:car_id>")
# def calculator(car_id):
#     # Fetch the car from DB
#     car = CarListing.query.get_or_404(car_id)
#     # Pass the car into the calculator template
#     return render_template("calculator.html", car=car)


@app.route("/calculator/<int:car_id>")
def calculator(car_id):
    car = CarListing.query.get_or_404(car_id)

    raw_str = car.prijs  # "20.950,-"
    numeric_price = parse_price(raw_str)  # hopefully => 20950.0
    if numeric_price <= 0:
        numeric_price = 30000.0  # fallback


    logging.debug(f"[Calculator Route] Car ID={car_id}, raw_str={raw_str!r}, final numeric_price={numeric_price}")

    return render_template(
        "calculator.html",
        car=car,
        thePrice=numeric_price  # Pass a numeric float to the template
    )

@app.route("/aanbod")
def aanbod():
    return render_template("aanbod.html")

@app.route("/diensten")
def diensten():
    return render_template("diensten.html")

@app.route('/financial-lease')
def financial_lease():
    return render_template('financial_lease.html')

@app.route('/cookieverklaring')
def cookieverklaring():
    return render_template('cookieverklaring.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')



@app.route('/operational-lease')
def operational_lease():
    return render_template('operational_lease.html')


@app.route('/persoonlijke-lening')
def personal_loan():
    return render_template('persoonlijke_lening.html')


@app.route("/favorites")
def favorites():
    return render_template("favorites.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/listings")
def listings():
    page = request.args.get("page", 1, type=int)
    per_page = 16
    
    # Paginate CarListing items from the database
    pagination = CarListing.query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        "listings.html",
        cars=pagination.items,
        page=page,
        total_pages=pagination.pages,
    )


@app.route("/submit-quote", methods=["POST"])
def submit_quote():
    """
    Handles the form posted from request_quote.html
    Then returns a "thank you" page with the posted data.
    """
    # 1) Grab form fields
    car_id = request.form.get("car_id")  # e.g. "123"
    car_title = request.form.get("car_title")
    monthly_payment = request.form.get("monthly_payment")
    phone = request.form.get("phone")
    email = request.form.get("email")
    message = request.form.get("message", "")

    # 2) Optionally, do your email-sending or store in DB:
    # send_email(to="info@neolease.nl", subject="New Quote Request", body=some_body_string)
    # or log them, or store in your database, etc.

    # For now, we’ll just pass them to a success page
    return render_template(
        "quote_submitted.html",
        car_title=car_title,
        monthly_payment=monthly_payment,
        phone=phone,
        email=email,
        message=message
    )

@app.route("/car/<int:car_id>")
def car_detail(car_id):
    # Grab the CarListing from DB or 404
    car = CarListing.query.get_or_404(car_id)
    return render_template("car_detail.html", car=car)

@app.route("/request-quote/<int:car_id>")
def request_quote(car_id):
    car = CarListing.query.get_or_404(car_id)
    
    # Possibly compute monthlyPayment if needed:
    monthly_payment = "€295"  # Example placeholder
    
    return render_template(
        "request_quote.html",
        car=car,
        monthly_payment=monthly_payment
    )





# ------------------ Final Startup ------------------

# if __name__ == "__main__":
#     # Make sure tables exist
#     with app.app_context():
#         db.create_all()
#     # Then run the server
#     app.run(debug=True)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
