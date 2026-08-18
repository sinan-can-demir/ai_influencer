
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
from datetime import datetime
from persona import IMAGE_PROMPT
import os

load_dotenv()
IMAGE_PATH="assets/generated"
IMAGE_MODEL="stabilityai/stable-diffusion-3-medium-diffusers"

def init_hf_client() -> InferenceClient:
    client = InferenceClient(provider="hf-inference", api_key=os.environ["HF_API_TOKEN"])
    print("Huggingface client initialized")
    return client

def get_prompt():
    # TODO: hardcoded for now, may need to vary per-post later
    prompt=IMAGE_PROMPT 
    print("prompt recevied")
    return prompt

def generate_image(prompt):
    client = init_hf_client()
    image = client.text_to_image(prompt, model=IMAGE_MODEL)
    print("Image generated")
    return image

def save_image(image) -> None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(IMAGE_PATH, exist_ok=True)
    save_path= os.path.join(IMAGE_PATH,timestamp + ".png")
    image.save(save_path)
    print(f"Image saved at {save_path}")

def image_pipeline():
    prompt=get_prompt()
    image=generate_image(prompt)
    save_image(image)
    print("Image pipeline complete.")

if __name__ == "__main__":
    image_pipeline()