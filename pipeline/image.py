
from dotenv import load_dotenv
from datetime import datetime
from persona import IMAGE_PROMPT
from gradio_client import Client, handle_file
from PIL import Image
import os

IMAGE_PATH="assets/generated"
IMAGE_MODEL="black-forest-labs/flux-klein-9b-kv"
REFERENCE_PATH="assets/reference"

load_dotenv()

def get_prompt():
    # TODO: hardcoded for now, may need to vary per-post later
    prompt=IMAGE_PROMPT 
    print("prompt recevied: success")
    return prompt

def save_image(image) -> None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(IMAGE_PATH, exist_ok=True)
    save_path= os.path.join(IMAGE_PATH,timestamp + ".png")
    image.save(save_path)
    print(f"Image saved at {save_path}: success")

def handle_path(dir_path) -> list:
    path_list = os.listdir(dir_path)
    paths=[]
    for path in path_list:
        paths.append(os.path.join(dir_path,path))
    print("Handle path: success")
    return paths

def input_images():
    paths = handle_path(REFERENCE_PATH)
    print("Input images: success")
    return [{"image": handle_file(path), "caption": None} for path in paths[:1]]

def init_gradio_client():
    client = Client(IMAGE_MODEL, token=os.environ["HF_API_TOKEN"])
    print("Gradio client initialized: success")
    return client


def generate_conditioned_image(prompt):
    images = input_images()
    client = init_gradio_client()
    result = client.predict(api_name="/generate",
                   prompt=prompt,
                   input_images=images,
                   seed = 0,
                   randomize_seed=True,
                   width=1024,
                   height=1024,
                   num_inference_steps=4,
                   prompt_upsampling=False
                   )
    print("Conditioned image generated: success")
    return result

def image_pipeline():
    prompt=get_prompt()
    try:
        result = generate_conditioned_image(prompt)
        print(result)
        image = Image.open(result[0])
        save_image(image)
        print("Image pipeline complete: success")
    except Exception as e:
        print(f"Error: {e}")
        print("Image pipeline complete: failure")
    

if __name__ == "__main__":
    image_pipeline()