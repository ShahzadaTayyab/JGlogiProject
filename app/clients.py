# app/clients.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models
from typing import List
import pandas as pd
from io import BytesIO

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Upload clients from file
@router.post("/upload")
async def upload_clients(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Check file extension
    if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
        raise HTTPException(status_code=400, detail="Invalid file type")

    # Read file content
    contents = await file.read()
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(BytesIO(contents), dtype=str)
        else:
            df = pd.read_excel(BytesIO(contents), dtype=str)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {e}")

    df.fillna('', inplace=True)

    # Process each row
    for _, row in df.iterrows():
        client_data = row.to_dict()
        # Clean and normalize keys
        client_dict = {k.lower().strip().replace('.', '').replace(' ', '_'): v.strip() for k, v in client_data.items()}
        customer_code = client_dict.get('customer_code')
        if not customer_code:
            continue  # Skip if customer code is missing

        # Check for duplicates
        existing_client = db.query(models.Client).filter(models.Client.customer_code == customer_code).first()
        if existing_client:
            continue  # Skip duplicates

        # Create new client
        client = models.Client(
            no=int(client_dict.get('no', 0)) if client_dict.get('no') else None,
            name=client_dict.get('name'),
            customer_code=customer_code,
            address=client_dict.get('address'),
            tel=client_dict.get('tel'),
            fax=client_dict.get('fax'),
            email=client_dict.get('email')
        )
        db.add(client)

    db.commit()
    return {"message": "Clients uploaded successfully"}

# Get all clients
@router.get("/", response_model=List[dict])
def get_clients(db: Session = Depends(get_db)):
    try:
        clients = db.query(models.Client).all()
        # Convert each client to a dictionary excluding SQLAlchemy internal state
        return [{
            'client_id': client.client_id,
            'no': client.no,
            'name': client.name,
            'customer_code': client.customer_code,
            'address': client.address,
            'tel': client.tel,
            'fax': client.fax,
            'email': client.email
        } for client in clients]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching clients: {e}")

# Get client by ID
@router.get("/{client_id}", response_model=dict)
def get_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.client_id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return {
        'client_id': client.client_id,
        'no': client.no,
        'name': client.name,
        'customer_code': client.customer_code,
        'address': client.address,
        'tel': client.tel,
        'fax': client.fax,
        'email': client.email
    }

# Create a new client
@router.post("/", response_model=dict)
def create_client(client_data: dict, db: Session = Depends(get_db)):
    customer_code = client_data.get('customer_code')
    if not customer_code:
        raise HTTPException(status_code=400, detail="Customer code is required")

    existing_client = db.query(models.Client).filter(models.Client.customer_code == customer_code).first()
    if existing_client:
        raise HTTPException(status_code=400, detail="Client with this customer code already exists")

    client = models.Client(
        no=client_data.get('no'),
        name=client_data.get('name'),
        customer_code=customer_code,
        address=client_data.get('address'),
        tel=client_data.get('tel'),
        fax=client_data.get('fax'),
        email=client_data.get('email')
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client.__dict__

# Update a client
@router.put("/{client_id}", response_model=dict)
def update_client(client_id: int, client_data: dict, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.client_id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    for key, value in client_data.items():
        setattr(client, key, value)
    db.commit()
    db.refresh(client)
    return client.__dict__

# Delete a client
@router.delete("/{client_id}", response_model=dict)
def delete_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.client_id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    db.delete(client)
    db.commit()
    return {"message": "Client deleted successfully"}
