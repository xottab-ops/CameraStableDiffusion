# CameraStableDiffusion
Processing a user's photo using Stable Diffusion and sending the image to cloud storage

<!-- GETTING STARTED -->
## Getting Started


### Prerequisites

* python 3.12
  ```sh
  apt install python3.12
  ```

### Installation

1. Get a Static Key of Cloud Account
2. Create credentials file in `~/.aws/credentials`.

    Credentials template:
   ```
    [default]
      aws_access_key_id = <идентификатор_статического_ключа>
      aws_secret_access_key = <секретный_ключ>
      region=ru-central1
   ```
3. Clone the repo
   ```sh
   git clone https://github.com/xottab-ops/CameraStableDiffusion.git
   ```
4. Install Python virtual environment 
   ```sh
   pythom -m venv .venv
   source ./.venv/Scripts/activate
   ```
5. Install Python packages
   ```sh
   pip install -r requirements.txt
   ```
6. Enter your settings in `settings.imi`
   ```ini
   [DEFAULT]
   S3_ENDPOINT = <<S3 Endpoint link>>
   S3_BUCKET_NAME = <<Bucket name in S3>>
   STABLE_DIFFUSION_URL = <<API URL of Stable Diffusion>>
   ORIGINAL_PHOTO_DIR = <<Path to save original photos>>
   EDITED_PHOTO_DIR = <<Path to save edited photos>>
   ```
7. Run Python application
   ```sh
   python3.12 main.py
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>