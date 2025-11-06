"""
Face and Person Detection using YOLO

Combines:
- YOLO11n for person detection (30-40 FPS)
- YOLO-Face for face detection
"""
import cv2
import numpy as np
import structlog
from typing import List, Dict, Tuple, Optional
from ultralytics import YOLO
from .config import settings

logger = structlog.get_logger()


class Detection:
    """Detection result"""

    def __init__(
        self,
        bbox: Tuple[int, int, int, int],
        confidence: float,
        class_id: int,
        class_name: str,
    ):
        """
        Args:
            bbox: Bounding box (x1, y1, x2, y2)
            confidence: Detection confidence score
            class_id: Class ID
            class_name: Class name
        """
        self.bbox = bbox
        self.confidence = confidence
        self.class_id = class_id
        self.class_name = class_name
        self.x1, self.y1, self.x2, self.y2 = bbox

    @property
    def width(self) -> int:
        """Detection width in pixels"""
        return self.x2 - self.x1

    @property
    def height(self) -> int:
        """Detection height in pixels"""
        return self.y2 - self.y1

    @property
    def area(self) -> int:
        """Detection area in pixels"""
        return self.width * self.height

    @property
    def center(self) -> Tuple[int, int]:
        """Detection center point (cx, cy)"""
        return (self.x1 + self.width // 2, self.y1 + self.height // 2)

    def is_valid_face_size(self, min_size: int = 80) -> bool:
        """
        Check if face is large enough for recognition

        Args:
            min_size: Minimum size in pixels (default: 80x80)

        Returns:
            bool: True if face is large enough
        """
        return self.width >= min_size and self.height >= min_size

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "bbox": self.bbox,
            "confidence": float(self.confidence),
            "class_id": self.class_id,
            "class_name": self.class_name,
            "width": self.width,
            "height": self.height,
            "area": self.area,
            "center": self.center,
        }


class FacePersonDetector:
    """
    Combined Face and Person Detector

    Uses:
    - YOLO11n for person detection (fast, 30-40 FPS)
    - YOLO-Face for face detection (accurate)
    """

    def __init__(
        self,
        person_model_path: Optional[str] = None,
        face_model_path: Optional[str] = None,
        device: str = "cuda:0",
    ):
        """
        Initialize detectors

        Args:
            person_model_path: Path to YOLO11n model (default: from settings)
            face_model_path: Path to YOLO-Face model (default: from settings)
            device: Device to run on ('cuda:0', 'cpu')
        """
        self.device = device

        # Load person detection model (YOLO11n)
        person_model_path = person_model_path or settings.PERSON_DETECTION_MODEL
        logger.info("loading_person_detection_model", model=person_model_path)
        self.person_model = YOLO(person_model_path)
        self.person_model.to(device)

        # Load face detection model (YOLO-Face)
        face_model_path = face_model_path or settings.FACE_DETECTION_MODEL
        logger.info("loading_face_detection_model", model=face_model_path)
        self.face_model = YOLO(face_model_path)
        self.face_model.to(device)

        logger.info("detectors_initialized", device=device)

    def detect_persons(
        self,
        frame: np.ndarray,
        confidence_threshold: Optional[float] = None,
    ) -> List[Detection]:
        """
        Detect persons in frame

        Args:
            frame: Input frame (BGR)
            confidence_threshold: Confidence threshold (default: from settings)

        Returns:
            List[Detection]: List of person detections
        """
        if confidence_threshold is None:
            confidence_threshold = settings.PERSON_CONFIDENCE_THRESHOLD

        results = self.person_model(frame, verbose=False, conf=confidence_threshold)

        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Filter for 'person' class (class_id = 0 in COCO)
                if int(box.cls) == 0:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    confidence = float(box.conf)
                    detections.append(
                        Detection(
                            bbox=(x1, y1, x2, y2),
                            confidence=confidence,
                            class_id=0,
                            class_name="person",
                        )
                    )

        return detections

    def detect_faces(
        self,
        frame: np.ndarray,
        confidence_threshold: Optional[float] = None,
        min_face_size: Optional[int] = None,
    ) -> List[Detection]:
        """
        Detect faces in frame

        Args:
            frame: Input frame (BGR)
            confidence_threshold: Confidence threshold (default: from settings)
            min_face_size: Minimum face size in pixels (default: from settings)

        Returns:
            List[Detection]: List of face detections (filtered by size)
        """
        if confidence_threshold is None:
            confidence_threshold = settings.FACE_CONFIDENCE_THRESHOLD

        if min_face_size is None:
            min_face_size = settings.MIN_FACE_SIZE

        results = self.face_model(frame, verbose=False, conf=confidence_threshold)

        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence = float(box.conf)

                detection = Detection(
                    bbox=(x1, y1, x2, y2),
                    confidence=confidence,
                    class_id=0,
                    class_name="face",
                )

                # Filter by minimum face size
                if detection.is_valid_face_size(min_face_size):
                    detections.append(detection)
                else:
                    logger.debug(
                        "face_too_small",
                        width=detection.width,
                        height=detection.height,
                        min_size=min_face_size,
                    )

        return detections

    def detect_combined(
        self,
        frame: np.ndarray,
    ) -> Dict[str, List[Detection]]:
        """
        Detect both persons and faces in a single call

        Args:
            frame: Input frame (BGR)

        Returns:
            Dict with 'persons' and 'faces' lists
        """
        persons = self.detect_persons(frame)
        faces = self.detect_faces(frame)

        return {"persons": persons, "faces": faces}

    def crop_face(
        self,
        frame: np.ndarray,
        detection: Detection,
        margin: float = 0.2,
    ) -> np.ndarray:
        """
        Crop face from frame with margin

        Args:
            frame: Input frame (BGR)
            detection: Face detection
            margin: Margin to add around face (default: 0.2 = 20%)

        Returns:
            np.ndarray: Cropped face image
        """
        x1, y1, x2, y2 = detection.bbox
        w, h = detection.width, detection.height

        # Add margin
        margin_w = int(w * margin)
        margin_h = int(h * margin)

        # Expand bbox with margin
        x1 = max(0, x1 - margin_w)
        y1 = max(0, y1 - margin_h)
        x2 = min(frame.shape[1], x2 + margin_w)
        y2 = min(frame.shape[0], y2 + margin_h)

        # Crop
        face_crop = frame[y1:y2, x1:x2]

        return face_crop

    def draw_detections(
        self,
        frame: np.ndarray,
        persons: List[Detection],
        faces: List[Detection],
    ) -> np.ndarray:
        """
        Draw detections on frame (for visualization/debugging)

        Args:
            frame: Input frame (BGR)
            persons: List of person detections
            faces: List of face detections

        Returns:
            np.ndarray: Frame with drawn detections
        """
        frame_copy = frame.copy()

        # Draw persons (green)
        for person in persons:
            x1, y1, x2, y2 = person.bbox
            cv2.rectangle(frame_copy, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"Person: {person.confidence:.2f}"
            cv2.putText(
                frame_copy,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )

        # Draw faces (blue)
        for face in faces:
            x1, y1, x2, y2 = face.bbox
            cv2.rectangle(frame_copy, (x1, y1), (x2, y2), (255, 0, 0), 2)
            label = f"Face: {face.confidence:.2f} ({face.width}x{face.height})"
            cv2.putText(
                frame_copy,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 0, 0),
                2,
            )

        return frame_copy
