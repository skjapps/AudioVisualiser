from PIL import Image
import os

# Function to process GIF files
def process_gif_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".gif"):
            gif_path = os.path.join(directory, filename)
            with Image.open(gif_path) as img:
                # Extract the first frame
                first_frame = img.convert("RGBA")
                
                # Calculate the new height to maintain aspect ratio
                original_width, original_height = first_frame.size
                new_width = 3840
                new_height = int((new_width / original_width) * original_height)
                
                # Resize with pixel perfect scaling (no smoothing)
                resized_frame = first_frame.resize((new_width, new_height), resample=Image.NEAREST)
                
                # Save the first frame as PNG
                png_path = os.path.join(directory, f"{os.path.splitext(filename)[0]}_first_frame.png")
                resized_frame.save(png_path)

# Specify the directory containing GIF files
directory = "backgrounds"

# Process the GIF files in the specified directory
process_gif_files(directory)

print("Processing complete. First frames saved as PNGs.")
