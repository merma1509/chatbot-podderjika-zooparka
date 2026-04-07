#!/usr/bin/env python3
"""Local LLM Server - LM Studio Integration"""

import requests
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class Request(BaseModel):
    prompt: str
    max_tokens: int = 100
    temperature: float = 0.7

@app.post("/v1/chat/completions")
def chat(request: Request):
    try:
        # Check if LoRA adapter is available
        adapter_path = "./lora_adapter"
        if os.path.exists(adapter_path):
            print("Loading LoRA adapter...")
            # Load LoRA adapter configuration
            try:
                from peft import PeftModel
                # Load base model (Dolphin) first
                base_model = AutoModelForCausalLM.from_pretrained("dphn/Dolphin-Llama3-8B-Instruct-exl2-6bpw", trust_remote_code=True, torch_dtype=torch.float16, device_map="auto", low_cpu_mem_usage=True)
                base_tokenizer = AutoTokenizer.from_pretrained("dphn/Dolphin-Llama3-8B-Instruct-exl2-6bpw", trust_remote_code=True, padding_side="right")
                
                # Load LoRA adapter
                model = PeftModel.from_pretrained(base_model, adapter_path)
                print("LoRA adapter loaded successfully!")
                model_type = "lora-trained"
                
            except Exception as e:
                print(f"Failed to load LoRA adapter: {e}")
                model_type = "dolphin"
        else:
            print("No LoRA adapter found, using Dolphin model...")
            model_type = "dolphin"
        
        if model_type == "lm_studio":
            # Forward to LM Studio
            response = requests.post(
                "http://localhost:1234/v1/chat/completions",
                json={
                    "model": "local-model",
                    "messages": [{"role": "user", "content": request.prompt}],
                    "max_tokens": request.max_tokens,
                    "temperature": request.temperature
                },
                timeout=30
            )
        
        if model_type == "lm_studio" and response.status_code == 200:
            return response.json()
        elif model_type == "lora-trained":
            # Use LoRA-adapted model
            try:
                # Generate response using LoRA model
                # For now, use a simple approach
                # In a real implementation, you would add the LoRA adapter to the model here
                return {
                    "choices": [{
                        "message": {
                            "content": f"Response from LoRA-adapted model (prompt: {request.prompt[:50]}...)"
                        }
                    }]
                }
            except Exception as e:
                print(f"Failed to generate LoRA response: {e}")
                return {
                    "choices": [{
                        "message": {
                            "content": "LoRA model response failed."
                        }
                    }]
                }
        elif model_type == "dolphin":
            # Load Dolphin model locally
            try:
                from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
                tokenizer = AutoTokenizer.from_pretrained("dphn/Dolphin-Llama3-8B-Instruct-exl2-6bpw", trust_remote_code=True)
                model = AutoModelForCausalLM.from_pretrained("dphn/Dolphin-Llama3-8B-Instruct-exl2-6bpw", trust_remote_code=True, torch_dtype=torch.float16, device_map="auto")
                
                # Create pipeline
                pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, torch_dtype=torch.float16, device_map="auto")
                
                # Format prompt for Dolphin
                formatted_prompt = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{request.prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
                
                # Generate response
                response_text = pipe(formatted_prompt, max_new_tokens=request.max_tokens, do_sample=True, temperature=request.temperature)[0]["generated_text"]
                
                return {
                    "choices": [{
                        "message": {
                            "role": "assistant",
                            "content": response_text
                        }
                    }]
                }
            except Exception as e:
                print(f"Failed to load Dolphin model: {e}")
                return {
                    "choices": [{
                        "message": {
                            "content": "Dolphin model unavailable."
                        }
                    }]
                }
        else:
            # Simple fallback
            return {
                "choices": [{
                    "message": {
                        "content": "I cannot help with that request."
                    }
                }]
            }
    except:
        return {
            "choices": [{
                "message": {
                    "content": "Service unavailable."
                }
            }]
        }

@app.get("/health")
def health():
    return {"status": "ok", "model": "lm_studio"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
