# OONI-ChainWatch -- Certificate Transparency Submitter

This Python script extracts certificate chains from OONI web connectivity measurements and submits them to a Let's Encrypt Certificate Transparency (CT) log. This aids in monitoring and auditing the certificates used on the web, contributing to internet transparency efforts.

## Features

*   **Efficiently processes OONI web connectivity measurement files** (`.jsonl.gz`) from a local directory.
*   **Extracts and parses X.509 certificate chains** using the `cryptography` library.
*   **Submits valid certificate chains** to the Twig CT log.
*   **Implements rate limiting** to avoid overloading the CT log server.
*   **Maintains persistence** by tracking processed chains to avoid redundant submissions.

## Installation and Setup

1.  **Clone or Fork the Repository:**
    *   **If you have write access to the repository:**
        ```bash
        git clone https://github.com/Ash-2k3/OONI-ChainWatch
        ```
    *   **If you don't have write access:**
        1.  Fork the repository on GitHub.
        2.  Clone your forked repository:
            ```bash
            git clone https://github.com/{{YOUR_USER_NAME}}/OONI-ChainWatch # Replace with your forked repository URL
            ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python3 -m venv ooni-env
    source ooni-env/bin/activate  # On macOS/Linux
    ooni-env\Scripts\activate.bat  # On Windows
    ```

3.  **Download Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **OONI Data:**
   *   **Local Datasets:** This repository includes a sample set of `web_connectivity` measurement files (`.jsonl.gz`) in the `OONI-S3-Datasets/2024` directory for testing purposes.
   *   **Additional Data (Optional):** If you want to process more data, you can download additional `web_connectivity` measurement files from the OONI S3 bucket. Follow the instructions in the [OONI Wiki](https://ooni.org/post/mining-ooni-data/) for downloading data from the S3 bucket. Place any additional downloaded files in the same `OONI-S3-Datasets/2024` directory.


## Usage

1.  **Activate the virtual environment (if you created one):**
    ```bash
    source ooni-env/bin/activate  # On macOS/Linux
    ooni-env\Scripts\activate.bat  # On Windows
    ```

2.  **Run the Script:**
    ```bash
    python main.py
    ```

The script will process the JSONL files, extract certificate chains, and attempt to submit them to the configured CT log.

![Sample-Script-Run-Screenshot](readme-assets/Sample-Script-Run.png)

## Alternative Approach: Fetching Data from S3 Bucket

If you prefer fetching measurement data directly from the OONI S3 bucket instead of using locally downloaded datasets, you can switch to the `fetch-from-S3-bucket` branch. This approach eliminates the need to download datasets manually and allows the script to fetch webconnectivity measurement files directly from the S3 bucket. However, please note that the current implementation statically mentions the `PREFIX` variable (`raw/20240101/00/CH/webconnectivity`). You may need to modify this variable to match your requirements.

## Contributing

I will Open Source it after 17th May 2024.

## More Ideas to Implement!!!

https://github.com/Ash-2k3/OONI-ChainWatch/issues

## Deployement Options.

There are several deployment options available, but for this project, I might utilize Docker. Docker provides a convenient environment for containerizing our script, and it also offers me an excellent opportunity to gain hands-on experience with Docker :)

1. Dockerization Process
Create Dockerfile: We will define the environment for our script in a Dockerfile. This file specifies the base image, dependencies, and commands needed to set up the environment.

2. Build and Push Image: 
After defining the Dockerfile, we will build the Docker image using the docker build command. Once built, we will push the image to a Docker registry, such as Docker Hub, to make it accessible to our deployment environment.

3. Execution Strategy
Pull Image on Server: On our deployment server (preferably a Linux machine), we will pull the Docker image from the Docker registry using the docker pull command.

4. Run Container: We will run the Docker image as a container on the server using the docker run command. We may specify a restart policy to ensure that the container restarts automatically in case of failure or system reboot.

5. Periodic Execution
Use Cron Jobs: To ensure periodic execution of our script, we will utilize cron jobs on the host server. We will set up a cron job that triggers the execution of our Docker container at specified intervals. This approach provides flexibility and allows us to easily manage the scheduling of our script.

6. Avoid Cron Inside Container: While it's possible to implement cron jobs within the Docker container itself, this approach may introduce complexity and dependencies within the container. To keep the container lightweight and focused on its primary task, we opt for using cron jobs on the host server.

By following this deployment strategy, we can effectively containerize our script using Docker, deploy it on our server, and ensure periodic execution with minimal overhead.
