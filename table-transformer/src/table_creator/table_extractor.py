from models.table_detector import TableDetector
from models.text_recognizer import TextRecognizer
from table_creator.data_structures import TableStructure
import pandas as pd
import re

class TableExtraction:
    def __init__(self) -> None:
        self._table_detection = TableDetector()
        self._document_ocr = TextRecognizer()
        self._linklist = TableStructure()

    def _merge_words(self, prev_obj, word, word_bb):
        """Merge the current word with the previous one if they overlap significantly."""
        merged_text = prev_obj[0] + ' ' + word
        merged_bb = [
            prev_obj[1][0], prev_obj[1][1], word_bb[2], word_bb[3]
        ]
        return (merged_text, merged_bb)

    def _assign_to_column(self, word, word_bb, columns, df, debug=False):
        """Assign a word to the correct column based on bounding box overlap."""
        for key, col_bb in columns.items():
            word_bb_temp = [word_bb[0], col_bb[1], word_bb[2], col_bb[3]]
            overlap = self._table_detection._calculate_overlap(word_bb_temp, col_bb)

            if overlap > 10:
                if len(df[key]) > 0:
                    prev_obj = df[key][-1]
                    prev_overlap = self._table_detection._calculate_overlap(
                        prev_obj[1], [prev_obj[1][0], word_bb[1], prev_obj[1][2], word_bb[3]]
                    )
                    if prev_overlap >= 30:
                        word, word_bb = self._merge_words(prev_obj, word, word_bb)
                        df[key][-1] = (word, word_bb)
                    else:
                        df[key].append((word, word_bb))
                else:
                    df[key].append((word, word_bb))
                    # Dynamically adjust the column bounding box to fit the new word
                    columns[key] = [
                        min(word_bb[0], col_bb[0]), col_bb[1],
                        max(word_bb[2], col_bb[2]), col_bb[3]
                    ]
                return True
        return False
    
    def _get_normalized_bounding_box(self, imgsz : str, bb : list) -> pd.DataFrame:
        names = ['pdf1','sample_pdf2.pdf']
        pass

    def get_words_in_column(self, cords: dict, df_word: pd.DataFrame, merge=True, debug=False):
        """Distribute words into their respective columns based on bounding box coordinates."""
        df = {key: [] for key in cords}
        unknown_columns = {}
        unknown_data = {}

        for index, row in df_word.iterrows():
            word, word_bb = row['text'], list(map(int, row['boundingBox']))
            if debug:
                print(f"\nProcessing word: '{word}'")

            if not self._assign_to_column(word, word_bb, cords, df, debug):
                # Handle words that do not match any known column
                for key, val in unknown_columns.items():
                    overlap = self._table_detection._calculate_overlap(
                        val, [word_bb[0], val[1], word_bb[2], val[3]]
                    )
                    if overlap > 30:
                        prev_obj = unknown_data[key][-1]
                        prev_overlap = self._table_detection._calculate_overlap(
                            prev_obj[1], [prev_obj[1][0], word_bb[1], prev_obj[1][2], word_bb[3]]
                        )
                        if prev_overlap >= 30:
                            word, word_bb = self._merge_words(prev_obj, word, word_bb)
                            unknown_data[key][-1] = (word, word_bb)
                        else:
                            unknown_data[key].append((word, word_bb))
                        break
                else:
                    # Create a new unknown column if no match is found
                    unknown_key = f'{word}__{index}__'
                    unknown_columns[unknown_key] = word_bb
                    unknown_data[unknown_key] = [(word, word_bb)]

        if merge:
            df.update(unknown_data)

        # Convert lists to DataFrames
        df = {key: pd.DataFrame(val, columns=['text', 'boundingBox']) for key, val in df.items()}
        return df, unknown_data, unknown_columns

    def postprocess(self, parsed_df: pd.DataFrame, columns=None):
        """Post-process the parsed DataFrame to merge columns and clean data."""
        try:
            parsed_df = parsed_df.dropna(how='all').reset_index(drop=True)
            new_df = pd.DataFrame()
            
            # Merge adjacent empty header columns
            empty_columns = parsed_df.columns[parsed_df.iloc[:1].isna().all()].tolist()
            for col in empty_columns[::-1]:
                col_idx = list(parsed_df.columns).index(col)
                if col_idx > 0:
                    parsed_df.iloc[:, col_idx - 1] += ' ' + parsed_df.iloc[:, col_idx]
            parsed_df = parsed_df.drop(columns=empty_columns)

            if not columns:
                return parsed_df

            used_indices = set()
            for header in columns:
                match_indices = [i for i, col in enumerate(parsed_df.columns) if header in col]
                if match_indices:
                    used_indices.update(match_indices)
                    new_df[header] = parsed_df.iloc[:, match_indices].apply(
                        lambda x: ' '.join(x.fillna('').str.strip()), axis=1
                    )

            # Include unused columns
            unused_columns = [col for i, col in enumerate(parsed_df.columns) if i not in used_indices]
            new_df = pd.concat([new_df, parsed_df[unused_columns]], axis=1)

            return new_df
        except Exception as e:
            print(f"Error in postprocess: {e}")
            return parsed_df

    def detect(self, image_path: str):
        """Detect tables in an image and extract their data."""
        cords = self._table_detection.detect(image_path)
        all_table_df = self._document_ocr.recognize(image_path, cords)
        
        table_data = []
        for table in all_table_df:
            column_data, _, _ = self.get_words_in_column({}, table)
            ordered_columns = sorted(column_data, key=lambda x: column_data[x].iloc[0]['boundingBox'][0])
            dictword = {col: column_data[col] for col in ordered_columns}

            df = self._linklist.build_structure(dictword)
            df = df.loc[:, ordered_columns]
            df = df.rename(columns=lambda col: re.sub(r'__\d+__', '', str(col)).strip())
            df_postp = self.postprocess(df)

            # Assign generic column names
            df.columns = [f"column {i+1}" for i in range(df.shape[1])]
            table_data.append((df, df_postp))

        return table_data[0], cords
