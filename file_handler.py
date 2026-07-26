"""
storage/file_handler.py
Module responsible for reading and writing data to text (.txt) files.
"""

import os
from typing import List, Dict, Optional

class FileHandler:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            # Default to data/ directory relative to project root
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(base_dir, "data")
        self.data_dir = data_dir
        self._ensure_directory_exists()

    def _ensure_directory_exists(self) -> None:
        """Ensure that the data directory exists."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)

    def get_file_path(self, filename: str) -> str:
        """Return the absolute path for a filename within the data directory."""
        return os.path.join(self.data_dir, filename)

    def ensure_file_exists(self, filename: str, headers: Optional[List[str]] = None) -> None:
        """Create file with optional header line if it does not already exist."""
        filepath = self.get_file_path(filename)
        if not os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                if headers:
                    f.write("|".join(headers) + "\n")

    def read_records(self, filename: str) -> List[Dict[str, str]]:
        """
        Reads a pipe-delimited text file.
        The first line is assumed to be headers.
        Returns a list of dictionaries mapping header -> value.
        """
        filepath = self.get_file_path(filename)
        if not os.path.exists(filepath):
            return []

        records = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
                if not lines:
                    return []
                
                headers = [h.strip() for h in lines[0].split("|")]
                for line in lines[1:]:
                    values = [v.strip() for v in line.split("|")]
                    if len(values) == len(headers):
                        records.append(dict(zip(headers, values)))
        except Exception as e:
            print(f"Error reading file {filename}: {e}")
            return []

        return records

    def write_records(self, filename: str, headers: List[str], records: List[Dict[str, str]]) -> bool:
        """
        Overwrites a text file with headers and a list of dictionary records.
        """
        filepath = self.get_file_path(filename)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("|".join(headers) + "\n")
                for record in records:
                    line = "|".join([str(record.get(h, "")) for h in headers])
                    f.write(line + "\n")
            return True
        except Exception as e:
            print(f"Error writing to file {filename}: {e}")
            return False

    def append_record(self, filename: str, headers: List[str], record: Dict[str, str]) -> bool:
        """
        Appends a single record to a file. Ensures file and header exist.
        """
        filepath = self.get_file_path(filename)
        file_exists = os.path.exists(filepath) and os.path.getsize(filepath) > 0

        try:
            with open(filepath, "a", encoding="utf-8") as f:
                if not file_exists:
                    f.write("|".join(headers) + "\n")
                line = "|".join([str(record.get(h, "")) for h in headers])
                f.write(line + "\n")
            return True
        except Exception as e:
            print(f"Error appending to file {filename}: {e}")
            return False
