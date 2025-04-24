"""Transformation operations for geometric parts."""

from typing import Tuple
from ...part.base import Part

def transform_part(part: Part, transform_type: str, *args, **kwargs) -> Part:
    """Apply a transformation to a part.
    
    Args:
        part: The Part instance to transform.
        transform_type: Type of transformation ('translate' or 'rotate').
        *args, **kwargs: Arguments passed to the specific transformation method.
    
    Returns:
        A new transformed Part instance.
    
    Raises:
        ValueError: If transform_type is invalid or arguments are incorrect.
    """
    if transform_type == 'translate':
        if len(args) != 3:
            raise ValueError("Translation requires x, y, z coordinates")
        return part.translate(*args)
    elif transform_type == 'rotate':
        if len(args) != 2:
            raise ValueError("Rotation requires angle and axis tuple")
        angle, axis = args
        if not isinstance(axis, tuple) or len(axis) != 3:
            raise ValueError("Rotation axis must be a tuple of (x, y, z)")
        return part.rotate(angle, axis)
    else:
        raise ValueError(f"Unknown transformation type: {transform_type}")

def translate_part(part: Part, x: float, y: float, z: float) -> Part:
    """Translate a part by the given coordinates.
    
    Args:
        part: The Part instance to translate.
        x: Translation along X axis.
        y: Translation along Y axis.
        z: Translation along Z axis.
    
    Returns:
        A new translated Part instance.
    """
    return transform_part(part, 'translate', x, y, z)

def rotate_part(part: Part, angle: float, axis: Tuple[float, float, float]) -> Part:
    """Rotate a part by the given angle around the specified axis.
    
    Args:
        part: The Part instance to rotate.
        angle: Rotation angle in degrees.
        axis: Rotation axis as (x, y, z) tuple.
    
    Returns:
        A new rotated Part instance.
    """
    return transform_part(part, 'rotate', angle, axis)
