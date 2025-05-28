"""Detection modülü"""
from .yolo_detector import YoloDetector
from .color_detector import ColorDetector
from .shape_detector import ShapeDetector

__all__ = ['YoloDetector', 'ColorDetector', 'ShapeDetector']