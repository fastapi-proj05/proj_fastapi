from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class MedicalRecordDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    chart_number: str
    symptoms: str
    xray_image_url: str
    is_pneumonia: Optional[bool] = None
    confidence: Optional[float] = None
    ai_model: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class PatientMedicalRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    chart_number: str
    symptoms: str
    created_at: datetime
    updated_at: Optional[datetime] = None

