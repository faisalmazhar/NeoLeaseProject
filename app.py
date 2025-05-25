# app.py

from flask import Flask, render_template, request, abort, send_from_directory
from flask_compress import Compress
from flask_caching import Cache
from models import db, CarListing
import logging
from sqlalchemy import func  # Add this import for random()
app = Flask(__name__)
Compress(app)
from utils import parse_price  # or put the function above directly in app.py
import pprint, sys, logging
from decimal import Decimal, ROUND_HALF_UP
import re

# Use the same connection style as your CSV script
# app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost:5432/neolease_db"
# app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://neolease_db_user:DKuNZ0Z4OhuNKWvEFaAuWINgr7BfgyTE@dpg-cvslkuvdiees73fiv97g-a.oregon-postgres.render.com:5432/neolease_db"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://neolease_db_kpz9_user:33H6QVFnAouvau72DlSjuKAMe5GdfviD@dpg-d0f0ihh5pdvs73b6h3bg-a.oregon-postgres.render.com:5432/neolease_db_kpz9"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# ------------------ Define Routes Below ------------------


# ── Configure Flask-Caching ──
app.config["CACHE_TYPE"] = "simple"       # in-memory; swap for RedisCache in prod
app.config["CACHE_DEFAULT_TIMEOUT"] = 86400 # 5 minutes
cache = Cache(app)


@app.template_filter("euro")                 # {{ value|euro }}
def format_euro(value):
    """
    Render anything that looks like a price as:
        €12.345,67   or   €12.345,-   (if no cents)
    – thousands = dot,  decimals = comma
    – accepts:  '20950', '20.950,-', 20950.0, Decimal, None
    """
    if value in (None, ""):
        return ""

    # keep digits & dots only  →  "€20.950,-" → "20.950"
    cleaned = re.sub(r"[^\d.]", "", str(value))
    if cleaned == "":
        return ""

    amount = Decimal(cleaned).quantize(Decimal("0.01"), ROUND_HALF_UP)

    euros      = int(amount)
    cents_part = int((amount - euros) * 100)

    euros_str = f"{euros:,}".replace(",", ".")     # 12345 -> '12.345'

    return f"€{euros_str},-" if cents_part == 0 else f"€{euros_str},{cents_part:02d}"


@app.route('/robots.txt')
def robots_txt():
    return send_from_directory('static', 'robots.txt')


@app.before_request
def block_bad_bots():
    user_agent = request.headers.get('User-Agent', '').lower()
    blocked_bots = ['gptbot', 'ahrefs', 'mj12bot', 'semrush']
    if any(bot in user_agent for bot in blocked_bots):
        abort(403)
        
@app.route("/")
@cache.cached()
def index():
    
    # 1) total cars count
    total_cars = CarListing.query.count()

    # 2) distinct brand list
    distinct_brands = db.session.query(CarListing.merk)\
                        .filter(CarListing.merk.isnot(None))\
                        .distinct()\
                        .order_by(CarListing.merk.asc())\
                        .all()
    brand_choices = [b[0] for b in distinct_brands if b[0]]
    # print(brand_choices)
    random_cars = CarListing.query.order_by(func.random()).limit(10).all()

    return render_template("index.html", total_cars=total_cars, random_cars=random_cars, brand_choices=brand_choices)



@app.route('/calculator')
def general_calculator():
    # Maybe just show a generic form or instructions
    return render_template('calculator_general.html')



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

@app.route("/disclaimer")
def disclaimer():
    return render_template("disclaimer.html")

