# OONI-ChainWatch -- Certificate Transparency Submitter

This Python script extracts certificate chains from OONI web connectivity measurements and submits them to a Let's Encrypt Certificate Transparency (CT) log. This aids in monitoring and auditing the certificates used on the web, contributing to internet transparency efforts.

## Features

*   **Efficiently processes OONI web connectivity measurement files** (`.jsonl.gz`) from a local directory.
*   **Extracts and parses X.509 certificate chains** using the `cryptography` library.
*   **Submits valid certificate chains** to a configurable CT log (Twig or Willow by default).
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
    ooni-env\Scripts\activate  # On Windows
    ```

3.  **Download Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Download OONI Data:**
    *   Download `web_connectivity` measurement files (`.jsonl.gz`) from the OONI S3 bucket (see instructions in the [OONI wiki]([url](https://ooni.org/post/mining-ooni-data))).
    *   Place the downloaded files in the `OONI-S3-Datasets/2024` directory within the project folder.

## Usage

1.  **Activate the virtual environment (if you created one):**
    ```bash
    source ooni-env/bin/activate  # On macOS/Linux
    ooni-env\Scripts\activate  # On Windows
    ```

2.  **Run the Script:**
    ```bash
    python main.py
    ```

The script will process the JSONL files, extract certificate chains, and attempt to submit them to the configured CT log.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

I will Open Source it after 17th May 2024.


