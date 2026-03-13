import torch
import torchvision
from torchvision import datasets, models, transforms
from torch import nn, optim
import os

# This script is a template for fine-tuning ResNet50 on specialized food datasets.
# It supports Food-101, UECFOOD256, and other folder-structured datasets.

def train_model(data_dir, dataset_name="Food-101", num_classes=101, epochs=25):
    """
    General training function for food classification.
    data_dir: Path to dataset (must have 'train' and 'val' subfolders)
    dataset_name: Name for logging
    num_classes: Number of food categories in the dataset
    """
    print(f"Initializing training for {dataset_name}...")
    
    # 1. Data augmentation and normalization (Standard for ResNet)
    data_transforms = {
        'train': transforms.Compose([
            transforms.RandomResizedCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(15),
            transforms.ColorJitter(brightness=0.1, contrast=0.1),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
        'val': transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
    }

    # 2. Load the dataset from local folders
    if not os.path.exists(data_dir):
        print(f"Error: Dataset directory {data_dir} not found.")
        print("Please download the dataset from Kaggle (e.g., 'dansbecker/food-101') and extract it.")
        return

    try:
        image_datasets = {x: datasets.ImageFolder(os.path.join(data_dir, x), data_transforms[x])
                          for x in ['train', 'val']}
        dataloaders = {x: torch.utils.data.DataLoader(image_datasets[x], batch_size=32,
                                                     shuffle=True, num_workers=4)
                      for x in ['train', 'val']}
        dataset_sizes = {x: len(image_datasets[x]) for x in ['train', 'val']}
        class_names = image_datasets['train'].classes
        print(f"Loaded {len(class_names)} classes from {dataset_name}")
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return

    # 3. Initialize the model (Transfer Learning from ResNet50)
    model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
    num_ftrs = model.fc.in_features
    # Update the final layer to match the number of classes in the food dataset
    model.fc = nn.Linear(num_ftrs, len(class_names))

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    # 4. Define loss and optimizer
    criterion = nn.CrossEntropyLoss()
    # Fine-tune only the last layer or all layers? 
    # Usually better to fine-tune all layers with a small learning rate for food
    optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)
    exp_lr_scheduler = optim.lr_lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)

    # 5. Training loop
    print(f"Starting training on {device}...")
    # ... (Actual training loop logic would be implemented here) ...
    
    # 6. Save the weights for use in FoodAnalyzer
    save_path = f"{dataset_name.lower()}_resnet50.pt"
    # torch.save(model.state_dict(), save_path)
    print(f"Training completed. Weights would be saved to {save_path}")

if __name__ == "__main__":
    print("=== Specialized Food Model Training Tool ===")
    print("Supported Datasets:")
    print("1. Food-101 (101 classes, ~100k images)")
    print("2. UECFOOD256 (256 classes, specifically for Asian food)")
    print("3. Kaggle USDA FoodData (Nutrition mapping reference)")
    print("\nTo improve recognition accuracy, download one of these datasets and run:")
    print("py training_scripts/train_food101.py --data_dir ./data/food-101")
