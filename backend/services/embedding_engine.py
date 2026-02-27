from sentence_transformers import SentenceTransformer
from PIL import Image
import numpy as np
from typing import List, Optional
import cv2
from mtcnn import MTCNN

class EmbeddingEngine:
    def __init__(self):
        self.scene_model = SentenceTransformer('sentence-transformers/clip-ViT-B-32')
        self.face_detector = MTCNN()

    def generate_scene_embedding(self, image_path: str) -> List[float]:
        try:
            image = Image.open(image_path).convert('RGB')

            embedding = self.scene_model.encode(image, convert_to_numpy=True)

            return embedding.tolist()

        except Exception as e:
            print(f"Error generating scene embedding: {e}")
            return [0.0] * 512

    def generate_character_embeddings(self, image_path: str) -> List[List[float]]:
        try:
            image = cv2.imread(image_path)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            faces = self.face_detector.detect_faces(image_rgb)

            if not faces:
                return []

            character_embeddings = []

            for face in faces:
                x, y, w, h = face['box']

                x = max(0, x)
                y = max(0, y)

                face_crop = image_rgb[y:y+h, x:x+w]

                if face_crop.size == 0:
                    continue

                face_pil = Image.fromarray(face_crop)
                face_embedding = self.scene_model.encode(face_pil, convert_to_numpy=True)

                character_embeddings.append(face_embedding.tolist())

            return character_embeddings

        except Exception as e:
            print(f"Error generating character embeddings: {e}")
            return []
