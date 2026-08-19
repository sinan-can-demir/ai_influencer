
from pipeline.draft import generate_draft
from pipeline.image import image_pipeline


def main():
    post_text = generate_draft()
    print(post_text)
    image_path = image_pipeline(post_text)
    if image_path:
        print("Driver completed: success")
    else:
        print("Driver completed: partial failure (image generation failed)")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error occured: Failure {e}")