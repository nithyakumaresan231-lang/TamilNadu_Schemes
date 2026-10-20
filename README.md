# Tamil Nadu Government Schemes Assistant

A bilingual web application that helps citizens explore Tamil Nadu government welfare schemes, understand eligibility requirements, and discover schemes relevant to their personal circumstances.

The application combines **Retrieval-Augmented Generation (RAG)** for question answering with a **rule-based eligibility recommendation engine** for personalized scheme discovery.

## Features

### 1. Government Scheme Chatbot

* Ask questions about Tamil Nadu government schemes in English or Tamil.
* Retrieve relevant information using semantic search.
* Generate answers using retrieved scheme information as context.
* Ask follow-up questions about scheme benefits, eligibility, required documents, and application procedures.
* Provide source information when available.
* Avoid treating information absent from the available records as confirmed facts.

### 2. Personalized Scheme Recommendations

* Collect user profile information through a recommendation form.
* Evaluate the profile against the available scheme eligibility criteria.
* Organize results into three categories:

  * **Likely Matches** — recorded criteria appear to match the user's profile.
  * **Needs Verification** — more information or official verification is required.
  * **Does Not Match** — at least one evaluated mandatory criterion is not satisfied.
* Explain which criteria matched, failed, or require additional information.
* Display scheme verification status and available source information.

> Recommendation results are informational, not official eligibility decisions. Users should verify scheme requirements with the relevant government department before applying.

### 3. Scheme Discovery

* Explore government schemes from a structured JSON dataset.
* Search for schemes and filter them by department.
* Review scheme descriptions, benefits, eligibility requirements, and application information when available.

### 4. Bilingual Interaction and Voice Support

* Interact with the assistant in English or Tamil.
* Use browser-supported speech recognition for voice input where available.
* Use browser text-to-speech for spoken responses where supported.

## Technology Stack

| Component         | Technology                       |
| ----------------- | -------------------------------- |
| Frontend          | React, JavaScript, CSS           |
| Backend           | Python, FastAPI                  |
| Embedding model   | `intfloat/multilingual-e5-small` |
| Vector search     | FAISS                            |
| Language model    | Llama 3.2 1B through Ollama      |
| Scheme data       | JSON                             |
| API testing       | FastAPI TestClient, unittest     |
| Voice interaction | Browser Web Speech APIs          |

## System Architecture

### RAG Question-Answering Pipeline

```text
User Question
     |
     v
FastAPI Backend
     |
     v
Semantic Retrieval
     |
     v
Sentence Transformer Embeddings
     |
     v
FAISS Vector Index
     |
     v
Relevant Scheme Chunks
     |
     v
Prompt Construction
     |
     v
Llama 3.2 1B via Ollama
     |
     v
Generated Answer
     |
     v
Frontend Response
```

The retrieval component identifies relevant scheme information from the indexed data. The language model then uses the retrieved context to formulate an answer.

### Personalized Recommendation Pipeline

```text
User Profile
     |
     v
Recommendation API
     |
     v
Eligibility Evaluation
     |
     v
Compare Profile with Scheme Criteria
     |
     v
Evaluate Missing Information
and Verification Status
     |
     v
Categorize Recommendations
     |
     v
Explain Matching Results
     |
     v
Display Results in React
```

The recommendation engine evaluates recorded eligibility conditions and distinguishes matching criteria from failed or unknown conditions. Records that require additional verification are not automatically treated as officially confirmed eligibility.

## Project Structure

```text
tn-government-schemes-rag/
|
├── backend/
│   ├── main.py
│   ├── routes.py
│   ├── recommendation_routes.py
│   └── translation.py
|
├── frontend/
│   └── src/
│       ├── App.jsx
│       ├── RecommendationsPage.jsx
│       └── recommendations.css
|
├── rag/
│   ├── retriever.py
│   ├── generator.py
│   └── prompt.py
|
├── recommendations/
│   ├── __init__.py
│   ├── eligibility.py
│   ├── models.py
│   └── recommender.py
|
├── data/
│   ├── schemes.json
│   └── processed/
│       └── chunks.json
|
├── vectorstore/
│   ├── index.faiss
│   └── embeddings.npy
|
├── tests/
│   ├── __init__.py
│   ├── test_recommendations.py
│   ├── test_api_routes.py
│   └── test_regression.py
|
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

*This is a high-level overview of the main project files. Other supporting files may also exist in the repository.*

## Requirements

Install the following before running the application:

* Python 3.10
* Node.js and npm
* Git
* Ollama
* The required Python packages listed in `requirements.txt`

The frontend may have its own `package.json` and dependencies.

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/nithyakumaresan231-lang/TamilNadu_Schemes.git
cd TamilNadu_Schemes
```

### 2. Set Up the Python Environment

On Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If your environment already exists, activate it instead of creating another one.

### 3. Set Up Ollama

Install Ollama and download the model:

```bash
ollama pull llama3.2:1b
```

Start Ollama and verify that the model is available:

```bash
ollama list
```

The backend must be able to reach the local Ollama service.

### 4. Start the Backend

From the project root, activate the virtual environment and run:

```powershell
python -m uvicorn backend.main:app --reload
```

The backend will normally be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation is normally available at:

```text
http://127.0.0.1:8000/docs
```

### 5. Start the Frontend

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by the frontend development server.

> Follow the existing project configuration if your backend or frontend uses a different startup command or port.

## Running Tests

Activate the Python virtual environment and run the following commands from the project root.

### Recommendation Tests

```powershell
$env:PYTHONPATH="."
python -m unittest tests.test_recommendations
```

### API Route Tests

```powershell
$env:PYTHONPATH="."
python -m unittest tests.test_api_routes
```

### Regression Tests

```powershell
$env:PYTHONPATH="."
python -m unittest tests.test_regression
```

These tests cover recommendation logic, API behavior, and selected existing functionality.

**Latest recorded test run:** 26 tests passed across the three test modules.

Test results may change when the code or dependencies are modified. Run the tests again to verify the current version.

## Data and Verification

Scheme information is maintained in a structured JSON dataset.

The RAG pipeline uses processed chunks and a vector index for semantic retrieval. The recommendation engine evaluates user profile information against the eligibility criteria recorded in the scheme dataset.

The quality of both systems depends on the completeness and accuracy of the available records.

* Scheme eligibility rules may change.
* Some records may require further review.
* Missing information should not be interpreted as proof of eligibility.
* Official departmental sources should be consulted before making application decisions.

## Security and Configuration

* Do not commit `.env` files, passwords, API keys, or other secrets.
* Use `.env.example` to document required environment variables without exposing secret values.
* Keep generated files, virtual environments, and other local-only artifacts out of version control where appropriate.
* Review scheme data and official source links regularly.

## Future Improvements

Potential improvements include:

* Expanding official source verification for scheme records.
* Improving eligibility-rule coverage and handling of missing profile information.
* Adding more automated tests for recommendation edge cases.
* Improving retrieval quality and evaluating answer grounding.
* Expanding accessibility and multilingual interaction.
* Adding further tests for API integration and existing chatbot behavior.

## Disclaimer

This project is an informational tool for discovering government schemes. It is not an official government portal and does not guarantee eligibility, approval, or financial benefits.

Always consult the relevant government department and official scheme guidelines for current eligibility conditions, required documents, benefits, and application procedures.
