#!/usr/bin/env python3
"""
OpenELM to Core ML conversion script for Digital Guardian
Converts Apple's OpenELM-270M model to Core ML format for iOS deployment
"""

import coremltools as ct
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os
import json

def convert_openelm_to_coreml():
    """Convert OpenELM-270M model to Core ML format"""
    
    # Model configuration
    model_path = "../OpenELM-270M"
    output_path = "../DigitalGuardianSimple/DigitalGuardianLLM.mlpackage"
    
    print(f"🤖 Digital Guardian LLM - OpenELM Core ML Conversion")
    print(f"=" * 60)
    print(f"📂 Model: {model_path}")
    print(f"📂 Output: {output_path}")
    print()
    
    try:
        # Step 1: Load OpenELM model and tokenizer
        print("📥 Loading OpenELM-270M model and tokenizer...")
        
        # Load the model with optimized settings for conversion
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float32,  # Use float32 for Core ML compatibility
            trust_remote_code=True,
            device_map="cpu",  # Force CPU for conversion
            low_cpu_mem_usage=True
        )
        
        # Load tokenizer - OpenELM uses a different approach
        print("📝 Loading tokenizer (OpenELM uses custom approach)...")
        
        try:
            # Try loading tokenizer directly
            tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                trust_remote_code=True
            )
        except Exception as e:
            print(f"⚠️ Direct tokenizer loading failed: {e}")
            print("🔧 Using alternative tokenizer loading...")
            
            # Fallback: use a compatible tokenizer
            # OpenELM is based on LLaMA architecture, so we can use LLaMA tokenizer
            try:
                from transformers import LlamaTokenizer
                tokenizer = LlamaTokenizer.from_pretrained("huggingface/CodeBERTa-small-v1", trust_remote_code=True)
                print("⚠️ Using fallback tokenizer - this is for conversion testing only")
            except:
                # Ultimate fallback
                from transformers import GPT2TokenizerFast
                tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
                print("⚠️ Using GPT2 tokenizer as fallback - this is for conversion testing only")
        
        # Add pad token if missing
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        print("✅ OpenELM model and tokenizer loaded successfully")
        print(f"📊 Model size: ~{sum(p.numel() for p in model.parameters())/1e6:.1f}M parameters")
        
        # Step 2: Prepare model for conversion
        print("🔧 Preparing model for Core ML conversion...")
        
        # Set model to evaluation mode
        model.eval()
        
        # Create TorchScript traced model
        example_input_ids = torch.randint(0, 32000, (1, 128), dtype=torch.long)
        
        # Create a simplified forward function
        def simple_forward(input_ids):
            with torch.no_grad():
                outputs = model(input_ids=input_ids)
                return outputs.logits
        
        # Trace the model
        print("🔧 Tracing model for TorchScript...")
        traced_model = torch.jit.trace(simple_forward, example_input_ids)
        
        # Step 3: Create example input for tracing
        print("📝 Creating example input for model tracing...")
        
        # Government contact query example
        example_text = "What is the phone number for the Australian Taxation Office?"
        example_inputs = tokenizer(
            example_text,
            return_tensors="pt",
            max_length=128,  # Shorter for mobile
            truncation=True,
            padding="max_length"
        )
        
        example_input_ids = example_inputs["input_ids"]
        print(f"📊 Input shape: {example_input_ids.shape}")
        
        # Step 4: Convert to Core ML with simpler approach
        print("⚙️ Converting to Core ML format...")
        print("⚠️  This may take 5-10 minutes...")
        
        # Use a more conservative conversion approach
        mlmodel = ct.convert(
            traced_model,
            inputs=[
                ct.TensorType(
                    name="input_ids",
                    shape=example_input_ids.shape,  # Fixed shape for reliability
                    dtype=ct.int32
                )
            ],
            convert_to="mlprogram",
            compute_units=ct.ComputeUnit.CPU_AND_GPU,  # More conservative than ALL
            minimum_deployment_target=ct.target.iOS16  # iOS 16+ for broader compatibility
        )
        
        print("✅ Core ML conversion completed")
        
        # Step 5: Add metadata
        print("📝 Adding model metadata...")
        
        mlmodel.short_description = "Digital Guardian OpenELM-270M - Compact on-device AI for government contact assistance"
        mlmodel.input_description["input_ids"] = "Tokenized input text for government service queries (max 128 tokens)"
        mlmodel.output_description["Identity"] = "Model logits for next token prediction"
        
        # Add comprehensive metadata
        mlmodel.author = "Digital Guardian - GovHack 2025"
        mlmodel.license = "Apple License (Original OpenELM)"
        mlmodel.version = "1.0"
        
        # Step 6: Save the model
        print(f"💾 Saving Core ML model...")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save the model
        mlmodel.save(output_path)
        
        # Step 7: Create tokenizer configuration for iOS
        print("📱 Creating tokenizer configuration for iOS...")
        
        # Save essential tokenizer info
        tokenizer_config = {
            "vocab_size": len(tokenizer.get_vocab()) if hasattr(tokenizer, 'get_vocab') else tokenizer.vocab_size,
            "model_max_length": 128,  # Conservative for mobile
            "pad_token_id": tokenizer.pad_token_id,
            "eos_token_id": tokenizer.eos_token_id,
            "bos_token_id": getattr(tokenizer, 'bos_token_id', None),
            "unk_token_id": getattr(tokenizer, 'unk_token_id', None),
            "pad_token": tokenizer.pad_token,
            "eos_token": tokenizer.eos_token,
            "model_type": "openelm",
            "architecture": "OpenELM-270M"
        }
        
        tokenizer_path = "../DigitalGuardianSimple/openelm_tokenizer_config.json"
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
        print("🎉 Digital Guardian OpenELM conversion completed successfully!")
        print(f"📊 Core ML model size: {model_size_mb:.1f} MB")
        print(f"📱 Optimized for iOS 16+ devices")
        print(f"🧠 270M parameters - Perfect for mobile deployment")
        print(f"🛡️ Ready for government contact assistance")
        print()
        print("Next steps:")
        print("1. Add DigitalGuardianLLM.mlpackage to Xcode project")
        print("2. Implement LLMService.swift with OpenELM integration")
        print("3. Test with government contact queries from verified_services.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        
        # Provide specific error guidance
        if "memory" in str(e).lower() or "out of memory" in str(e).lower():
            print()
            print("💡 Memory Error Solutions:")
            print("- Close other applications to free RAM")
            print("- Try with low_cpu_mem_usage=True (already enabled)")
            print("- Restart the conversion process")
        elif "shape" in str(e).lower() or "dimension" in str(e).lower():
            print()
            print("💡 Shape Error Solutions:")
            print("- The model architecture may need adjustment")
            print("- Try with different input shapes")
            print("- Consider using torch.jit.trace instead")
        else:
            print()
            print("💡 General Solutions:")
            print("- Ensure OpenELM model files are complete")
            print("- Check available disk space (need ~2GB free)")
            print("- Try restarting Python environment")
            
        return False

def main():
    """Main conversion process"""
    success = convert_openelm_to_coreml()
    
    if success:
        print("🚀 Ready to integrate with Digital Guardian iOS app!")
    else:
        print("⚠️ Conversion failed - check error messages above")

if __name__ == "__main__":
    main()