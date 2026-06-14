import json
import time
from worker.redis_client import get_sync_redis
from worker.inference import run_prediction

TASK_QUEUE = "pneumonia_task_queue"
PROCESSING_QUEUE = "pneumonia_processing_queue"

def process_task(task_data: dict):
    record_id = task_data["record_id"]
    image_path = task_data["image_path"]
    model_key = task_data.get("model_key", "FastViT-SA12")

    print(f"[Worker] 작업 시작 - record_id: {record_id}")

    try:
        is_pneumonia, confidence, model_name = run_prediction(image_path, model_key)
        result = {
            "record_id": record_id,
            "is_pneumonia": is_pneumonia,
            "confidence": confidence,
            "model_key": model_name,
            "status": "success"
        }
    except Exception as e:
        result = {
            "record_id": record_id,
            "status": "error",
            "error": str(e)
        }

    # 결과를 Redis에 Publish
    r = get_sync_redis()
    channel = f"prediction_result:{record_id}"
    r.publish(channel, json.dumps(result))
    print(f"[Worker] 결과 발행 완료 - channel: {channel}")


def main():
    r = get_sync_redis()
    print("[Worker] AI Worker 시작 - 작업 대기 중...")

    while True:
        try:
            # BRPOPLPUSH: task_queue에서 꺼내 processing_queue로 이동 (안전한 큐)
            task_json = r.brpoplpush(TASK_QUEUE, PROCESSING_QUEUE, timeout=5)

            if task_json is None:
                continue

            task_data = json.loads(task_json)
            process_task(task_data)

            # 처리 완료 후 processing_queue에서 제거
            r.lrem(PROCESSING_QUEUE, 1, task_json)

        except Exception as e:
            print(f"[Worker] 오류 발생: {e}")
            time.sleep(1)


if __name__ == "__main__":
    main()