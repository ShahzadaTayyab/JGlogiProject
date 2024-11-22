# app/bookings.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models
from typing import List
import pandas as pd
from io import BytesIO
# from app.email_utils import send_confirmation_email

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Upload bookings from file
@router.post("/upload")
async def upload_bookings(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents))
        
        # Define the column names in order
        db_columns = [
            'no', 'pl_mod', 'modd', 'shipper', 'customer_code', 'booking_no',
            'booking_status', 'bl_no', 'bl_status', 'doc_link', 'cnt_no',
            'unit_m3', 'noc', 'line', 'open_date', 'cut_date', 'etd', 'eta',
            'vessel', 'voyage', 'pol', 'pod', 'p_base_bof', 'p_bof', 'p_crs',
            'p_cdd', 'p_thc', 'p_seal', 'p_doc_star', 'p_doc', 'p_others',
            'p_taxable_ttl', 'p_vat', 'p_exvat_ttl', 'p_pay_ttl', 's_inv_date',
            's_inv_no', 's_link', 'days', 'pay_date', 'usd_ex', 'eur_ex',
            'r_base_bof', 'r_bof', 'r_crs', 'r_cdd', 'r_thc', 'r_seal',
            'r_doc', 'r_others', 'r_taxable_ttl', 'r_vat', 'r_exvat_ttl',
            'r_adjustments', 'rec_ttl', 'c_inv_date', 'c_inv_no', 'c_link',
            'rec_date', 'profit'
        ]

        # Rename DataFrame columns using index
        df.columns = db_columns[:len(df.columns)]
        
        # Replace empty strings with NaN
        df = df.replace(r'^\s*$', pd.NA, regex=True)
        
        # Define date fields
        date_fields = [
            'open_date', 'cut_date', 'etd', 'eta', 
            's_inv_date', 'pay_date', 
            'c_inv_date', 'rec_date'
        ]
        
        numeric_fields = {
            'no': int,
            'unit_m3': float,
            'noc': int,
            'p_base_bof': float,
            'p_bof': float,
            'p_crs': float,
            'p_cdd': float,
            'p_thc': float,
            'p_seal': float,
            'p_doc_star': float,
            'p_doc': float,
            'p_others': float,
            'p_taxable_ttl': float,
            'p_vat': float,
            'p_exvat_ttl': float,
            'p_pay_ttl': float,
            'usd_ex': float,
            'eur_ex': float,
            'r_base_bof': float,
            'r_bof': float,
            'r_crs': float,
            'r_cdd': float,
            'r_thc': float,
            'r_seal': float,
            'r_doc': float,
            'r_others': float,
            'r_taxable_ttl': float,
            'r_vat': float,
            'r_exvat_ttl': float,
            'r_adjustments': float,
            'rec_ttl': float,
            'profit': float
        }

        string_fields = [
        'pl_mod', 'modd', 'shipper', 'customer_code', 
        'booking_no', 'booking_status', 'bl_no', 'bl_status',
        'doc_link', 'cnt_no', 'line', 'vessel', 'voyage',
        'pol', 'pod', 's_inv_no', 's_link',
        'c_inv_no', 'c_link'
        ]

        bookings = []
        for _, row in df.iterrows():
            booking_dict = row.to_dict()
            
            # Process date fields
            for field in date_fields:
                value = booking_dict.get(field)
                if pd.isna(value) or value == '' or value is None:
                    booking_dict[field] = None
                else:
                    try:
                        date_value = pd.to_datetime(value)
                        booking_dict[field] = date_value.date()
                    except:
                        booking_dict[field] = None

            # Process numeric fields
            for field, type_func in numeric_fields.items():
                value = booking_dict.get(field)
                if pd.isna(value) or value == '' or value is None:
                    booking_dict[field] = None
                else:
                    try:
                        booking_dict[field] = type_func(value)
                    except:
                        booking_dict[field] = None

            # Process string fields
            for field in string_fields:
                value = booking_dict.get(field)
                if pd.isna(value) or value == '' or value is None:
                    booking_dict[field] = ''
                else:
                    booking_dict[field] = str(value)

            bookings.append(models.Booking(**booking_dict))

        db.bulk_save_objects(bookings)
        db.commit()
        
        return {"message": f"Successfully uploaded {len(bookings)} bookings"}
        
    except Exception as e:
        db.rollback()
        print(f"Error: {str(e)}")  # Add this for debugging
        raise HTTPException(status_code=400, detail=str(e))

# Get all bookings
@router.get("/")
def get_bookings(db: Session = Depends(get_db)):
    bookings = db.query(models.Booking).all()
    # Convert SQLAlchemy models to dictionaries, excluding SQLAlchemy internal state
    return [
        {key: value for key, value in booking.__dict__.items() 
         if not key.startswith('_')}
        for booking in bookings
    ]

# Get booking by ID
@router.get("/{booking_id}")
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(models.Booking.booking_id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    # Convert SQLAlchemy model to dictionary, excluding SQLAlchemy internal state
    return {key: value for key, value in booking.__dict__.items() 
            if not key.startswith('_')}

# Confirm a booking
@router.post("/{booking_id}/confirm")
def confirm_booking(booking_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(models.Booking.booking_id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    booking.status = 'CONFIRMED'
    db.commit()
    db.refresh(booking)

    client = db.query(models.Client).filter(models.Client.customer_code == booking.customer_code).first()
    if client and client.email:
        subject = f"Booking {booking.booking_no} Confirmed"
        content = f"""
        Dear {client.name},<br><br>
        Your booking with Booking Number {booking.booking_no} has been confirmed.<br><br>
        Best regards,<br>
        Your Company
        """
        # Send email in the background
        # background_tasks.add_task(send_confirmation_email, client.email, subject, content)

    return {"message": "Booking confirmed and email sent if applicable"}

# Other CRUD operations as needed (create, update, delete bookings)
