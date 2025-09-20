"""
Face Detection Service
Handles facial detection using OpenCV for PhotoVault
"""

import cv2
import os
import logging
from typing import List, Dict, Any, Optional
from PIL import Image
import numpy as np
from photovault.models import FaceDetection, Photo
from photovault.extensions import db

logger = logging.getLogger(__name__)

class FaceDetectionService:
    """Service for detecting faces in images using OpenCV"""
    
    def __init__(self):
        self._face_cascade = None
        self._load_cascade()
    
    def _load_cascade(self):
        """Load the Haar cascade for face detection"""
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self._face_cascade = cv2.CascadeClassifier(cascade_path)
            if self._face_cascade.empty():
                raise Exception("Failed to load face cascade")
            logger.info("Face detection cascade loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load face cascade: {str(e)}")
            self._face_cascade = None
    
    def detect_faces(self, image_path: str, max_image_size: int = 1024) -> List[Dict[str, Any]]:
        """
        Detect faces in an image
        
        Args:
            image_path: Path to the image file
            max_image_size: Maximum image dimension for processing (default 1024)
            
        Returns:
            List of face detection dictionaries with x, y, w, h, confidence, detector
        """
        if not self._face_cascade:
            logger.warning("Face cascade not available")
            return []
        
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return []
        
        try:
            # Load image using OpenCV
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Failed to load image: {image_path}")
                return []
            
            # Get original dimensions
            original_height, original_width = image.shape[:2]
            
            # Resize image if too large to speed up detection
            scale_factor = 1.0
            if max(original_width, original_height) > max_image_size:
                scale_factor = max_image_size / max(original_width, original_height)
                new_width = int(original_width * scale_factor)
                new_height = int(original_height * scale_factor)
                image = cv2.resize(image, (new_width, new_height))
            
            # Convert to grayscale for detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces using Haar cascade
            faces = self._face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            # Convert to list of dictionaries with original coordinates
            detections = []
            for (x, y, w, h) in faces:
                # Scale coordinates back to original image size
                orig_x = int(x / scale_factor)
                orig_y = int(y / scale_factor)
                orig_w = int(w / scale_factor)
                orig_h = int(h / scale_factor)
                
                # Basic confidence estimation based on size
                face_area = orig_w * orig_h
                image_area = original_width * original_height
                area_ratio = face_area / image_area
                confidence = min(0.9, max(0.3, area_ratio * 10))  # Rough confidence estimate
                
                detections.append({
                    'x': orig_x,
                    'y': orig_y,
                    'w': orig_w,
                    'h': orig_h,
                    'confidence': confidence,
                    'detector': 'haar'
                })
            
            logger.info(f"Detected {len(detections)} faces in {image_path}")
            return detections
            
        except Exception as e:
            logger.error(f"Error detecting faces in {image_path}: {str(e)}")
            return []
    
    def persist_detections(self, photo: Photo) -> int:
        """
        Run face detection on a photo and save results to database
        
        Args:
            photo: Photo model instance
            
        Returns:
            Number of faces detected and saved
        """
        try:
            # Run face detection
            detections = self.detect_faces(photo.file_path)
            
            if not detections:
                logger.info(f"No faces detected in photo {photo.id}")
                return 0
            
            # Save detections to database
            saved_count = 0
            for detection in detections:
                face_detection = FaceDetection(
                    photo_id=photo.id,
                    x=detection['x'],
                    y=detection['y'],
                    w=detection['w'],
                    h=detection['h'],
                    confidence=detection['confidence'],
                    detector=detection['detector'],
                    auto_detected=True
                )
                db.session.add(face_detection)
                saved_count += 1
            
            db.session.commit()
            logger.info(f"Saved {saved_count} face detections for photo {photo.id}")
            return saved_count
            
        except Exception as e:
            logger.error(f"Error persisting face detections for photo {photo.id}: {str(e)}")
            db.session.rollback()
            return 0
    
    def assign_face_to_person(self, face_detection_id: int, person_id: int) -> bool:
        """
        Assign a detected face to a person
        
        Args:
            face_detection_id: ID of the face detection
            person_id: ID of the person
            
        Returns:
            True if assignment was successful
        """
        try:
            face_detection = FaceDetection.query.get(face_detection_id)
            if not face_detection:
                logger.error(f"Face detection {face_detection_id} not found")
                return False
            
            face_detection.assigned_person_id = person_id
            db.session.commit()
            
            logger.info(f"Assigned face detection {face_detection_id} to person {person_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error assigning face detection {face_detection_id} to person {person_id}: {str(e)}")
            db.session.rollback()
            return False

# Global service instance
face_service = FaceDetectionService()