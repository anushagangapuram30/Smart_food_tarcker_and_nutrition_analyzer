import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet50, ResNet50_Weights
from ultralytics import YOLO
import os

class FoodAnalyzer:
    def __init__(self):
        # Load pre-trained YOLOv8 model for object detection
        self.ingredient_model = YOLO('yolov8n.pt') 
        
        # Load pre-trained ResNet50 for more general classification
        weights = ResNet50_Weights.DEFAULT
        self.classification_model = resnet50(weights=weights)
        self.classification_model.eval()
        
        # Get ImageNet categories
        self.categories = weights.meta["categories"]
        
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def preprocess_image(self, image_path):
        """Read and basic preprocess for OpenCV."""
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image at {image_path}")
        return image

    def detect_ingredients(self, image_path):
        """Use YOLOv8 to detect objects in the image."""
        results = self.ingredient_model(image_path)
        detected = []
        
        # YOLOv8 returns a list of Results objects
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get class name and confidence
                cls_id = int(box.cls[0])
                name = result.names[cls_id]
                conf = float(box.conf[0])
                
                # Only add if confidence is decent
                if conf > 0.3:
                    detected.append({"name": name, "confidence": conf})
        
        # If nothing detected by YOLO, return empty list
        return detected

    def classify_food(self, image_path):
        """Use ResNet50 and YOLOv8 to classify the overall food item."""
        # 1. Check YOLOv8 detections (specifically for food objects)
        yolo_detected = self.detect_ingredients(image_path)
        if yolo_detected:
            yolo_detected.sort(key=lambda x: x["confidence"], reverse=True)
            top_yolo = yolo_detected[0]
            # YOLO COCO food classes are highly reliable
            coco_food = ['apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake']
            if top_yolo["name"] in coco_food and top_yolo["confidence"] > 0.5:
                return top_yolo["name"].capitalize()

        # 2. Use ResNet50 with broad food category matching (simulating Food-101/UECFOOD256)
        image = cv2.imread(image_path)
        if image is None: return "Unknown Food"
            
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        input_tensor = self.transform(image_rgb).unsqueeze(0)
        
        with torch.no_grad():
            output = self.classification_model(input_tensor)
            
        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        top5_prob, top5_catid = torch.topk(probabilities, 5)
        
        # Extended food keywords covering Food-101 and UECFOOD256 categories
        food_keywords = [
            'pizza', 'burger', 'sandwich', 'hotdog', 'taco', 'burrito', 'salad', 'soup', 'bread', 'cake', 
            'fruit', 'vegetable', 'meat', 'fish', 'pasta', 'rice', 'egg', 'cheese', 'dessert', 'snack', 
            'chocolate', 'cookie', 'pie', 'stew', 'curry', 'noodle', 'wrap', 'sushi', 'steak', 'chicken',
            'pork', 'beef', 'shrimp', 'omelette', 'pancake', 'waffle', 'ice cream', 'donut', 'muffin',
            'bagel', 'croissant', 'toast', 'cereal', 'yogurt', 'smoothie', 'juice', 'coffee', 'tea'
        ]
        
        for i in range(5):
            category_name = self.categories[top5_catid[i]].lower()
            if any(keyword in category_name for keyword in food_keywords):
                # Clean up the name (e.g., 'cheeseburger, burger' -> 'Cheeseburger')
                return category_name.split(',')[0].strip().capitalize()
        
        # Fallback to YOLO if any detection exists, else top ResNet prediction
        if yolo_detected:
            return yolo_detected[0]["name"].capitalize()
        return self.categories[top5_catid[0]].split(',')[0].strip().capitalize()

    def detect_cooking_method(self, image_path):
        """Heuristic-based cooking method detection for demo purposes."""
        # This is very hard to do without a specific model.
        # We'll use a simple heuristic based on image brightness/color for demo.
        image = cv2.imread(image_path)
        if image is None:
            return "Unknown"
            
        avg_color = np.mean(image, axis=(0, 1))
        # Simple heuristic: if it's very dark/brown, maybe it's grilled/baked
        if avg_color[2] > 150: # More red/yellow
            return "Grilled"
        elif avg_color[0] > 150: # More blue/white
            return "Steamed/Boiled"
        else:
            return "Baked"
