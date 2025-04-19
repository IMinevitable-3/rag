from pathlib import Path
from typing import Optional, Union
import numpy as np
from ultralytics import YOLO
# from ultralyticsplus import YOLO


class TableDetector:
    """
    A class for detecting tables in document images using YOLO models.
    
    Attributes:
        model_path (Path): Path to the YOLO model weights
        confidence (float): Confidence threshold for detection
        iou_threshold (float): IoU threshold for NMS
    """
    
    def __init__(
        self,
        confidence: float = 0.50,
        iou_threshold: float = 0.45
    ) -> None:
        """
        Initialize the TableDetector with model and parameters.
        
        Args:
            model_path: Path to the YOLO model weights
            confidence: Confidence threshold for detection
            iou_threshold: IoU threshold for NMS
        """
        self.model_path = 'src/models/table-detection-and-extraction.pt'
        self.model = YOLO(str(self.model_path))
        self.min_conf = confidence
        self.iou = iou_threshold

    def detect(self, image_path: Union[str, Path]) -> Optional[np.ndarray]:
        """
        Detect tables in the given image.
        
        Args:
            image_path: Path to the input image
            
        Returns:
            Array of bounding box coordinates or None if no tables detected
        """
        results = self.model.predict(str(image_path), verbose=False, iou = self.iou, conf = self.min_conf)
        if results:
            print('boxes :\n',results[0])
            boxes = results[0].boxes.xyxy.numpy()
            cord =  self.merge_boxes(boxes)
            print('cords : ',cord)
            return [sorted(cord, key = lambda x : (x[2]-x[0])* (x[3]-x[1]), reverse=True)[0]] if len(cord) > 0 else []
        return None

    def merge_boxes(self, boxes: np.ndarray, overlap_threshold: float = 35) -> np.ndarray:
        """
        Merge overlapping bounding boxes.
        
        Args:
            boxes: Array of bounding box coordinates
            overlap_threshold: Threshold for merging overlapping boxes
            
        Returns:
            Array of merged bounding box coordinates
        """
        # Sort boxes by area in descending order
        areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
        sorted_indices = np.argsort(-areas)
        boxes = boxes[sorted_indices]
        
        merged_boxes = []
        
        for box in boxes:
            if not merged_boxes:
                merged_boxes.append(box)
                continue
                
            overlap_found = False
            for i, merged_box in enumerate(merged_boxes):
                iou = self._calculate_overlap(box, merged_box)
                if iou > overlap_threshold:
                    # Keep the larger box
                    box_area = (box[2] - box[0]) * (box[3] - box[1])
                    merged_area = (merged_box[2] - merged_box[0]) * (merged_box[3] - merged_box[1])
                    if box_area > merged_area:
                        merged_boxes[i] = box
                    overlap_found = True
                    break
                    
            if not overlap_found:
                merged_boxes.append(box)
        
        return np.array(merged_boxes).astype(int)

    @staticmethod
    def _calculate_overlap(box1: np.ndarray, box2: np.ndarray) -> float:
        """
        Calculate the percentage overlap between two boxes.
        
        Args:
            box1: First bounding box coordinates
            box2: Second bounding box coordinates
            
        Returns:
            Percentage of overlap between the boxes
        """
        x_left = max(box1[0], box2[0])
        y_top = max(box1[1], box2[1])
        x_right = min(box1[2], box2[2])
        y_bottom = min(box1[3], box2[3])

        if x_right < x_left or y_bottom < y_top:
            return 0.0

        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
        box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])

        min_area = min(box1_area, box2_area)
        if min_area == 0:
            return 0.0
            
        return (intersection_area / min_area) * 100