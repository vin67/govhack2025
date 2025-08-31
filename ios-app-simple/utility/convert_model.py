#!/usr/bin/env python3
"""
Core ML Model Conversion Script for Digital Guardian
Converts Microsoft Phi-3-mini model to Core ML format for on-device iOS inference
"""

import coremltools as ct
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os
import json

def convert_phi3_to_coreml():
    """Convert Phi-3-mini model to Core ML format"""
    
    # Model configuration
    model_name = "microsoft/Phi-3-mini-4K-Instruct"
    output_path = "../DigitalGuardianSimple/DigitalGuardianLLM.mlpackage"
    
    print(f"🤖 Starting Digital Guardian LLM conversion...")
    print(f"📂 Model: {model_name}")
    print(f"📂 Output: {output_path}")
    print()
    
    try:
        # Step 1: Load model and tokenizer
        print("📥 Loading Phi-3-mini model and tokenizer...")
        
        # Use optimized settings for Mac
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,  # Use float32 for better Core ML compatibility
            trust_remote_code=True,
            device_map="cpu"  # Force CPU for conversion
        )
        
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True
        )
        
        print("✅ Model and tokenizer loaded successfully")
        
        # Step 2: Prepare example input for tracing
        print("🔧 Preparing model for conversion...")
        
        # Create example input for Digital Guardian queries
        example_prompt = "Context: You are Digital Guardian. Answer: What is the ATO phone number?"
        example_inputs = tokenizer(
            example_prompt,
            return_tensors="pt",
            max_length=512,
            truncation=True,
            padding=True
        )
        
        # Step 3: Convert to Core ML
        print("⚙️ Converting to Core ML format...")
        print("⚠️  This may take 10-15 minutes and use significant memory...")
        
        # Set model to evaluation mode
        model.eval()
        
        # Convert with optimized settings
        mlmodel = ct.convert(
            model,
            convert_to="mlprogram",
            inputs=[
                ct.TensorType(
                    name="input_ids",
                    shape=(1, ct.RangeDim(1, 512))  # Variable length up to 512 tokens
                    # dtype will be inferred automatically
                )
            ],
            # outputs will be inferred automatically
            compute_units=ct.ComputeUnit.ALL,  # Use CPU, GPU, and Neural Engine
            minimum_deployment_target=ct.target.iOS17  # iOS 17+ for best performance
        )
        
        print("✅ Model conversion completed")
        
        # Step 4: Add metadata
        print("📝 Adding model metadata...")
        
        mlmodel.short_description = "Digital Guardian LLM - On-device AI for government contact verification"
        mlmodel.input_description["input_ids"] = "Tokenized input text for government service queries"
        mlmodel.output_description["logits"] = "Model logits for text generation"
        
        # Add model info
        mlmodel.metadata = {
            "source_model": model_name,
            "created_by": "Digital Guardian - GovHack 2025",
            "purpose": "On-device government contact information assistant",
            "data_source": "383 verified Australian government contacts"
        }
        
        # Step 5: Save the model
        print(f"💾 Saving Core ML model to {output_path}...")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save the model
        mlmodel.save(output_path)
        
        # Step 6: Create tokenizer info for iOS
        print("📱 Creating tokenizer configuration for iOS...")
        
        tokenizer_config = {
            "vocab_size": tokenizer.vocab_size,
            "model_max_length": tokenizer.model_max_length,
            "pad_token": tokenizer.pad_token,
            "eos_token": tokenizer.eos_token,
            "bos_token": tokenizer.bos_token,
            "unk_token": tokenizer.unk_token
        }
        
        tokenizer_path = "../DigitalGuardianSimple/tokenizer_config.json"
        with open(tokenizer_path, 'w') as f:
            json.dump(tokenizer_config, f, indent=2)
        
        print("✅ Tokenizer configuration saved")
        
        # Success summary
        model_size_mb = sum(
            os.path.getsize(os.path.join(dirpath, filename))
            for dirpath, dirnames, filenames in os.walk(output_path)
            for filename in filenames
        ) / (1024 * 1024)
        
        print()
        print("🎉 Digital Guardian LLM conversion completed successfully!")
        print(f"📊 Model size: {model_size_mb:.1f} MB")
        print(f"📱 Ready for iOS integration")
        print(f"🛡️ On-device AI for government contact verification")
        print()
        print("Next steps:")
        print("1. Drag DigitalGuardianLLM.mlpackage into Xcode")
        print("2. Implement LLMService.swift")
        print("3. Test with government contact queries")
        
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        
        # Provide helpful error suggestions
        if "out of memory" in str(e).lower() or "oom" in str(e).lower():
            print()
            print("💡 Memory Error Solutions:")
            print("- Close other applications")
            print("- Try with smaller batch size")
            print("- Consider using a smaller model variant")
        elif "connection" in str(e).lower() or "download" in str(e).lower():
            print()
            print("💡 Download Error Solutions:")
            print("- Check internet connection")
            print("- Try again - HuggingFace servers may be busy")
            print("- Ensure sufficient disk space")
        else:
            print()
            print("💡 General Solutions:")
            print("- Ensure all dependencies are installed correctly")
            print("- Try running: pip install --upgrade transformers coremltools")
            print("- Check available memory and disk space")

def main():
    """Main conversion process"""
    print("🤖 Digital Guardian LLM - Core ML Conversion")
    print("=" * 50)
    convert_phi3_to_coreml()

if __name__ == "__main__":
    main()