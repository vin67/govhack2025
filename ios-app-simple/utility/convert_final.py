# convert_final.py
import coremltools as ct
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# --- CONFIGURATION ---
# Path to the model you already downloaded
local_model_path = "/Users/vinodralh/Code/claude/govhack2025/ios-app-simple/OpenELM-270M" 
# The name for the final output file
output_path = "/Users/vinodralh/Code/claude/govhack2025/ios-app-simple/DigitalGuardianSimple/DigitalGuardianLLM.mlpackage"

print("--- Starting OpenELM to Core ML Conversion ---")

# 1. Load Model and Tokenizer from local files
print(f"-> Loading model from: {local_model_path}")
model = AutoModelForCausalLM.from_pretrained(local_model_path, trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained(local_model_path, trust_remote_code=True)
model.eval() # Set model to evaluation mode
print("-> Model and Tokenizer loaded.")

# 2. Trace the model with a sample input
# This creates a simpler, more convertible version of the model
print("-> Tracing model with sample input...")
example_input_ids = torch.randint(0, 100, (1, 128)) # Batch size of 1, sequence length of 128
traced_model = torch.jit.trace(model, example_input_ids)
print("-> Model traced successfully.")

# 3. Convert the TRACED model to Core ML
print("-> Converting traced model to Core ML...")
mlmodel = ct.convert(
    traced_model,
    convert_to="mlprogram",
    inputs=[ct.TensorType(name="input_ids", shape=(1, ct.RangeDim(1, 2048)), dtype=ct.int32)],
    compute_units=ct.ComputeUnit.ALL
)
print("-> Initial conversion complete.")

# 4. (Optional but Recommended) Quantize the model to make it smaller and faster
print("-> Quantizing model to 4-bits...")
op_config = ct.optimize.coreml.OpPalettizerConfig(
    mode="kmeans", 
    nbits=4,
    weight_threshold=512
)
config = ct.optimize.coreml.OptimizationConfig(global_config=op_config)
mlmodel = ct.optimize.coreml.palettize(mlmodel, config)
print("-> Quantization complete.")

# 5. Save the final, optimized model
print(f"-> Saving final model to: {output_path}")
mlmodel.save(output_path)

print("\n--- SUCCESS! ---")
print(f"Model saved to {output_path}. You can now add this to Xcode.")