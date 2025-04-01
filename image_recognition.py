import numpy as np
from io import BytesIO

from tensorflow.keras.applications.resnet50 import ResNet50
from tensorflow.keras.models import Model
from tensorflow.keras.layers import GlobalAveragePooling2D
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications.resnet50 import preprocess_input
import json

base_model = ResNet50(weights='imagenet', include_top=False)
x = base_model.output
x = GlobalAveragePooling2D()(x)
feature_model = Model(inputs=base_model.input, outputs=x)

def extract_feature_vector(file_data: bytes) -> np.ndarray:
    img = load_img(BytesIO(file_data), target_size=(224, 224))
    img_array = img_to_array(img)
    img_array = preprocess_input(np.expand_dims(img_array, axis=0))
    feature_vector = feature_model.predict(img_array)[0]
    return feature_vector

def cosine_similarity(a, b):
    dot_product = np.dot(a, b)
    norm1 = np.linalg.norm(a)
    norm2 = np.linalg.norm(b)
    return dot_product / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0
