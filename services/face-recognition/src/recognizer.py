"""
Face Recognition using ArcFace Embeddings

Features:
- ArcFace embeddings (512-dimensional)
- Similarity threshold: 0.35
- Voting mechanism: 60% of embeddings must agree
- Multi-frame verification
"""
import cv2
import numpy as np
import structlog
from typing import List, Dict, Optional, Tuple
from insightface.app import FaceAnalysis
from insightface.model_zoo import get_model
from .config import settings
from .detector import Detection

logger = structlog.get_logger()


class FaceEmbedding:
    """Face embedding representation"""

    def __init__(
        self,
        embedding: np.ndarray,
        detection: Detection,
        quality_score: float = 1.0,
    ):
        """
        Args:
            embedding: Face embedding vector (512-dim)
            detection: Face detection
            quality_score: Quality score (0-1)
        """
        self.embedding = embedding
        self.detection = detection
        self.quality_score = quality_score

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "embedding": self.embedding.tolist(),
            "detection": self.detection.to_dict(),
            "quality_score": float(self.quality_score),
        }


class RecognitionResult:
    """Face recognition result"""

    def __init__(
        self,
        person_id: Optional[str],
        full_name: Optional[str],
        similarity: float,
        vote_count: int,
        total_embeddings: int,
        vote_percentage: float,
        decision: str,  # 'MATCH' or 'NO_MATCH' or 'UNKNOWN'
    ):
        self.person_id = person_id
        self.full_name = full_name
        self.similarity = similarity
        self.vote_count = vote_count
        self.total_embeddings = total_embeddings
        self.vote_percentage = vote_percentage
        self.decision = decision

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "person_id": self.person_id,
            "full_name": self.full_name,
            "similarity": float(self.similarity),
            "vote_count": self.vote_count,
            "total_embeddings": self.total_embeddings,
            "vote_percentage": float(self.vote_percentage),
            "decision": self.decision,
        }


