from pathlib import Path
from typing import List, Optional, Dict, Union
import numpy as np
import pandas as pd
from paddleocr import PaddleOCR
from PIL import Image

class TextRecognizer:
    """
    A class for performing OCR on detected tables using PaddleOCR.
    
    Attributes:
        models_dir (Path): Directory containing OCR model files
    """
    
    def __init__(self, models_dir: Optional[Union[str, Path]] = None) -> None:
        """
        Initialize the TextRecognizer with model directory.
        
        Args:
            models_dir: Directory containing OCR model files
        """
        self.models_dir = Path(models_dir) if models_dir else Path(__file__).parent / 'paddleocr_models'
        self._setup_model_dirs()
        
        self.model = PaddleOCR(
            use_angle_cls=False,
            lang='en',
            det_model_dir=str(self.models_dir / 'det'),
            rec_model_dir=str(self.models_dir / 'rec')
        )

    def _setup_model_dirs(self) -> None:
        """Create necessary directories for model files."""
        (self.models_dir / 'det').mkdir(parents=True, exist_ok=True)
        (self.models_dir / 'rec').mkdir(parents=True, exist_ok=True)

    def recognize(
        self, 
        image_path: Union[str, Path], 
        table_boxes: Optional[np.ndarray] = None,
        padding: tuple = (0, 0)
    ) -> List[pd.DataFrame]:
        """
        Perform OCR on the image within specified table regions.
        
        Args:
            image_path: Path to the input image
            table_boxes: Array of table bounding box coordinates
            padding: Padding to add around table regions (x, y)
            
        Returns:
            List of DataFrames containing extracted text and positions
        """
        with Image.open(image_path) as img:
            img_array = np.array(img.convert('RGB'))
            
        if table_boxes is not None and len(table_boxes) == 1:
            pad_x, pad_y = padding
            box = table_boxes[0]
            img_array = img_array[
                max(box[1]-pad_y, 0):box[3]+pad_y,
                max(box[0]-pad_x, 0):box[2]+pad_x
            ]
            
        ocr_result = self.model.ocr(img_array)
        
        if table_boxes is not None and len(table_boxes) > 1:
            return self._process_multiple_tables(ocr_result[0], table_boxes)
        return self._process_single_table(ocr_result[0])

    def _process_multiple_tables(
        self, 
        ocr_data: List, 
        table_boxes: np.ndarray
    ) -> List[pd.DataFrame]:
        """Process OCR results for multiple tables."""
        result: Dict[int, List] = {}
        
        for item in ocr_data:
            bbox = np.array(item[0]).astype(int)
            word = item[1][0]
            bbox = [bbox[:,0].min(), bbox[:,1].min(), bbox[:,0].max(), bbox[:,1].max()]
            
            for idx, table_box in enumerate(table_boxes):
                if (bbox[0] >= table_box[0] and bbox[1] >= table_box[1] and 
                    bbox[0] <= table_box[2] and bbox[1] <= table_box[3]):
                    if idx not in result:
                        result[idx] = []
                    result[idx].append((word, bbox))
                    
        return [
            pd.DataFrame(
                sorted(table_data, key=lambda x: (x[1][1], x[1][0])),
                columns=['text', 'boundingBox']
            )
            for table_data in result.values()
        ]

    def _process_single_table(self, ocr_data: List) -> List[pd.DataFrame]:
        """Process OCR results for a single table."""
        processed_data = [
            (item[1][0], [
                np.array(item[0])[:,0].min(),
                np.array(item[0])[:,1].min(),
                np.array(item[0])[:,0].max(),
                np.array(item[0])[:,1].max()
            ])
            for item in ocr_data
        ]
        
        return [pd.DataFrame(
            sorted(processed_data, key=lambda x: (x[1][1], x[1][0])),
            columns=['text', 'boundingBox']
        )]