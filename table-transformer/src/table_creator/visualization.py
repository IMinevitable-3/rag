from typing import List, Tuple, Union
import cv2
import numpy as np
from PIL import Image

class TableVisualizer:
    """
    Utility class for visualizing detected tables and OCR results.
    """
    
    @staticmethod
    def draw_boxes(
        image: Union[np.ndarray, Image.Image],
        boxes: List[List[int]],
        color: Tuple[int, int, int] = (0, 255, 0),
        thickness: int = 2
    ) -> Image.Image:
        """
        Draw bounding boxes on an image.
        
        Args:
            image: Input image
            boxes: List of bounding box coordinates [x1, y1, x2, y2]
            color: RGB color for the boxes
            thickness: Line thickness
            
        Returns:
            Image with drawn bounding boxes
        """
        if isinstance(image, Image.Image):
            image = np.array(image)
            
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
            
        image_copy = image.copy()
        
        for box in boxes:
            cv2.rectangle(
                image_copy,
                (box[0], box[1]),
                (box[2], box[3]),
                color,
                thickness
            )
            
        return Image.fromarray(image_copy)

    @staticmethod
    def draw_text_boxes(
        image: Union[np.ndarray, Image.Image],
        text_data: List[Tuple[str, List[int]]],
        color: Tuple[int, int, int] = (255, 0, 0),
        thickness: int = 1
    ) -> Image.Image:
        """
        Draw text boxes with labels on an image.
        
        Args:
            image: Input image
            text_data: List of (text, bbox) tuples
            color: RGB color for the boxes
            thickness: Line thickness
            
        Returns:
            Image with drawn text boxes
        """
        if isinstance(image, Image.Image):
            image = np.array(image)
            
        image_copy = image.copy()
        
        for text, bbox in text_data:
            cv2.rectangle(
                image_copy,
                (bbox[0], bbox[1]),
                (bbox[2], bbox[3]),
                color,
                thickness
            )
            cv2.putText(
                image_copy,
                text[:20],
                (bbox[0], bbox[1] - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                thickness
            )
            
        return Image.fromarray(image_copy)