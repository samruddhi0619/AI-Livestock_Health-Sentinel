from pydantic import BaseModel, Field
from typing import List, Optional

class UserRegister(BaseModel):
    username: str
    password: str
    fullname: str
    role: str # FARMER, VETERINARIAN, OFFICER, ADMIN
    phone: Optional[str] = ""
    village: Optional[str] = ""
    taluka: Optional[str] = ""
    district: Optional[str] = ""

class UserLogin(BaseModel):
    username: str
    password: str

class AnimalCreate(BaseModel):
    species: str = "Cattle"
    breed: str
    age: float
    gender: str
    health_history: Optional[str] = "None"
    farm_id: str
    latitude: float
    longitude: float
    village: str
    taluka: str
    district: str

class HealthRecordCreate(BaseModel):
    symptoms: List[str]
    temperature: float = 38.5
    appetite: float = 1.0 # 0=None, 1=Normal, 2=High
    milk_production: float = 15.0
    activity: float = 1.0 # 0=Low, 1=Normal, 2=High
    observations: Optional[str] = ""
    image_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    village: Optional[str] = None
    taluka: Optional[str] = None
    district: Optional[str] = None

class CaseVerifyRequest(BaseModel):
    status: str # VERIFIED, REJECTED
    diagnosis: str
    treatment: str
    follow_up: Optional[str] = ""

class VaccinationCreate(BaseModel):
    animal_id: str
    vaccine_name: str
    date_administered: str
    next_due_date: str
