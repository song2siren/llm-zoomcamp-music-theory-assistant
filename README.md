# LLM Zoomcamp - Music Theory Assistant
This is a RAG application project for the DataTalksClub [LLM Zoomcamp 2025](https://github.com/DataTalksClub/llm-zoomcamp).

<p align="center">
  <img src="images/banner.png">
</p>

## Problem Description

Understanding music theory can be overwhelming, especially when analysing harmonic functions and cadences across different songs. Traditional resources are often scattered and difficult to search effectively.

The Music Theory Assistant provides a conversational AI that helps users explore songs through a theoretical lens—answering questions about cadences, chord functions, and harmonic context in a natural and intuitive way.

This is based upon a musically accurate dataset that can answer music theory questions like:

"Which songs use deceptive cadences?"

"Which have authentic cadences?"

"What is the function of G in Let It Be?"

## Project Overview
The Music Theory Assistant is a RAG application designed to help users analyse and understand songs through the lens of music theory.

The main use cases include:

**Cadence Identification**: Discovering songs that use specific cadences such as deceptive or authentic cadences.

**Chord Function Analysis**: Understanding the harmonic function of specific chords within a song’s context.

**Song-Based Querying**: Asking theory-related questions about well-known songs in a conversational way.

**Conversational Interaction**: Making music theory more approachable without digging through textbooks, disparate online resources or dense analyses.

## Dataset

The dataset used in this project contains detailed music theory annotations for various well-known songs, including:

- **Title:** The name of the song (e.g., *Let It Be*, *Smells Like Teen Spirit*).  
- **Artist:** The performing artist or band (e.g., The Beatles, Nirvana).  
- **Genre:** The musical style or category (e.g., Pop, Rock, Jazz).  
- **Key:** The key signature of the song (e.g., C major, A minor).  
- **Tempo (BPM):** The tempo in beats per minute (e.g., 76, 120).  
- **Time Signature:** The time signature used in the song (e.g., 4/4, 3/4).  
- **Chord Progression:** The main chord sequence in Roman and/or letter notation (e.g., C – G – Am – F).  
- **Roman Numerals:** The chord progression translated into Roman numeral analysis (e.g., I – V – vi – IV).  
- **Cadence:** Identified cadences within the song (e.g., Authentic, Deceptive, Plagal).  
- **Theory Notes:** Additional commentary on harmonic features, chord functions, or interesting theoretical elements.

The dataset currently contains 100 curated, musically accurate and unique records. It serves as the foundation for the Music Theory Assistant's ability to answer questions about harmonic analysis, cadences, and chord functions.

You can find the data in [`data/music-theory-dataset-100.csv`](data/music-theory-dataset-100.csv).

## Technologies

- Python 3.12
- Docker and Docker Compose for containerization
- [Minsearch](https://github.com/alexeygrigorev/minsearch) for full-text search
- [Qdrant](https://qdrant.tech/) for vector search
- Flask as the API interface (see [Background](#background) for more information on Flask)
- Grafana for monitoring and PostgreSQL as the backend for it
- OpenAI as an LLM

## Setup
The Python project has been developed in [GitHub Codespaces](https://github.com/features/codespaces). As such, it is preferable to use Codespaces to run this application.

The project uses OpenAI, so you need to provide the API key:

1. OpenAI keys can be generated here: [OpenAI Platform](https://platform.openai.com/api-keys). The key is then stored as an evironment variable associated with this project.
2. For OpenAI, it is recommended that you create a new project and use a separate key.
3. Install `direnv`. This is a shell extension that automatically manages environment variables necessary to run the project.

```bash
sudo apt update
sudo apt install direnv
echo 'eval "$(direnv hook bash)"' >> ~/.bashrc
source ~/.bashrc
```
4. Run `direnv allow` to load the key into your environment.
5. Copy `.envrc_template` into `.envrc` and insert your OpenAI key there.
6. For dependency management, I use pipenv, so you need to install it:

```bash
pip install pipenv
```
7. Once installed, you can install the virtual environment and app dependencies:

```bash
pipenv install --dev
```
8. Now install remaining dependencies:

```bash
pipenv install openai scikit-learn pandas minsearch qdrant-client[fastembed]>=1.14.2 streamlit httpie
```
9. Now install Jupyter Notebook

```bash
pipenv install --dev tqdm notebook==7.1.2 ipywidgets
```

## Evaluation

The code for evaluating the system can be found in the [notebooks/rag-test.ipynb](notebooks/rag-test.ipynb) notebook.

This code requires Qdrant and FastEmbed to be installed and running. If it is not available, do the following:

Install Qdrant and FastEmbed (if not already installed during project setup):

```bash
pip install -q "qdrant-client[fastembed]>=1.14.2"
```

Run in Docker:

```bash
docker pull qdrant/qdrant

docker run -p 6333:6333 -p 6334:6334 \
   -v "$(pwd)/qdrant_storage:/qdrant/storage:z" \
   qdrant/qdrant
```

The score criteria (with additional commentary) can be found in the [docs/project-evaluation.ipynb](notebooks/docs/project-evaluation.ipynb) notebook.

### Retrieval Flow

The knowledgebase is based upon a [ChatGPT](https://chatgpt.com/) generated [data/music-theory-dataset-100.csv](data/music-theory-dataset-100.csv) CSV file. This is used together with the [ChatGPT 4o LLM](https://chatgpt.com/?model=gpt-4o).

### Retrieval Evaluation

Multiple retrieval approaches are evaluated.

The first approach uses [minsearch](https://github.com/alexeygrigorev/minsearch/blob/main/minsearch.py) without any boosting and returns the following results:

* hit_rate: 91%
* MRR: 63%

After the boosting is improved, the following results are returned:

* hit_rate: 93%
* MRR: 91%

The best boosting parameters:
```python
boost = {
    'title': 2.37,
    'artist': 0.30,
    'genre': 0.61,
    'key': 2.46,
    'tempo_bpm': 1.42,
    'time_signature': 2.21,
    'chord_progression': 0.32,
    'roman_numerals': 0.60,
    'cadence': 0.39,
    'theory_notes': 0.16
}
```
The second approach uses [Qdrant](https://qdrant.tech/) and returns the following results:

* hit_rate: 91%
* MRR: 87%

### LLM Evaluation

Two approaches are taken to evaluate the quality of the RAG flow:

* Cosine similarity (with [gpt-4o-mini](https://chatgpt.com/?model=gpt-4o-mini))
* LLM-as-a-Judge (with [gpt-4o-mini](https://chatgpt.com/?model=gpt-4o-mini) and [gpt-4o](https://chatgpt.com/?model=gpt-4o))

For cosine similarity with a single test record, the following result was returned:

* Cosine similarity: 0.45508164

For cosine similarity when comparing the [gpt-4o-mini](https://chatgpt.com/?model=gpt-4o-mini) answer for each question in the [ground truth data set](data/ground-truth-retrieval.csv) with the answer in the original [music theory dataset](data/music-theory-dataset-100.csv), the following results were returned:

| Metric   | Value   | Meaning                                 |
| -------- | ------- | --------------------------------------- |
| count    | 500     | Number of comparisons made.             |
| mean     | 0.57    | Avg cosine similarity across all pairs. |
| std      | 0.12    | Standard deviation.                     |
| min      | 0.22    | Lowest similarity.                      |
| 25%      | 0.50    | First quartile (poor matches).          |
| 50%      | 0.58    | Median.                                 |
| 75%      | 0.66    | Third quartile (good matches).          |
| max      | 0.84    | Best similarity.                        |

Just a single model was used for cosine similarity, but for LLM-as-a-Judge multiple models were evaluated.

For the LLM-as-a-Judge (with [gpt-4o-mini](https://chatgpt.com/?model=gpt-4o-mini)), among 200 records, the following results were returned:

* RELEVANT - 195 (97.5%)
* PARTLY_RELEVANT - 4 (2%)
* NON_RELEVANT - 1 (0.5%)

For the LLM-as-a-Judge (with [gpt-4o](https://chatgpt.com/?model=gpt-4o)), among 200 records, the following results were returned:

* RELEVANT - 192 (96%)
* PARTLY_RELEVANT - 6 (3%)
* NON_RELEVANT - 2 (1%)

### Interface

Before running either interface it is necessary to run the Python data ingestion script into Qdrant as noted in the [Ingestion Pipeline section](#ingestion-pipeline) below.

This project provides **two ways to interact with the Music Theory Assistant**:

- Streamlit UI 🎵

  A web-based interface where users can type in natural-language questions (e.g., "Which songs use deceptive cadences?") and receive answers enhanced with contextual information from the knowledge base.

  To start the app:

  ```bash
  streamlit run music-theory-assistant/app.py
  ```
  The UI is interactive, lightweight, and requires no coding from the user.

- FastAPI ⚡

  A REST API that exposes the same RAG functionality programmatically. This allows other applications or scripts to integrate with the assistant.

  To start the API server:

  ```bash
  # Option 1: Run from inside the application folder
  cd music-theory-assistant
  uvicorn api:app --reload --port 8000

  # Option 2: Run from project root
  uvicorn music-theory-assistant.api:app --reload --port 8000
  ```

  Example query from the terminal (using [httpie](https://httpie.io/)):

  ```bash
  http POST :8000/rag question="Which songs use deceptive cadences?"
  ```

  Or open the interactive docs at: http://127.0.0.1:8000/docs

### Ingestion Pipeline

The dataset (of musical theory–annotated songs) is loaded into a Qdrant vector database via a dedicated ingestion script. This ensures that the retrieval layer is always backed by fresh and structured embeddings.

The script reads from [data/music-theory-dataset-100.csv](data/music-theory-dataset-100.csv).

It generates embeddings for each record (title, artist, genre, chords, cadences, etc.) using jinaai/jina-embeddings-v2-small-en.

The embeddings and payloads are stored in a Qdrant collection (zoomcamp-music-theory-assistant).

Run the ingestion step once before starting the app:

```bash
python music-theory-assistant/ingest.py
```

After ingestion, Qdrant persists the collection, so the app and API can be restarted without re-ingesting.

### Containerization

[Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) have also been used for the application and API setup.

To get started:

**Prerequisites**

- Docker and Docker Compose installed
- An OpenAI API key

**Project layout (expected)**

```kotlin
project-root/
├── data/
│   └── music-theory-dataset-100.csv
├── docker-compose.yml
└── music-theory-assistant/
    ├── app.py
    ├── api.py
    ├── ingest.py
    ├── wait-for-qdrant.py
    ├── requirements.txt
    └── (other project files…)
```

**Environment**

Set your OpenAI key so the containers can access it. Easiest is to export it before running Compose:

```bash
export OPENAI_API_KEY=sk-...
```

(You can also put this in a .env file next to docker-compose.yml with OPENAI_API_KEY=....)

**One-command run**

From the **project root**, run:

```bash
docker compose up --build
```

What happens:

- **Qdrant** starts and persists data in a named volume.
- **ingest** waits until Qdrant is ready, then loads [data/music-theory-dataset-100.csv](data/music-theory-dataset-100.csv) into the zoomcamp-music-theory collection (and exits).
- **app** (Streamlit UI) starts on http://localhost:8501.
- **api** (FastAPI) starts on http://localhost:8000.

Visit:

- UI: http://localhost:8501
- API docs: http://localhost:8000/docs

**If your Docker Compose is older**

If <mark style="background-color: grey">service_completed_successfully</mark> isn’t supported, run in two steps:

```bash
docker compose up -d qdrant          # start Qdrant
docker compose run --rm ingest       # run ingestion one-off (exits on success)
docker compose up -d app api         # start UI + API
```

**Re-ingesting data**

If you change the CSV, re-run only the ingestion:

```bash
docker compose run --rm ingest
```

**Stopping everything**

```bash
docker compose down
```

## Acknowledgements

Many thanks to [DataTalksClub](https://github.com/DataTalksClub) for the `llm-zoomcamp` resources and to Alexey Grigorev and others for providing clear and comprehensive project instructions.