import os
import cv2
import numpy as np
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class SegmentedInstance:
    class_id: int
    class_name: str
    confidence: float
    box: List[float]  # [x1, y1, x2, y2]
    area_pixels: int
    area_percentage: float


@dataclass
class YOLOSegmentationResult:
    has_detections: bool
    num_instances: int
    combined_mask: np.ndarray  # uint8 (0 o 255) de tamaño (H, W)
    instances: List[SegmentedInstance] = field(default_factory=list)
    annotated_image: Optional[np.ndarray] = None
    avg_confidence: float = 0.0
    model_name: str = ""


class YOLOSegmenter:
    _instance: Optional["YOLOSegmenter"] = None
    _model: Any = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(YOLOSegmenter, cls).__new__(cls)
            cls._instance._model = None
            cls._instance._loaded_model_path = None
        return cls._instance

    def _load_model(self):
        """Carga diferida del modelo YOLO-seg."""
        if self._model is not None:
            return self._model

        from ultralytics import YOLO

        model_path = settings.YOLO_SEG_MODEL_PATH

        # Si no existe como ruta absoluta o local, buscar en carpeta models o dejar que ultralytics lo descargue
        if not os.path.isabs(model_path) and not os.path.exists(model_path):
            candidate_in_models = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models", model_path)
            if os.path.exists(candidate_in_models):
                model_path = candidate_in_models

        logger.info(f"Cargando modelo YOLO-seg desde: {model_path}")
        try:
            self._model = YOLO(model_path)
            self._loaded_model_path = model_path
            logger.info(f"Modelo YOLO-seg ({model_path}) cargado exitosamente.")
        except Exception as e:
            logger.error(f"Error al cargar el modelo YOLO-seg: {e}")
            raise e

        return self._model

    def segment(
        self,
        image_bgr: np.ndarray,
        conf_threshold: Optional[float] = None,
    ) -> YOLOSegmentationResult:
        """
        Ejecuta la inferencia de segmentación de instancias sobre una imagen BGR.
        Retorna la máscara combinada de vegetación/instancias, conteo y detalles.
        """
        h, w = image_bgr.shape[:2]
        total_pixels = h * w
        conf = conf_threshold if conf_threshold is not None else settings.YOLO_CONF_THRESHOLD

        try:
            model = self._load_model()
            results = model.predict(
                source=image_bgr,
                conf=conf,
                device=settings.YOLO_DEVICE,
                verbose=False,
            )
        except Exception as e:
            logger.warning(f"No se pudo ejecutar YOLO-seg ({e}). Retornando resultado vacío.")
            return YOLOSegmentationResult(
                has_detections=False,
                num_instances=0,
                combined_mask=np.zeros((h, w), dtype=np.uint8),
                instances=[],
                annotated_image=image_bgr.copy(),
                avg_confidence=0.0,
                model_name=settings.YOLO_SEG_MODEL_PATH,
            )

        if not results or len(results) == 0:
            return YOLOSegmentationResult(
                has_detections=False,
                num_instances=0,
                combined_mask=np.zeros((h, w), dtype=np.uint8),
                instances=[],
                annotated_image=image_bgr.copy(),
                avg_confidence=0.0,
                model_name=settings.YOLO_SEG_MODEL_PATH,
            )

        res = results[0]
        names = res.names or {}

        # Generar imagen anotada con el contorno y etiquetas de segmentación
        annotated = res.plot() if settings.SAVE_SEGMENTATION_OVERLAY else None

        combined_mask = np.zeros((h, w), dtype=np.uint8)
        instances_list: List[SegmentedInstance] = []
        confidences: List[float] = []

        if res.masks is not None and len(res.masks) > 0:
            # res.masks.data tiene forma (N, orig_H, orig_W) o (N, net_H, net_W)
            # res.masks.xy contiene los polígonos correspondientes a la escala de la imagen original
            for i, polygon in enumerate(res.masks.xy):
                if len(polygon) == 0:
                    continue

                # Crear máscara binaria para esta instancia
                inst_mask = np.zeros((h, w), dtype=np.uint8)
                pts = polygon.astype(np.int32).reshape((-1, 1, 2))
                cv2.fillPoly(inst_mask, [pts], 255)

                # Acumular en la máscara global
                combined_mask = cv2.bitwise_or(combined_mask, inst_mask)

                # Extraer información de la caja y clase
                box_info = res.boxes[i] if res.boxes is not None and len(res.boxes) > i else None
                cls_id = int(box_info.cls.item()) if box_info is not None else 0
                conf_val = float(box_info.conf.item()) if box_info is not None else float(conf)
                cls_name = names.get(cls_id, f"class_{cls_id}")

                inst_pixels = int(np.count_nonzero(inst_mask))
                pct = (inst_pixels / total_pixels) * 100.0

                confidences.append(conf_val)
                instances_list.append(
                    SegmentedInstance(
                        class_id=cls_id,
                        class_name=cls_name,
                        confidence=round(conf_val, 3),
                        box=[round(float(c), 1) for c in (box_info.xyxy[0].tolist() if box_info is not None else [0, 0, 0, 0])],
                        area_pixels=inst_pixels,
                        area_percentage=round(pct, 2),
                    )
                )

        avg_conf = float(np.mean(confidences)) if confidences else 0.0

        return YOLOSegmentationResult(
            has_detections=len(instances_list) > 0,
            num_instances=len(instances_list),
            combined_mask=combined_mask,
            instances=instances_list,
            annotated_image=annotated if annotated is not None else image_bgr.copy(),
            avg_confidence=round(avg_conf, 3),
            model_name=os.path.basename(self._loaded_model_path or settings.YOLO_SEG_MODEL_PATH),
        )


yolo_segmenter = YOLOSegmenter()
