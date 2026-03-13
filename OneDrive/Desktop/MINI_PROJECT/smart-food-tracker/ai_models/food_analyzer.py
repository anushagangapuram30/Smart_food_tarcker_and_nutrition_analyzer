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

    def detect_cooking_method(self, image_path, food_name=None):
        """
        Improved cooking method detection using food-type context and 
        advanced image features (texture/color distribution).
        """
        # 1. Use food-type context if available (most reliable for many dishes)
        if food_name:
            food_name_lower = food_name.lower()
            mapping = {
                'sushi': 'Raw',
                'sashimi': 'Raw',
                'pizza': 'Baked',
                'bread': 'Baked',
                'cake': 'Baked',
                'muffin': 'Baked',
                'sandwich': 'Fresh/Cold',
                'salad': 'Fresh/Cold',
                'apple': 'Raw',
                'orange': 'Raw',
                'banana': 'Raw',
                'soup': 'Boiled/Simmered',
                'stew': 'Slow Cooked',
                'curry': 'Simmered',
                'pasta': 'Boiled',
                'rice': 'Steamed/Boiled',
                'steak': 'Grilled/Pan-Seared',
                'burger': 'Grilled/Fried',
                'fries': 'Deep Fried',
                'donut': 'Fried',
                'omelette': 'Fried/Pan-Seared'
            }
            for key, method in mapping.items():
                if key in food_name_lower:
                    return method

        # 2. Advanced Heuristics based on Image Features
        image = cv2.imread(image_path)
        if image is None: return "Unknown"
        
        # Convert to HSV for better color analysis
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # Convert to Grayscale for texture/edge analysis
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # A. Check for Charring/Grill Marks (High contrast dark lines)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
        
        # B. Check for "Fried" colors (Golden/Deep Brown)
        # Golden-brown range in HSV
        lower_golden = np.array([10, 100, 100])
        upper_golden = np.array([25, 255, 200])
        mask_fried = cv2.inRange(hsv, lower_golden, upper_golden)
        fried_ratio = np.sum(mask_fried > 0) / (mask_fried.shape[0] * mask_fried.shape[1])
        
        # C. Check for "Steamed/Boiled" (Higher brightness, lower saturation)
        v_channel = hsv[:,:,2]
        s_channel = hsv[:,:,1]
        brightness = np.mean(v_channel)
        saturation = np.mean(s_channel)

        # Decision Logic
        if fried_ratio > 0.15:
            return "Fried/Golden"
        elif edge_density > 0.08 and brightness < 120:
            return "Grilled/Roasted"
        elif brightness > 180 and saturation < 80:
            return "Steamed/Boiled"
        elif saturation > 150 and brightness > 100:
            return "Fresh/Raw"
        else:
            return "Baked/Roasted"
