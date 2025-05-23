"""
This module provides a unified interface for loading data from various sources.
"""

from .general_loader import GeneralLoader
from .url_loader import URLLoader
from .pdf_loader import PDFLoader
from .excel_loader import ExcelLoader

__all__ = ["GeneralLoader", "PDFLoader", "URLLoader", "ExcelLoader", "ImageLoader"]
