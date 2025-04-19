from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

@dataclass
class TableCell:
    """
    Represents a cell in a table with its value and position.
    
    Attributes:
        value: The text content of the cell
        bbox: Bounding box coordinates [x1, y1, x2, y2]
        column_name: Name of the column this cell belongs to
    """
    value: str
    bbox: List[int]
    column_name: str

@dataclass
class TableRow:
    """
    Represents a row in a table with its cells and boundaries.
    
    Attributes:
        cells: Dictionary of column name to TableCell
        min_x: Minimum x coordinate of the row
        max_x: Maximum x coordinate of the row
        min_y: Minimum y coordinate of the row
        max_y: Maximum y coordinate of the row
    """
    cells: Dict[str, TableCell]
    min_x: float
    max_x: float
    min_y: float
    max_y: float

class TableStructure:
    """
    Maintains the structure of a table using a linked list representation.
    """
    
    def __init__(self, debug: bool = False) -> None:
        """
        Initialize the table structure.
        
        Args:
            debug: Enable debug logging
        """
        self.rows: List[TableRow] = []
        self.debug = debug

    def build_structure(self, dataframes: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Build table structure from column-wise dataframes.
        
        Args:
            dataframes: Dictionary of column name to DataFrame containing text and positions
            
        Returns:
            DataFrame with structured table data
        """
        if not dataframes:
            return pd.DataFrame()

        # Initialize with first column
        first_col = list(dataframes.keys())[0]
        self._initialize_rows(first_col, dataframes[first_col])
        
        # Process remaining columns
        for col_name in list(dataframes.keys())[1:]:
            self._process_column(col_name, dataframes[col_name])
            
        return self._to_dataframe(dataframes.keys())

    def _initialize_rows(self, column_name: str, df: pd.DataFrame) -> None:
        """Initialize rows with the first column's data."""
        for _, row in df.iterrows():
            bbox = row['boundingBox']
            self.rows.append(TableRow(
                cells={column_name: TableCell(row['text'], bbox, column_name)},
                min_x=bbox[0],
                max_x=bbox[2],
                min_y=bbox[1],
                max_y=bbox[3]
            ))

    def _process_column(self, column_name: str, df: pd.DataFrame) -> None:
        """Process additional columns and align with existing rows."""
        search_idx = 0
        
        for _, row in df.iterrows():
            text = row['text']
            bbox = row['boundingBox']
            
            matched = False
            for idx, table_row in enumerate(self.rows[search_idx:], search_idx):
                overlap = self._calculate_overlap(
                    bbox,
                    [bbox[0], table_row.min_y, bbox[2], table_row.max_y]
                )
                
                if overlap > 10:
                    self._update_row(idx, column_name, text, bbox)
                    search_idx = idx + 1
                    matched = True
                    break
                elif bbox[3] <= table_row.min_y:
                    self._insert_row(idx, column_name, text, bbox)
                    search_idx = idx + 1
                    matched = True
                    break
                
            if not matched and bbox[1] >= self.rows[-1].max_y:
                self._append_row(column_name, text, bbox)

    def _calculate_overlap(self, rect1: List[int], rect2: List[int]) -> float:
        """Calculate percentage overlap between two rectangles."""
        x_left = max(rect1[0], rect2[0])
        y_top = max(rect1[1], rect2[1])
        x_right = min(rect1[2], rect2[2])
        y_bottom = min(rect1[3], rect2[3])

        if x_right < x_left or y_bottom < y_top:
            return 0.0

        intersection = (x_right - x_left) * (y_bottom - y_top)
        min_area = min(
            (rect1[2] - rect1[0]) * (rect1[3] - rect1[1]),
            (rect2[2] - rect2[0]) * (rect2[3] - rect2[1])
        )
        
        return (intersection / min_area * 100) if min_area > 0 else 0

    def _update_row(self, idx: int, column_name: str, text: str, bbox: List[int]) -> None:
        """Update existing row with new cell data."""
        self.rows[idx].cells[column_name] = TableCell(text, bbox, column_name)
        self.rows[idx].min_x = min(self.rows[idx].min_x, bbox[0])
        self.rows[idx].max_x = max(self.rows[idx].max_x, bbox[2])

    def _insert_row(self, idx: int, column_name: str, text: str, bbox: List[int]) -> None:
        """Insert new row at specified index."""
        self.rows.insert(idx, TableRow(
            cells={column_name: TableCell(text, bbox, column_name)},
            min_x=bbox[0],
            max_x=bbox[2],
            min_y=bbox[1],
            max_y=bbox[3]
        ))

    def _append_row(self, column_name: str, text: str, bbox: List[int]) -> None:
        """Append new row at the end."""
        self.rows.append(TableRow(
            cells={column_name: TableCell(text, bbox, column_name)},
            min_x=bbox[0],
            max_x=bbox[2],
            min_y=bbox[1],
            max_y=bbox[3]
        ))

    def _to_dataframe(self, columns: List[str]) -> pd.DataFrame:
        """Convert table structure to DataFrame."""
        data = []
        for row in self.rows:
            row_data = {
                col: row.cells[col].value if col in row.cells else None
                for col in columns
            }
            row_data.update({
                'row_min_x': row.min_x,
                'row_max_x': row.max_x,
                'row_min_y': row.min_y,
                'row_max_y': row.max_y
            })
            data.append(row_data)
            
        return pd.DataFrame(data)