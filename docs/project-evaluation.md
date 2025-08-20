# Project Evaluation

Reference: The [evaluation criteria](https://github.com/DataTalksClub/llm-zoomcamp/blob/main/project.md#evaluation-criteria) of the [LLM-zoomcamp course](https://github.com/DataTalksClub/llm-zoomcamp) (as of 20/08/2025).

- ✅ Problem description
  - [ ] 0 points: The problem is not described
  - [ ] 1 point: The problem is described but briefly or unclearly
  - [x] 2 points: The problem is well-described and it's clear what problem the project solves

- ✅ Retrieval flow
  - [ ] 0 points: No knowledge base or LLM is used
  - [ ] 1 point: No knowledge base is used, and the LLM is queried directly
  - [x] 2 points: Both a knowledge base and an LLM are used in the flow

- ✅ Retrieval evaluation:
  - [ ] 0 points: No evaluation of retrieval is provided
  - [ ] 1 point: Only one retrieval approach is evaluated
  - [x] 2 points: Multiple retrieval approaches are evaluated, and the best one is used

- ✅ LLM evaluation:
  - [ ] 0 points: No evaluation of final LLM is provided
  - [ ] 1 point: Only one approach (e.g., one prompt) is evaluated
  - [x] 2 points: Multiple approaches are evaluated, and the best one is used

- ✅ Interface
  - [ ] 0 points: No way to interact with the application at all
  - [ ] 1 point: Command line interface, a script, or a Jupyter notebook
  - [x] 2 points: UI (e.g., Streamlit), ~~web application (e.g., Django)~~, or an API (e.g., built with FastAPI)

- ✅ Ingestion pipeline
  - [ ] 0 points: No ingestion
  - [ ] 1 point: Semi-automated ingestion of the dataset into the knowledge base, e.g., with a Jupyter notebook
  - [x] 2 points: Automated ingestion with a **Python script** ~~or a special tool (e.g., Mage, dlt, Airflow, Prefect)~~

- ✅ Monitoring:
  - [ ] 0 points: No monitoring
  - [ ] 1 point: User feedback is collected OR there's a monitoring dashboard
  - [x] 2 points: User feedback is collected and there's a dashboard with at least 5 charts

- ✅ Containerization:
  - [ ] 0 points: No containerization
  - [ ] 1 point: Dockerfile is provided for the main application OR there's a docker-compose for the dependencies only
  - [x] 2 points: Everything is in docker-compose

- ✅ Reproducibility:
  - [ ] 0 points: No instructions on how to run the code, the data is missing, or it's unclear how to access it
  - [ ] 1 point: Some instructions are provided but are incomplete, OR instructions are clear and complete, the code works, but the data is missing
  - [x] 2 points: Instructions are clear, the dataset is accessible, it's easy to run the code, and it works. The versions for all dependencies are specified.

- ✅ Best practices:
  - [x] Hybrid search: combining both text and vector search (at least evaluating it) (1 point)
  - [x] Document re-ranking (1 point)
  - [ ] User query rewriting (1 point)

- ⬜ Bonus points (not covered in the course)
  - [ ]  Deployment to the cloud (2 points)
  