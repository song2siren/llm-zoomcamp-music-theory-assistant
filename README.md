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
pipenv install openai scikit-learn pandas minsearch streamlit flask "qdrant-client[fastembed]>=1.14.2"
```
9. Now install Jupyter Notebook

```bash
pipenv install --dev tqdm notebook==7.1.2 ipywidgets
```


## Acknowledgements

Many thanks to [DataTalksClub](https://github.com/DataTalksClub) for the `llm-zoomcamp` resources and to Alexey Grigorev and others for providing clear and comprehensive project instructions.