from typing import List, Any, Union
from transformers import CLIPProcessor, CLIPModel
import torch
import numpy as np
from pathlib import Path
import base64
from io import BytesIO
from PIL import Image
import requests
from ..base import EmbeddingProvider


class CLIPImageEmbedder(EmbeddingProvider):
    """CLIP image embedding provider for image data."""
    
    def __init__(self, model_name: str = "default", **kwargs):
        if model_name == "default":
            model_name = "openai/clip-vit-base-patch32"
        super().__init__(model_name, **kwargs)
        self.model = CLIPModel.from_pretrained(model_name)
        self.processor = CLIPProcessor.from_pretrained(model_name)

    def _load_image(self, image_data: Union[str, dict, bytes, Image.Image]) -> Image.Image:
        """
        Load an image from various formats (path, URL, base64, bytes dict, or PIL Image).
        Args:
            image_data: Image as path, URL, base64 string, dict with 'bytes', raw bytes, or PIL Image
        Returns:
            PIL Image
        """
        # Already a PIL Image
        if isinstance(image_data, Image.Image):
            return image_data
        
        # Dictionary with 'bytes' key (as seen in visualization.py)
        if isinstance(image_data, dict) and 'bytes' in image_data:
            img_bytes = image_data['bytes']
            if isinstance(img_bytes, str):
                # If already base64 string, decode it
                img_bytes = base64.b64decode(img_bytes)
            return Image.open(BytesIO(img_bytes))
        
        # Raw bytes
        if isinstance(image_data, bytes):
            return Image.open(BytesIO(image_data))
        
        # String formats
        image_str = str(image_data)
        
        # Base64 encoded image with data URI
        if image_str.startswith('data:image'):
            # Extract base64 data after comma
            base64_data = image_str.split(',', 1)[1]
            img_bytes = base64.b64decode(base64_data)
            return Image.open(BytesIO(img_bytes))
        
        # URL
        elif image_str.startswith('http://') or image_str.startswith('https://'):
            response = requests.get(image_str, timeout=10)
            return Image.open(BytesIO(response.content))
        
        # File path
        else:
            img_path = Path(image_str)
            if img_path.exists() and img_path.is_file():
                return Image.open(img_path)
            else:
                raise ValueError(f"Image file not found: {image_str}")

    def embed(self, images: List[Any]) -> np.ndarray:
        """
        Embeds a batch of images using CLIP.
        Args:
            images: List of images (paths, URLs, base64 strings, or PIL Images)
        Returns:
            numpy array of embedding vectors (one per image)
        """
        # Load all images
        pil_images = [self._load_image(img) for img in images]
        
        # Process with CLIP
        inputs = self.processor(images=pil_images, return_tensors="pt", padding=True)
        with torch.no_grad():
            features = self.model.get_image_features(**inputs)
        return features.cpu().numpy()
    
    def embed_batch(self, images: List[Any], batch_size: int = 32) -> np.ndarray:
        """
        Embeds images in batches.
        Args:
            images: List of images (paths, URLs, base64 strings, or PIL Images)
            batch_size: Batch size for processing
        Returns:
            numpy array of embedding vectors
        """
        # For now, process all at once. Can add true batching later if needed.
        return self.embed(images)
