from ultralytics import YOLO
import torch
import gc
import time

if __name__ == '__main__':
    # Hyperparameters
    dataset_yaml = "data.yaml"
    epochs = 50
    img_size = 320
    batch_size = 16
    device = 0 # Uses your local RTX 4050 GPU
    
    print("--- STARTING MULTI-MODEL COMPARATIVE TRAINING ---")
    
    # YOLOv5 is removed because it already finished successfully!
    models_to_train = {
        "YOLOv10-Nano": "yolov10n.pt",
        "YOLO11-Nano": "yolo11n.pt"
    }
    
    for name, weights in models_to_train.items():
        print(f"\n\n>>> INITIALIZING TRAINING FOR: {name} <<<")
        
        # 1. Clear the GPU Memory and Python RAM
        torch.cuda.empty_cache()
        gc.collect()
        time.sleep(2) # Give the OS 2 seconds to release the memory
        
        # 2. Load the specific YOLO model
        model = YOLO(weights)
        
        # 3. Train the model (Note: workers=4 helps prevent Windows multiprocessing crashes)
        model.train(
            data=dataset_yaml,
            epochs=epochs,
            imgsz=img_size,
            batch=batch_size,
            device=device,
            workers=4, 
            project="Robot_Comparisons",
            name=f"{name}_Results"
        )
        
        # 4. Delete the model from memory before starting the next loop
        del model
    
    print("\n--- ALL COMPARATIVE TRAINING COMPLETE! ---")
    print("Check the 'Robot_Comparisons' folder for your new results.")