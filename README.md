# Text-to-Image Workflow Using LLM and Stable Diffusion

This project provides a complete text-to-image pipeline that utilizes two Python scripts:

1. **`text-model-call-async.py`**: A script for generating high-quality Stable Diffusion prompts using a text model (via the Ollama API).
2. **`image-model-call-async.py`**: A script for generating images from Stable Diffusion prompts using the AUTOMATIC1111 API.

The workflow allows you to:
- Enter a prompt or feedback for generating Stable Diffusion prompts.
- Queue multiple prompts for processing.
- Automatically generate images from queued prompts.

## Features
- **Asynchronous Processing**: Both scripts are fully asynchronous for efficient task management.
- **Queue System**: The image generation script processes multiple prompts stored in the queue.
- **Detailed Outputs**: Images and metadata are saved with timestamps for better organization.
- **Customizable Models**: Supports selecting different Stable Diffusion models based on the content of the prompt.

---

## Directory Structure
The scripts ensure the following directories are created and used:

```
project-root/
|
├── queue/          # Prompts to be processed are placed here
├── archive/        # Processed prompts are moved here
├── outputs/        # Generated images and metadata are saved here
|
├── text-model-call-async.py  # Script for generating prompts
├── image-model-call-async.py # Script for generating images
├── requirements.txt          # Dependencies for the project
```

---

## Installation

### Prerequisites
- **Python 3.10+**
- Install dependencies from the `requirements.txt` file:
  ```bash
  pip install -r requirements.txt
  ```
- A running **Ollama** API instance for text generation.
- A running **AUTOMATIC1111 Stable Diffusion WebUI API** at `http://localhost:7860`.

### Clone the Repository
```bash
git clone <repository-url>
cd <repository-folder>
```

---

## Configuration

### Text Model Script (`text-model-call-async.py`)
- The script uses the Ollama API to generate prompts.
- You can customize the system prompt or conversation history to suit your needs.

### Image Model Script (`image-model-call-async.py`)
- Update the `models` dictionary with your model paths:
  ```python
  models = {
      "Standard": "<MODEL_PATH>",
      "Anime": "<MODEL_PATH>",
      "Realism": "<MODEL_PATH>"
  }
  ```
- Ensure your Stable Diffusion WebUI is running at `http://localhost:7860`.

---

## Usage

### Step 1: Generate Text Prompts
Run the `text-model-call-async.py` script to generate prompts:
```bash
python text-model-call-async.py
```
1. Enter a prompt when prompted by the script.
2. Iterate on the generated prompt as needed.
3. When satisfied, confirm the final prompt (sets `Final: Yes`).
4. The finalized prompt is saved to the `queue/` folder.

### Step 2: Generate Images
Run the `image-model-call-async.py` script to process prompts in the queue and generate images:
```bash
python image-model-call-async.py
```
1. The script polls the `queue/` folder for prompts.
2. For each prompt, it generates an image using the specified Stable Diffusion model.
3. The generated image and metadata are saved in the `outputs/` folder.
4. Processed prompt files are moved to the `archive/` folder.

---

## Outputs
### Image Files
Generated images are saved in the `outputs/` folder with filenames like:
```
2025-01-19_10-15-26_generated_image.png
```

### Metadata Files
Metadata for each generated image is saved as a `.txt` file with the same timestamp. Example:
```
2025-01-19_10-15-26_generated_image.txt
```
Contents:
```
Prompt: young adult, short spiky orange hair, vibrant blue eyes...
ModelType: Anime
ModelName: <<MODEL_PATH>>
```

---

## Locally Running Containers

To set up the required APIs locally, follow these links:
- **Ollama**: [Setup Instructions](https://ollama.com/blog/ollama-is-now-available-as-an-official-docker-image)
- **AUTOMATIC1111 WebUI**: [Setup Instructions](https://github.com/AbdBarho/stable-diffusion-webui-docker/wiki/Setup)

---

## Example Workflow
1. **Run the Text Model Script**:
   ```bash
   python text-model-call-async.py
   ```
   Input: "A sunset over a calm ocean with dolphins jumping"
   Output: Generates a finalized prompt saved to `queue/`.

2. **Run the Image Model Script**:
   ```bash
   python image-model-call-async.py
   ```
   Output: An image and metadata saved in `outputs/`.

---

## Troubleshooting
- **Ollama API Issues**:
  - Ensure the API is running and accessible.
  - Check network configurations and ensure the `ollama` package is correctly installed.

- **Stable Diffusion API Issues**:
  - Ensure the WebUI API is running at `http://localhost:7860`.
  - Verify the model paths in the `models` dictionary.

---

## Future Enhancements
- Add support for more advanced Stable Diffusion options.
- Integrate additional LLMs for prompt generation.
- Expand functionality for asynchronous bot integrations.

---

## License
This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) License. See the `LICENSE` file for details.

## Acknowledgments
- **Ollama**: For providing the text generation API used to create Stable Diffusion prompts. Learn more at [Ollama](https://ollama.com/).
- **AUTOMATIC1111 Stable Diffusion WebUI**: For providing the API used to generate images. Learn more and contribute at [GitHub](https://github.com/AUTOMATIC1111/stable-diffusion-webui).

## Stability AI Licensing
This project uses models provided under Stability AI’s licensing terms. See [Stability AI License](https://stability.ai) for details.
