#!/usr/bin/env python3
"""
Prepare a photo for ASCII conversion:
1. Remove background with rembg
2. Boost local contrast with CLAHE
3. Composite onto pure white
"""
import sys
import io
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove

DEFAULT_INPUT = "professional-photo.png"


def prep_photo(input_path: str, output_path: str = "data/source-prepped.png"):
    """Process a photo for clean ASCII conversion."""
    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading {input_path}...")
    with open(input_path, "rb") as f:
        input_bytes = f.read()

    print("Removing background...")
    output_bytes = remove(input_bytes)

    # Load as PIL Image with alpha channel
    img = Image.open(io.BytesIO(output_bytes)).convert("RGBA")

    # Create white background
    white_bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    # Composite: white_bg + img (img has alpha)
    composite = Image.alpha_composite(white_bg, img)

    # Convert to OpenCV format for CLAHE
    cv_img = cv2.cvtColor(np.array(composite), cv2.COLOR_RGBA2BGR)

    print("Applying CLAHE contrast enhancement...")
    # Convert to LAB color space
    lab = cv2.cvtColor(cv_img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    # Apply CLAHE to L channel
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)

    # Merge and convert back
    lab = cv2.merge((l, a, b))
    enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    # Save
    cv2.imwrite(str(output_path), enhanced)
    print(f"Saved prepped image to {output_path}")


if __name__ == "__main__":
    input_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INPUT
    output_path = sys.argv[2] if len(sys.argv) > 2 else "data/source-prepped.png"
    prep_photo(input_path, output_path)