@app.route("/short-lease")
def short_lease():
    return render_template("short_lease.html")


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
@cache.cached(query_string=True)
def listings():
    page = request.args.get("page", 1, type=int)
    per_page = 16

    # distinct brand list
    distinct_brands = db.session.query(CarListing.merk)\
                        .filter(CarListing.merk.isnot(None))\
                        .distinct()\
                        .order_by(CarListing.merk.asc())\
                        .all()
    brand_choices = [b[0] for b in distinct_brands if b[0]]

    # Gather filters
    brand_filter   = request.args.get("brand")
    search_query   = request.args.get("q")
    
    # The new monthly range string, e.g. "200-299" or "1000+"
    monthly_param  = request.args.get("monthly")

    query = CarListing.query
    
    # brand
    if brand_filter:
        query = query.filter(CarListing.merk.ilike(f"%{brand_filter}%"))

    # If the user typed a free-text search
    if search_query:
        from sqlalchemy import or_
        query = query.filter(
            or_(
                CarListing.title.ilike(f"%{search_query}%"),
                CarListing.subtitle.ilike(f"%{search_query}%"),
                CarListing.model.ilike(f"%{search_query}%")
            )
        )

    # If we got a monthly param (like "200-299", "1-99", or "1000+"), 
    # convert that to total price range:
    if monthly_param:
        if monthly_param.endswith("+"):                      # "> 700"
            min_monthly = float(monthly_param.rstrip("+"))   # 700
            total_min   = (min_monthly + 1) * 60             # >= 701 €/mnd
            query = query.filter(
                db.func.cast(
                    db.func.regexp_replace(CarListing.prijs, '[^0-9]', '', 'g'),
                    db.Float
                ) >= total_min
            )
        else:
            try:
                lo, hi = map(float, monthly_param.split("-"))   # e.g. 301-400
                total_lo = lo * 60
                total_hi = hi * 60
                query = query.filter(
                    db.func.cast(
                        db.func.regexp_replace(CarListing.prijs, '[^0-9]', '', 'g'),
                        db.Float
                    ).between(total_lo, total_hi)
                )
            except ValueError:
                pass   # ignore malformed input

    # (Optional) if you still want sorting logic
    sort = request.args.get("sort")
    if sort == "price_asc":
        query = query.order_by(
            db.func.cast(db.func.regexp_replace(CarListing.prijs, '[^0-9]', '', 'g'), db.Float).asc()
        )
    elif sort == "price_desc":
        query = query.order_by(
            db.func.cast(db.func.regexp_replace(CarListing.prijs, '[^0-9]', '', 'g'), db.Float).desc()
        )
    elif sort is None:
    # no explicit sort → shuffle results every request
        query = query.order_by(func.random())

    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # Right after pagination = query.paginate(...):

    page = pagination.page          # The current page
    total_pages = pagination.pages  # The total number of pages

    # 1) Try to center "page" with +/-2
    start_page = page - 2
    if start_page < 1:
        start_page = 1

    end_page = page + 2
    if end_page > total_pages:
        end_page = total_pages

    # 2) Make sure we always show 5 pages if possible
    window_size = end_page - start_page + 1
    if window_size < 5:
        if start_page == 1:
            # Bump end_page up if we can
            end_page = min(total_pages, start_page + 4)
        else:
            # Shift start_page down
            start_page = max(1, end_page - 4)



    return render_template(
        "listings.html",
        cars=pagination.items,
        page=page,
        total_pages=pagination.pages,
        start_page=start_page,     # <--- ADD THIS
        end_page=end_page,         # <--- AND THIS
        brand_choices=brand_choices,
        current_brand=brand_filter,
        current_q=search_query,
        current_sort=sort,
        current_monthly=monthly_param,     # <--- Add this line
        pagination=pagination
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
@cache.cached()
def car_detail(car_id):
    # Grab the CarListing from DB or 404
    car = CarListing.query.get_or_404(car_id)
    random_cars = CarListing.query.order_by(func.random()).limit(10).all()


    # logging.warning("CAR %s DUMP:\n%s",
    #                 car_id,
    #                 pprint.pformat({k: getattr(car, k) for k in car.__table__.columns.keys()},
    #                                width=120))
    
    return render_template(
        "car_detail.html",
        car=car,
        random_cars=random_cars   # <-- pass these to the template
        )

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
