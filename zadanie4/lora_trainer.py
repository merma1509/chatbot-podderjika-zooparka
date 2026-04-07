#!/usr/bin/env python3
"""LoRA Adapter Training Script for Task 4
Trains LoRA adapter on adversarial prompt dataset using Dolphin model"""

import os
import json
import torch
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
    from peft import LoraConfig, get_peft_model, TaskType
    from datasets import Dataset
    import numpy as np
except ImportError:
    print("Installing required dependencies...")
    os.system("pip install transformers peft datasets torch accelerate")
    from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
    from peft import LoraConfig, get_peft_model, TaskType
    from datasets import Dataset
    import numpy as np

class LoRATrainer:
    """LoRA Adapter Training Pipeline"""
    
    def __init__(self, model_name: str = "../.lmstudio/models/dolphinnlp/Llama-3-8B-Instruct-exl2-6bpw", 
                 dataset_path: str = "../zadanie3/data/lora_training_dataset.json",
                 output_dir: str = "./lora_adapter"):
        # Use local Dolphin model
        self.model_name = model_name
        print(f"Using local model: {model_name}")
        self.model_name = model_name
        self.dataset_path = dataset_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Training configuration
        self.training_config = {
            "model_name": model_name,
            "dataset_path": dataset_path,
            "output_dir": str(self.output_dir),
            "per_device_train_batch_size": 4,
            "gradient_accumulation_steps": 4,
            "warmup_steps": 100,
            "max_steps": 1000,
            "learning_rate": 2e-4,
            "fp16": True,
            "logging_steps": 10,
            "save_steps": 100,
            "evaluation_strategy": "steps",
            "load_best_model_at_end": True,
            "metric_for_best_model": "eval_loss",
            "greater_is_better": None,
            "report_to": "tensorboard",
            "lr_scheduler_type": "cosine",
            "weight_decay": 0.01,
            "num_train_epochs": 3,
            "train_batch_size": 4,
            "eval_batch_size": 8,
            "save_total_limit": 2,
            "save_strategy": "steps",
            "push_to_hub": False,
            "hub_strategy": "every",
            "hub_token": None,
            "gradient_checkpointing": True,
            "dataloader_pin_memory": False,
            "dataloader_num_workers": 4,
            "remove_unused_columns": None,
            "label_names": None,
            "task_type": "CAUSAL_LM",
            "optim": "adamw",
            "adam_beta1": 0.9,
            "adam_beta2": 0.999,
            "adam_epsilon": 1e-8,
            "max_grad_norm": 1.0,
        }
        
    def load_dataset(self) -> List[Dict]:
        """Load training dataset"""
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def prepare_dataset(self, dataset: List[Dict], tokenizer) -> Dataset:
        """Prepare dataset for training"""
        # Extract prompts and responses
        texts = []
        labels = []
        
        for item in dataset:
            # Format for instruction tuning
            text = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{item['prompt']}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n{item.get('response', 'I cannot help with that.')}"
            texts.append(text)
            labels.append(text)  # For instruction tuning, labels are the same as texts
        
        # Create dataset
        return Dataset.from_dict({"text": texts, "label": labels})
    
    def train_adapter(self):
        """Train LoRA adapter on Dolphin model"""
        print(f"Loading {self.model_name} for LoRA training...")
        
        # Load tokenizer and model
        if self.model_name == "local-model":
            # Use LM Studio proxy instead of loading local model
            print("Using LM Studio proxy for training...")
            tokenizer = None  # Will be handled by LM Studio
            model = None     # Will be handled by LM Studio
        else:
            # Load local model (Dolphin)
            tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                padding_side="right"
            )
            
            model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                torch_dtype=torch.float16,
                device_map="auto",
                low_cpu_mem_usage=True
            )
        
        # Prepare LoRA configuration
        lora_config = LoraConfig(
            r=16,  # attention dimension
            lora_alpha=32,
            target_modules=["q_proj", "v_proj"],
            lora_dropout=0.1,
            bias="none",
            task_type=TaskType.CAUSAL_LM,
        )
        
        # Apply LoRA to model
        model = get_peft_model(model, lora_config)
        
        # Prepare dataset
        dataset = self.prepare_dataset(self.load_dataset(), tokenizer)
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=str(self.output_dir),
            overwrite_output_dir=True,
            **self.training_config
        )
        
        # Create trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=dataset,
            tokenizer=tokenizer,
            data_collator=lambda data: tokenizer(data["text"], padding="max_length", truncation=True, return_tensors="pt"),
        )
        
        print("Starting LoRA training...")
        trainer.train()
        
        # Save final model
        trainer.save_model()
        print(f"LoRA adapter saved to {self.output_dir}")
        
        # Save training stats
        stats = {
            "training_date": datetime.now().isoformat(),
            "model_name": self.model_name,
            "dataset_size": len(dataset),
            "training_steps": trainer.state.global_step,
            "final_loss": trainer.state.log_history[-1]["train_loss"] if trainer.state.log_history else None,
            "lora_config": {
                "r": 16,
                "lora_alpha": 32,
                "target_modules": ["q_proj", "v_proj"]
            }
        }
        
        with open(self.output_dir / "training_stats.json", "w") as f:
            json.dump(stats, f, indent=2)
        
        print("Training completed successfully!")
    
    def run_training(self):
        """Main training pipeline"""
        print("=== LoRA Adapter Training ===")
        print(f"Model: {self.model_name}")
        print(f"Dataset: {self.dataset_path}")
        print(f"Output: {self.output_dir}")
        
        self.train_adapter()

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="LoRA Adapter Training for Task 4")
    parser.add_argument("--model", type=str, default="dphn/Dolphin-Llama3-8B-Instruct-exl2-6bpw", 
                       help="Model name for LoRA training")
    parser.add_argument("--dataset", type=str, default="../zadanie3/data/lora_training_dataset.json",
                       help="Path to training dataset")
    parser.add_argument("--output", type=str, default="./lora_adapter",
                       help="Output directory for LoRA adapter")
    
    args = parser.parse_args()
    
    trainer = LoRATrainer(args.model, args.dataset, args.output)
    trainer.run_training()

if __name__ == "__main__":
    main()
