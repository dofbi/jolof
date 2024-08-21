# Wolof Dataset for Open LLM Fine-Tuning

This project provides a dataset for fine-tuning language models (LLMs) in Wolof. It uses a Python script to create a JSONLines (`.jsonl`) file from a list of words, retrieving detailed information from a Wolof-French dictionary API.

## How It Works

1. **Input File**: The script reads a list of words from a text file (`mots.txt`), with one word per line.
2. **API Requests**: For each word, the script calls an API to fetch JSON data containing definitions, examples, and etymology.
3. **Data Transformation**: The retrieved data is transformed into a structured format and saved in a JSONLines file (`dataset.jsonl`).

## Data Source

The data is sourced from the "Corpus Oraux du LLACAN," which provides comprehensive Wolof-French dictionary data. You can access the API for this dictionary at:

- **API Endpoint**: [https://corporan.huma-num.fr](https://corporan.huma-num.fr)

## Features

- **Automated Data Extraction**: Fetches data from the Wolof-French dictionary API.
- **Structured Output**: Converts data into JSONLines format for easy use in model training.
- **Rate Limiting**: Includes a delay between API calls to manage rate limits.

## Setup

1. **Install Dependencies**: Ensure you have Python 3.x and install the required library:

    ```bash
    pip install requests
    ```

2. **Prepare Input File**: Create a `mots.txt` file with one word per line.

3. **Run the Script**: Execute the Python script to generate the dataset:

    ```bash
    python script.py
    ```

## License

This project is licensed under the [MIT License](LICENSE).

## Author

- [Mamadou Diagne](https://dofbi.eth.limo)