class ArcFaceRecognizer:
    """
    Face Recognition using ArcFace

    Uses InsightFace's buffalo_l model (99.82% accuracy on LFW)
    512-dimensional embeddings
    """

    def __init__(
        self,
        model_name: str = "buffalo_l",
        device: str = "cuda",
    ):
        """
        Initialize ArcFace recognizer

        Args:
            model_name: InsightFace model name (default: buffalo_l)
            device: Device to run on ('cuda' or 'cpu')
        """
        self.model_name = model_name
        self.device = device

        logger.info("loading_arcface_model", model=model_name, device=device)

        # Initialize FaceAnalysis
        ctx_id = 0 if device == "cuda" else -1
        self.app = FaceAnalysis(
            name=model_name,
            providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
            if device == "cuda"
            else ["CPUExecutionProvider"],
        )
        self.app.prepare(ctx_id=ctx_id, det_size=(640, 640))

        logger.info("arcface_model_loaded")

    def extract_embedding(
        self,
        face_crop: np.ndarray,
        return_quality: bool = True,
    ) -> Optional[FaceEmbedding]:
        """
        Extract face embedding from cropped face image

        Args:
            face_crop: Cropped face image (BGR)
            return_quality: Whether to compute quality score

        Returns:
            FaceEmbedding or None if face not detected
        """
        try:
            # Convert BGR to RGB
            face_rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)

            # Detect and extract features
            faces = self.app.get(face_rgb)

            if len(faces) == 0:
                logger.warning("no_face_detected_in_crop")
                return None

            # Get the first (and should be only) face
            face = faces[0]

            # Extract embedding (512-dim)
            embedding = face.embedding

            # Compute quality score (if needed)
            quality_score = 1.0
            if return_quality:
                quality_score = self._compute_quality_score(face)

            # Create dummy detection (we don't have bbox here)
            h, w = face_crop.shape[:2]
            detection = Detection(
                bbox=(0, 0, w, h),
                confidence=face.det_score if hasattr(face, "det_score") else 1.0,
                class_id=0,
                class_name="face",
            )

            return FaceEmbedding(
                embedding=embedding,
                detection=detection,
                quality_score=quality_score,
            )

        except Exception as e:
            logger.error("embedding_extraction_failed", error=str(e))
            return None

    def _compute_quality_score(self, face) -> float:
        """
        Compute face quality score based on various factors

        Factors:
        - Detection confidence
        - Age (prefer clear adult faces)
        - Face angle (prefer frontal faces)

        Args:
            face: InsightFace face object

        Returns:
            float: Quality score (0-1)
        """
        score = 1.0

        # Detection confidence
        if hasattr(face, "det_score"):
            score *= face.det_score

        # Penalize extreme ages (possible detection errors)
        if hasattr(face, "age"):
            age = face.age
            if age < 10 or age > 80:
                score *= 0.8

        # Penalize non-frontal faces
        if hasattr(face, "pose"):
            # Pose: [pitch, yaw, roll]
            pose = face.pose
            max_angle = max(abs(pose[0]), abs(pose[1]), abs(pose[2]))
            if max_angle > 30:
                score *= 0.7
            elif max_angle > 15:
                score *= 0.9

        return score

    def compute_similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray,
    ) -> float:
        """
        Compute cosine similarity between two embeddings

        Args:
            embedding1: First embedding (512-dim)
            embedding2: Second embedding (512-dim)

        Returns:
            float: Similarity score (0-1, higher is more similar)
        """
        # Cosine similarity
        similarity = np.dot(embedding1, embedding2) / (
            np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        )

        # Convert from [-1, 1] to [0, 1]
        similarity = (similarity + 1) / 2

        return float(similarity)

    def recognize_face(
        self,
        query_embedding: np.ndarray,
        registered_embeddings: List[Dict],
        similarity_threshold: Optional[float] = None,
        voting_threshold: Optional[float] = None,
    ) -> RecognitionResult:
        """
        Recognize face using voting mechanism

        Args:
            query_embedding: Query face embedding (512-dim)
            registered_embeddings: List of registered embeddings with metadata:
                [
                    {
                        'person_id': 'EMP001',
                        'full_name': 'John Doe',
                        'embedding': np.ndarray (512-dim),
                        'is_active': True
                    },
                    ...
                ]
            similarity_threshold: Similarity threshold (default: from settings)
            voting_threshold: Voting threshold (default: from settings)

        Returns:
            RecognitionResult
        """
        if similarity_threshold is None:
            similarity_threshold = settings.SIMILARITY_THRESHOLD

        if voting_threshold is None:
            voting_threshold = settings.VOTING_THRESHOLD

        # Group embeddings by person_id
        person_embeddings = {}
        for item in registered_embeddings:
            if not item.get("is_active", True):
                continue

            person_id = item["person_id"]
            if person_id not in person_embeddings:
                person_embeddings[person_id] = {
                    "person_id": person_id,
                    "full_name": item.get("full_name", "Unknown"),
                    "embeddings": [],
                }
            person_embeddings[person_id]["embeddings"].append(item["embedding"])

        # Compute votes for each person
        best_match = None
        best_vote_percentage = 0.0
        best_similarity = 0.0

        for person_id, data in person_embeddings.items():
            embeddings = data["embeddings"]
            total_embeddings = len(embeddings)

            # Compute similarity with each embedding
            similarities = []
            for emb in embeddings:
                sim = self.compute_similarity(query_embedding, emb)
                similarities.append(sim)

            # Count votes (similarity > threshold)
            high_confidence_votes = sum(1 for sim in similarities if sim > similarity_threshold)
            avg_similarity = np.mean(similarities)
            vote_percentage = high_confidence_votes / total_embeddings

            # Check if this is the best match
            if vote_percentage > best_vote_percentage:
                best_vote_percentage = vote_percentage
                best_similarity = avg_similarity
                best_match = {
                    "person_id": person_id,
                    "full_name": data["full_name"],
                    "vote_count": high_confidence_votes,
                    "total_embeddings": total_embeddings,
                    "similarity": avg_similarity,
                }

        # Make decision
        if best_match is None:
            return RecognitionResult(
                person_id=None,
                full_name=None,
                similarity=0.0,
                vote_count=0,
                total_embeddings=0,
                vote_percentage=0.0,
                decision="UNKNOWN",
            )

        # Check voting threshold (60% must agree)
        if best_vote_percentage >= voting_threshold:
            decision = "MATCH"
        else:
            decision = "NO_MATCH"

        return RecognitionResult(
            person_id=best_match["person_id"],
            full_name=best_match["full_name"],
            similarity=best_match["similarity"],
            vote_count=best_match["vote_count"],
            total_embeddings=best_match["total_embeddings"],
            vote_percentage=best_vote_percentage,
            decision=decision,
        )

    def batch_extract_embeddings(
        self,
        face_crops: List[np.ndarray],
    ) -> List[Optional[FaceEmbedding]]:
        """
        Extract embeddings from multiple face crops

        Args:
            face_crops: List of cropped face images (BGR)

        Returns:
            List[Optional[FaceEmbedding]]: List of embeddings (None if failed)
        """
        embeddings = []
        for face_crop in face_crops:
            emb = self.extract_embedding(face_crop)
            embeddings.append(emb)
        return embeddings
