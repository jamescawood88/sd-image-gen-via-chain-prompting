import asyncio
import aiohttp
import os
import base64
from datetime import datetime

def print_with_timestamp(message):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    print(f"{timestamp} - {message}")

# Dynamically get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
queue_dir = os.path.join(script_dir, "queue")
archive_dir = os.path.join(script_dir, "archive")

# URL and model dictionary
url = "http://localhost:7860"
models = {
    "Standard": "<<INSERT MODEL PATH HERE>>",
    "Anime": "<<INSERT MODEL PATH HERE>>",
    "Realism":"<<INSERT MODEL PATH HERE>>"
}

# Generate image request asynchronously
async def generate_image(session, image_data):
    async with session.post(f"{url}/sdapi/v1/txt2img", json=image_data, timeout=aiohttp.ClientTimeout(total=600)) as response:
        if response.status == 200:
            print_with_timestamp("Image generation request sent successfully.")
            return await response.json()
        else:
            print_with_timestamp(f"Error generating image: {response.status}")
            print_with_timestamp(await response.text())
            return None

async def check_progress(session, interval, generation_task, retries=3):
    retry_count = 0
    while not generation_task.done():
        try:
            async with session.get(f"{url}/sdapi/v1/progress?skip_current_image=false") as response:
                if response.status == 200:
                    data = await response.json()
                    progress = data.get("progress", 0)
                    eta_remaining = data.get("eta_relative", 0)
                    print_with_timestamp(f"Progress: {progress*100:.2f}% \t ETA: {eta_remaining:.2f} seconds")
                    retry_count = 0  # Reset retry count on success
                else:
                    print_with_timestamp(f"Error checking progress: {response.status}")
        except aiohttp.ClientConnectionError as e:
            retry_count += 1
            print_with_timestamp(f"Connection error: {e}. Retrying ({retry_count}/{retries})...")
            if retry_count >= retries:
                print_with_timestamp("Max retries reached. Exiting progress check.")
                break
        except aiohttp.ClientError as e:
            print_with_timestamp(f"An error occurred: {e}. Retrying...")
        except asyncio.CancelledError:
            # Gracefully handle cancellation
            print_with_timestamp("Progress checking task was cancelled.")
            break
        await asyncio.sleep(interval)


# Main processing loop
async def process_prompt():
    while True:
        # Get a list of all prompt files in the queue directory
        prompt_files = [f for f in os.listdir(queue_dir) if f.endswith(".txt")]

        if prompt_files:
            for prompt_file in prompt_files:
                prompt_path = os.path.join(queue_dir, prompt_file)
                print_with_timestamp(f"Processing prompt file: {prompt_file}")

                # Read the prompt file
                with open(prompt_path, "r") as file:
                    sd_prompt = file.read()

                # Parse the prompt file
                model_type = "Standard"
                for line in sd_prompt.splitlines():
                    if line.startswith("Prompt:"):
                        sd_prompt = line.split("Prompt:")[1].strip()
                    elif line.startswith("ModelType:"):
                        model_type = line.split("ModelType:")[1].strip()

                selected_model = models.get(model_type, models["Standard"])
                print_with_timestamp(f"Using model: {selected_model}")

                # Prepare the image generation request
                image_data = { 
                "prompt": sd_prompt,
                "negative_prompt": "ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, extra limbs, disfigured, deformed, body out of frame, bad anatomy, watermark, signature, cut off, low contrast, underexposed, overexposed, bad art, beginner, amateur, distorted face",
                "styles": [
                    ""
                ],
                "seed": -1,
                "subseed": -1,
                "subseed_strength": 0,
                "seed_resize_from_h": -1,
                "seed_resize_from_w": -1,
                "sampler_name": "DPM++ 2M",
                "scheduler": "Karras",
                "batch_size": 1,
                "n_iter": 1,
                "steps": 20,
                "cfg_scale": 7,
                "width": 512,
                "height": 512,
                "restore_faces": True,
                "tiling": False,
                "do_not_save_samples": False,
                "do_not_save_grid": False,
                "eta": 0,
                "denoising_strength": 0.7,
                "s_min_uncond": 0,
                "s_churn": 0,
                "s_tmax": 0,
                "s_tmin": 0,
                "s_noise": 0,
                "override_settings": {"sd_model_checkpoint": selected_model},
                "override_settings_restore_afterwards": True,
                "refiner_switch_at": 0.8,
                "disable_extra_networks": False,
                "comments": {},
                "enable_hr": True,
                "firstphase_width": 0,
                "firstphase_height": 0,
                "hr_scale": 2,
                "hr_upscaler": "Latent",
                "hr_second_pass_steps": 0,
                "sampler_index": "Euler",
                "script_args": [],
                "send_images": True,
                "save_images": True,
                "alwayson_scripts": {}
                }
                        

                async with aiohttp.ClientSession() as session:
                    # Create the generation task
                    generation_task = asyncio.create_task(generate_image(session, image_data))

                    # Run progress checker concurrently while monitoring the generation task
                    await asyncio.gather(
                        check_progress(session, interval=5, generation_task=generation_task),
                        generation_task  # Ensure the generation task completes
                    )

                    # Retrieve the result of the generation task
                    image_result = await generation_task

                    if image_result:
                        # Save the generated image
                        base64_image = image_result["images"][0]
                        image_data = base64.b64decode(base64_image)

                        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                        output_filename = f"{timestamp}_generated_image.png"
                        details_filename = f"{timestamp}_generated_image.txt"

                        output_path = os.path.join(script_dir, "outputs", output_filename)
                        details_path = os.path.join(script_dir, "outputs", details_filename)

                        with open(output_path, "wb") as f:
                            f.write(image_data)
                        print_with_timestamp(f"Image saved as {output_filename}")

                        with open(details_path, "w") as f:
                            f.write(f"Prompt:{sd_prompt}\nModelType:{model_type}\nModelName:{selected_model}")
                        print_with_timestamp("Details file created.")

                # Move processed prompt file to the archive directory
                archive_path = os.path.join(archive_dir, prompt_file)
                os.rename(prompt_path, archive_path)
                print_with_timestamp(f"Moved processed prompt file to archive: {prompt_file}")

            else:
                print_with_timestamp("Error: Waiting for prompt files in queue")

        await asyncio.sleep(5)

# Entry point
async def main():
    await process_prompt()

if __name__ == "__main__":
    asyncio.run(main())
