import os
import json
import uuid
import shutil
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.db.databases import async_get_db
from app.core.redis_client import get_redis
from app.models.record import MedicalRecord
from app.schemas.record import MedicalRecordDetail

router = APIRouter(prefix="/api/v1/medical-records", tags=["Medical Records"])

UPLOAD_DIR = Path("static/uploads/xray")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".dcm"}

TASK_QUEUE = "pneumonia_task_queue"
PROCESSING_QUEUE = "pneumonia_processing_queue"

# 임시 메모리 저장소
mock_analyses = {}


def _validate_image(file: UploadFile) -> None:
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"지원하지 않는 파일 형식입니다. 허용: {ALLOWED_EXTENSIONS}",
        )

def _save_image(file: UploadFile) -> str:
    ext = Path(file.filename).suffix.lower()
    filename = f"{uuid.uuid4().hex}{ext}"
    dest = UPLOAD_DIR / filename
    with dest.open("wb") as buf:
        shutil.copyfileobj(file.file, buf)
    return f"static/uploads/xray/{filename}"

def _image_url(request: Request, path: str) -> str:
    if not path:
        return ""
    filename = Path(path).name
    return f"{request.base_url}static/uploads/xray/{filename}"


@router.post("", response_model=MedicalRecordDetail, status_code=status.HTTP_201_CREATED)
async def create_medical_record(
    request: Request,
    patient_id: int = Form(...),
    chart_number: str = Form(...),
    symptoms: str = Form(...),
    xray_image: UploadFile = File(...),
    db: AsyncSession = Depends(async_get_db)
):
    _validate_image(xray_image)
    saved_path = _save_image(xray_image)

    new_record = MedicalRecord(
        patient_id=patient_id,
        chart_number=chart_number,
        symptoms=symptoms,
        xray_image_path=saved_path
    )
    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)

    return MedicalRecordDetail(
        id=new_record.id,
        patient_id=new_record.patient_id,
        chart_number=new_record.chart_number,
        symptoms=new_record.symptoms,
        xray_image_url=_image_url(request, new_record.xray_image_path),
        created_at=new_record.created_at,
        updated_at=new_record.updated_at
    )


@router.get("/{record_id}", response_model=MedicalRecordDetail)
async def get_medical_record(
    record_id: int,
    request: Request,
    db: AsyncSession = Depends(async_get_db)
):
    result = await db.execute(select(MedicalRecord).where(MedicalRecord.id == record_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"진료기록 ID {record_id}을(를) 찾을 수 없습니다."
        )

    return MedicalRecordDetail(
        id=record.id,
        patient_id=record.patient_id,
        chart_number=record.chart_number,
        symptoms=record.symptoms,
        xray_image_url=_image_url(request, record.xray_image_path),
        created_at=record.created_at,
        updated_at=record.updated_at
    )


@router.post("/{record_id}/predict")
async def predict_pneumonia(
    record_id: int,
    db: AsyncSession = Depends(async_get_db)
):
    # 레코드 존재 여부 확인
    result = await db.execute(select(MedicalRecord).where(MedicalRecord.id == record_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="진료기록을 찾을 수 없습니다."
        )

    # 같은 진료기록으로 이미 예측한 결과가 있으면 DB 캐시 반환
    if record.is_pneumonia is not None:
        print(f"[DB Cache Hit] 이미 예측된 진료기록입니다. DB 캐시 결과를 즉시 반환합니다. - record_id: {record_id}")
        return [
            {
                "id": 1,
                "is_pneumonia": record.is_pneumonia,
                "confidence": record.confidence,
                "hitmap_image_url": "",
                "created_at": record.updated_at.isoformat() if record.updated_at else record.created_at.isoformat(),
                "ai_model": record.ai_model or "FastViT-SA12"
            }
        ]

    # Redis에 작업 등록
    r = await get_redis()
    task = {
        "record_id": record_id,
        "image_path": record.xray_image_path,
        "model_key": "FastViT-SA12"
    }
    await r.lpush(TASK_QUEUE, json.dumps(task))

    # 결과 Subscribe (최대 30초 대기)
    pubsub = r.pubsub()
    channel = f"prediction_result:{record_id}"
    await pubsub.subscribe(channel)

    try:
        for _ in range(300):  # 0.1초 * 300 = 30초
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                result_data = json.loads(message["data"])
                if result_data.get("status") == "error":
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=result_data.get("error")
                    )

                # DB에 예측결과 영구 저장
                record.is_pneumonia = result_data["is_pneumonia"]
                record.confidence = result_data["confidence"]
                record.ai_model = result_data["model_key"]
                record.updated_at = datetime.utcnow()
                db.add(record)
                await db.commit()
                await db.refresh(record)

                analysis = {
                    "id": 1,
                    "is_pneumonia": record.is_pneumonia,
                    "confidence": record.confidence,
                    "hitmap_image_url": "",
                    "created_at": record.updated_at.isoformat(),
                    "ai_model": record.ai_model
                }
                return analysis

            await asyncio.sleep(0.1)
    finally:
        await pubsub.unsubscribe(channel)

    raise HTTPException(
        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        detail="AI 추론 타임아웃 (30초 초과)"
    )


@router.get("/{record_id}/analyses")
async def get_medical_record_analyses(
    record_id: int,
    db: AsyncSession = Depends(async_get_db)
):
    result = await db.execute(select(MedicalRecord).where(MedicalRecord.id == record_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="진료기록을 찾을 수 없습니다."
        )

    if record.is_pneumonia is not None:
        return [
            {
                "id": 1,
                "is_pneumonia": record.is_pneumonia,
                "confidence": record.confidence,
                "hitmap_image_url": "",
                "created_at": record.updated_at.isoformat() if record.updated_at else record.created_at.isoformat(),
                "ai_model": record.ai_model or "FastViT-SA12"
            }
        ]
    return []