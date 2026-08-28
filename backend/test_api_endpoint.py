import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(__file__))

from app.main import app
from app.core.database import SessionLocal, Base, engine
from app.models.models import Plant, Species

client = TestClient(app)

def test_api():
    print("=== Probando Endpoint FastAPI con YOLO-seg ===")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Asegurar una planta de prueba
    plant = db.query(Plant).first()
    if not plant:
        plant = Plant(name="Monstera Test", species=Species.HORTALIZA, location="Invernadero 1")
        db.add(plant)
        db.commit()
        db.refresh(plant)
    plant_id = plant.id
    db.close()

    # Enviar imagen para análisis
    image_path = os.path.join(os.path.dirname(__file__), "uploads", "test_plant.jpg")
    with open(image_path, "rb") as f:
        response = client.post(
            "/api/v1/analysis/analyze",
            data={"plant_id": plant_id, "source": "test_script"},
            files={"file": ("test_plant.jpg", f, "image/jpeg")},
        )

    print(f"Status code: {response.status_code}")
    assert response.status_code == 201, f"Error en endpoint: {response.text}"
    data = response.json()
    print("Respuesta recibida:")
    print(f"  • Image ID: {data['image_id']}")
    print(f"  • Health Score: {data['analysis']['health_score']}")
    print(f"  • Health Status: {data['analysis']['health_status']}")
    print(f"  • Green Coverage: {data['analysis']['green_coverage']}%")
    print(f"  • Leaf count: {data['analysis']['estimated_leaf_count']}")
    print(f"  • Notes: {data['analysis']['notes']}")
    print(f"  • Recomendación de riego: {data['analysis']['recommendation']['water_amount_ml']} ml cada {data['analysis']['recommendation']['frequency_days']} días")
    print("=== Endpoint FastAPI validado con éxito ===")

if __name__ == "__main__":
    test_api()
