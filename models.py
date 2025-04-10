# models.py

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class CarListing(db.Model):
    __tablename__ = 'car_listings'
    
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(300))
    title = db.Column(db.String(200))
    subtitle = db.Column(db.String(200))
    financial_lease_price = db.Column(db.String(100))
    financial_lease_term = db.Column(db.String(100))
    advertentienummer = db.Column(db.String(100))
    merk = db.Column(db.String(100))
    model = db.Column(db.String(100))
    bouwjaar = db.Column(db.String(10))
    km_stand = db.Column(db.String(50))
    transmissie = db.Column(db.String(50))
    prijs = db.Column(db.String(50))
    brandstof = db.Column(db.String(50))
    btw_marge = db.Column(db.String(50))
    opties_accessoires = db.Column(db.Text)
    address = db.Column(db.String(200))
    
    # Here’s the relationship to multiple images
    images = db.relationship(
        'CarImage',       # the child model
        backref='car_listing',
        cascade='all, delete-orphan',
        lazy=True
    )

class CarImage(db.Model):
    __tablename__ = 'car_images'
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(500), nullable=False)
    car_listing_id = db.Column(
        db.Integer,
        db.ForeignKey('car_listings.id'),
        nullable=False
    )
