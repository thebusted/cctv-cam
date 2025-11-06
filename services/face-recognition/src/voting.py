"""
Multi-frame Verification for Face Recognition

Implements:
- Multi-frame verification (check 3 frames, 1 second apart)
- Temporal consistency checking
- False positive reduction
"""
import structlog
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import deque
from .recognizer import RecognitionResult
from .config import settings

logger = structlog.get_logger()


class FrameVerification:
    """Single frame verification result"""

    def __init__(
        self,
        timestamp: datetime,
        result: RecognitionResult,
    ):
        self.timestamp = timestamp
        self.result = result


class MultiFrameVerifier:
    """
    Multi-frame Verification System

    Verifies face recognition across multiple frames to reduce false positives.

    Strategy:
    - Collect recognition results from multiple frames (default: 3 frames)
    - Frames should be ~1 second apart
    - Verify consistency: same person across all frames
    - Final decision: majority vote
    """

    def __init__(
        self,
        verification_frames: Optional[int] = None,
        verification_interval: Optional[float] = None,
        history_ttl: int = 30,
    ):
        """
        Initialize Multi-frame Verifier

        Args:
            verification_frames: Number of frames to verify (default: from settings)
            verification_interval: Time interval between frames in seconds (default: from settings)
            history_ttl: Time to keep verification history in seconds (default: 30)
        """
        self.verification_frames = verification_frames or settings.VERIFICATION_FRAMES
        self.verification_interval = (
            verification_interval or settings.VERIFICATION_INTERVAL
        )
        self.history_ttl = history_ttl

        # History of verifications per tracking_id
        # tracking_id -> deque of FrameVerification
        self.verification_history: Dict[str, deque] = {}

        logger.info(
            "multi_frame_verifier_initialized",
            verification_frames=self.verification_frames,
            verification_interval=self.verification_interval,
        )

    def add_verification(
        self,
        tracking_id: str,
        result: RecognitionResult,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """
        Add a verification result for a tracked person

        Args:
            tracking_id: Unique tracking ID (from DeepSORT or similar)
            result: Recognition result
            timestamp: Timestamp of verification (default: now)
        """
        if timestamp is None:
            timestamp = datetime.now()

        # Initialize history if needed
        if tracking_id not in self.verification_history:
            self.verification_history[tracking_id] = deque(
                maxlen=self.verification_frames * 2  # Keep extra for analysis
            )

        # Add verification
        verification = FrameVerification(timestamp=timestamp, result=result)
        self.verification_history[tracking_id].append(verification)

        logger.debug(
            "verification_added",
            tracking_id=tracking_id,
            person_id=result.person_id,
            decision=result.decision,
            vote_percentage=result.vote_percentage,
        )

    def verify_identity(
        self,
        tracking_id: str,
        require_recent: bool = True,
    ) -> Optional[RecognitionResult]:
        """
        Verify identity across multiple frames

        Args:
            tracking_id: Unique tracking ID
            require_recent: Only consider recent frames within verification_interval

        Returns:
            RecognitionResult: Verified result or None if not enough data
        """
        if tracking_id not in self.verification_history:
            return None

        history = self.verification_history[tracking_id]

        if len(history) < self.verification_frames:
            logger.debug(
                "insufficient_frames",
                tracking_id=tracking_id,
                current=len(history),
                required=self.verification_frames,
            )
            return None

        # Get recent verifications
        now = datetime.now()
        recent_verifications = []

        for verification in reversed(history):  # Start from most recent
            time_diff = (now - verification.timestamp).total_seconds()

            if require_recent:
                # Only consider frames within the verification window
                max_age = self.verification_interval * (self.verification_frames - 1) + 5
                if time_diff > max_age:
                    continue

            recent_verifications.append(verification)

            if len(recent_verifications) >= self.verification_frames:
                break

        if len(recent_verifications) < self.verification_frames:
            logger.debug(
                "insufficient_recent_frames",
                tracking_id=tracking_id,
                recent=len(recent_verifications),
                required=self.verification_frames,
            )
            return None

        # Check temporal spacing (should be ~1 second apart)
        if require_recent and len(recent_verifications) >= 2:
            intervals = []
            for i in range(len(recent_verifications) - 1):
                interval = (
                    recent_verifications[i].timestamp
                    - recent_verifications[i + 1].timestamp
                ).total_seconds()
                intervals.append(abs(interval))

            avg_interval = sum(intervals) / len(intervals)
            if avg_interval < self.verification_interval * 0.5:
                logger.warning(
                    "frames_too_close",
                    tracking_id=tracking_id,
                    avg_interval=avg_interval,
                    expected=self.verification_interval,
                )

        # Perform voting across frames
        return self._vote_across_frames(tracking_id, recent_verifications)

    def _vote_across_frames(
        self,
        tracking_id: str,
        verifications: List[FrameVerification],
    ) -> RecognitionResult:
        """
        Vote across multiple frames to determine final identity

        Strategy:
        - Count votes for each person_id
        - Require majority (> 50%) to confirm identity
        - Average similarity scores

        Args:
            tracking_id: Unique tracking ID
            verifications: List of verification results

        Returns:
            RecognitionResult: Final verified result
        """
        # Count votes per person_id
        votes: Dict[str, List[RecognitionResult]] = {}

        for verification in verifications:
            result = verification.result

            # Only count MATCH decisions
            if result.decision != "MATCH":
                continue

            person_id = result.person_id
            if person_id not in votes:
                votes[person_id] = []
            votes[person_id].append(result)

        # No matches found
        if not votes:
            return RecognitionResult(
                person_id=None,
                full_name=None,
                similarity=0.0,
                vote_count=0,
                total_embeddings=len(verifications),
                vote_percentage=0.0,
                decision="NO_MATCH",
            )

        # Find person with most votes
        best_person_id = max(votes.keys(), key=lambda pid: len(votes[pid]))
        best_results = votes[best_person_id]

        # Calculate statistics
        total_frames = len(verifications)
        match_count = len(best_results)
        vote_percentage = match_count / total_frames
        avg_similarity = sum(r.similarity for r in best_results) / match_count

        # Require majority (> 50%)
        if vote_percentage > 0.5:
            decision = "MATCH"
        else:
            decision = "NO_MATCH"

        logger.info(
            "multi_frame_verification_complete",
            tracking_id=tracking_id,
            person_id=best_person_id,
            decision=decision,
            vote_percentage=vote_percentage,
            match_count=match_count,
            total_frames=total_frames,
        )

        return RecognitionResult(
            person_id=best_person_id,
            full_name=best_results[0].full_name,
            similarity=avg_similarity,
            vote_count=match_count,
            total_embeddings=total_frames,
            vote_percentage=vote_percentage,
            decision=decision,
        )

    def cleanup_old_history(self) -> None:
        """Remove old verification history to prevent memory buildup"""
        now = datetime.now()
        ttl_threshold = timedelta(seconds=self.history_ttl)

        tracking_ids_to_remove = []

        for tracking_id, history in self.verification_history.items():
            if not history:
                tracking_ids_to_remove.append(tracking_id)
                continue

            # Check last verification time
            last_verification = history[-1]
            age = now - last_verification.timestamp

            if age > ttl_threshold:
                tracking_ids_to_remove.append(tracking_id)

        # Remove old histories
        for tracking_id in tracking_ids_to_remove:
            del self.verification_history[tracking_id]
            logger.debug("removed_old_history", tracking_id=tracking_id)

    def get_status(self) -> dict:
        """Get verifier status"""
        return {
            "active_tracks": len(self.verification_history),
            "verification_frames": self.verification_frames,
            "verification_interval": self.verification_interval,
            "history_ttl": self.history_ttl,
        }
