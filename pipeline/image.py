
from dotenv import load_dotenv
from datetime import datetime
from pipeline.draft import generate_image_prompt
from gradio_client import Client, handle_file
from PIL import Image
from pipeline.history import log_image
import os

IMAGE_PATH="assets/generated"
IMAGE_MODEL="black-forest-labs/flux-klein-9b-kv"
REFERENCE_PATH="assets/reference"
NUM_REFERENCE_IMAGES=1 # to determine how many images will be used

load_dotenv()

def get_prompt(post_text):
    prompt=generate_image_prompt(post_text)
    print("image prompt recevied: success")
    return prompt

def save_image(image, save_path) -> None:
    image.save(save_path)
    print(f"Image saved at {save_path}: success")

def build_save_path():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(IMAGE_PATH, exist_ok=True)
    save_path = os.path.join(IMAGE_PATH, timestamp + ".png")
    return save_path

def handle_path(dir_path) -> list:
    path_list = os.listdir(dir_path)
    paths=[]
    for path in path_list:
        paths.append(os.path.join(dir_path,path))
    print("Handle path: success")
    return paths

def input_images(paths):
    print("Input images: success")
    return [{"image": handle_file(path), "caption": None} for path in paths[:NUM_REFERENCE_IMAGES]]

def init_gradio_client():
    client = Client(IMAGE_MODEL, token=os.environ["HF_API_TOKEN"])
    print("Gradio client initialized: success")
    return client


def generate_conditioned_image(prompt, images):
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

def image_pipeline(post_text) -> str:
    try:
        prompt=get_prompt(post_text)
        paths = handle_path(REFERENCE_PATH)
        images = input_images(paths)
        result = generate_conditioned_image(prompt, images)
        print("Image created: success \n", result)
        image = Image.open(result[0])
        save_path = build_save_path()
        save_image(image, save_path)
        print("Image pipeline complete: success")
        log_image(prompt,paths[:NUM_REFERENCE_IMAGES],result[1], save_path)
        return save_path
    except Exception as e:
        print(f"Error: {e}")
        print("Image pipeline complete: failure")
    return None

if __name__ == "__main__":
    image_pipeline("test post text")