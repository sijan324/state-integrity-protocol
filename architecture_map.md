# State Integrity Protocol (SIP): Architecture & Blueprint

## 1. High-Level Concept

The **State Integrity Protocol (SIP)** is designed to measure **State Decay** (fidelity loss) across multi-step AI agent pipelines. When an AI agent performs successive tasks in a chain, the goal often deviates from the initial intent. SIP monitors this using semantic text embeddings.

**Core Workflow:**
1. **Anchor**: You capture the embedding of the initial prompt/intent (e.g., "Analyze financials").
2. **Observe**: After every step the AI completes, you measure the output text against the Anchor.
3. **Drift Detection**: The system calculates the distance (Cosine Similarity) between the Anchor vector and the New Output vector. `Drift = 1 - Cosine Similarity`. If Drift exceeds a set `threshold`, the system flags it.

---

## 2. Directory and File Mapping

Here is the exact responsibility of every file in the `state-integrity-protocol` directory, structured exactly as they link to each other.

### A. The Core Engine (`sip/` directory)
This folder is the actual Python library that does the heavy lifting.

*   `sip/protocol.py` **(The Orchestrator)**:
    *   **What it does:** The main entry point. It defines the `StateIntegrityProtocol` class.
    *   **How it links:** It acts as a wrapper that instantiates `SemanticAnchor` and `FidelityObserver`.
    *   **Main Functions:** `anchor(prompt)` to start the process, and `observe(output)` to measure a new step. Handles alerting if the drift threshold is breached.
*   `sip/anchor.py` **(The Origin Point)**:
    *   **What it does:** Defines `SemanticAnchor`.
    *   **How it links:** Called by `protocol.py`. Uses `embeddings.py` to convert the initial prompt into a numerical vector (embedding). It just stores this initial vector as the "ground truth".
*   `sip/observer.py` **(The Measuring Tape & Logbook)**:
    *   **What it does:** Defines `FidelityObserver` and `TransitionRecord`.
    *   **How it works:** When `protocol.py` tells it to observe an output, it gets the output's embedding, pulls the origin vector from the `SemanticAnchor`, and calculates the Cosine Similarity. It saves this as a historical step (`TransitionRecord`).
*   `sip/embeddings.py` **(The Math / Vectorizer)**:
    *   **What it does:** Defines `TFIDFEmbedder`.
    *   **How it works:** Converts text into a mathematical vector (a list of floats). By default, it uses a custom Term Frequency-Inverse Document Frequency (TF-IDF) approach without needing external API keys (like OpenAI), removing common stop words (e.g., "the", "and") for accuracy.
*   `sip/__init__.py`:
    *   **What it does:** A standard Python file that bundles the `sip` folder into a module. It re-exports `StateIntegrityProtocol` for easy importing.

### B. The Application & Demo Files (Root Directory)
These files demonstrate or package the core engine.

*   `app.py` **(The Streamlit Frontend)**:
    *   **What it does:** A graphical User Interface (UI) built with Streamlit. It imports `sip.protocol.StateIntegrityProtocol` to show a user-friendly dashboard with charts showing drift.
*   `integrity_engine.py` **(The Concept Sandbox)**:
    *   **What it does:** A simple script containing pure Numpy logic (`np.dot`) to show the bare-bones mathematical concept behind cosine similarity and auditing a pipeline. It operates independently of the `sip` package.
*   `run_test.py` **(The Quick Test)**:
    *   **What it does:** A 7-line script verifying that the package runs effectively.

---

## 3. How the Components Link Together

1.  **User Init:** `sip = StateIntegrityProtocol(threshold=0.15)`
    *   *Result:* Initializes an empty `SemanticAnchor` and a `FidelityObserver`.
2.  **Anchoring:** `sip.anchor("Original query text")`
    *   *Follow the link:* `protocol.py` calls `anchor.py` -> `anchor.py` calls `embeddings.py` to turn text into `[0.5, 0.1, ...]`. Vector is saved.
3.  **Observing:** `sip.observe("Agent output text")`
    *   *Follow the link:* `protocol.py` calls `observer.py`. `observer.py` calls `embeddings.py` on the output text.
    *   *Math:* `observer.py` calculates `1.0 - cosine_similarity(anchor_vector, new_vector)`.
    *   *History:* `observer.py` saves the result. `protocol.py` checks if the result is greater than `0.15` and warns the system if true.

---

## 4. Architect's Blueprint: Rebuilding It Yourself

To make your own open-source version in another language or completely rewritten, here is your implementation plan:

1.  **Step 1: The Vectorizer (Embeddings)**
    *   Write a function that takes a String and outputs an Array of Floats.
    *   *Tip:* You can skip writing a custom TF-IDF (like `embeddings.py` did) and simply use a pre-built model (e.g., calling OpenAI's `text-embedding-3-small` or HuggingFace embeddings).
2.  **Step 2: The Core Object (Anchor)**
    *   Create a simple state/singleton object that stores two fields: `originalText` (String) and `originalVector` (Array of Floats).
3.  **Step 3: The Math Utility (Cosine Similarity)**
    *   Write a standard Math function: `(Dot Product of A * B) / (Magnitude of A * Magnitude of B)`.
4.  **Step 4: The Evaluation Endpoint (Observer)**
    *   Write a method that accepts a new String constraint. Vectorize it. Compare it to your stored Anchor using your Math utility.
    *   Output the Drift Score `(1 - Similarity)`.
5.  **Step 5: The Guardrail (Protocol Orchestrator)**
    *   Write an Orchestrator class. Give it a `threshold` config (e.g. `0.20`).
    *   If `Observer` returns drift > `0.20`, throw an exception, execute a callback, or pause the system.

---

## 5. FastAPI Concept: Exposing SIP as a Service

If you want to use SIP within a modern backend stack (FastAPI), here is the architecture. In this concept, the API keeps track of "Sessions" (an AI chain execution), allowing an external AI framework to report its steps via HTTP.

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Dict
# Assume sip is installed
from sip import StateIntegrityProtocol

app = FastAPI(title="State Integrity API", version="1.0")

# In-memory session store mapping Session ID to a Protocol instance
# (In production, you'd use a database like Redis to store vectors)
session_store: Dict[str, StateIntegrityProtocol] = {}

class AnchorRequest(BaseModel):
    session_id: str
    intent_prompt: str
    threshold: float = 0.15

class ObserveRequest(BaseModel):
    session_id: str
    agent_output: str

@app.post("/api/v1/anchor", status_code=status.HTTP_201_CREATED)
def set_anchor(req: AnchorRequest):
    """
    Initialize a new AI agent execution session and set the ground truth intention.
    """
    sip = StateIntegrityProtocol(threshold=req.threshold)
    sip.anchor(req.intent_prompt)
    session_store[req.session_id] = sip
    return {"message": "Anchor set successfully.", "session_id": req.session_id}

@app.post("/api/v1/observe")
def observe_drift(req: ObserveRequest):
    """
    Called by the agent after completing a step to check for state decay.
    """
    if req.session_id not in session_store:
        raise HTTPException(status_code=404, detail="Session not found. Please anchor first.")
    
    sip = session_store[req.session_id]
    result = sip.observe(req.agent_output)
    
    response = {
        "step": result.step,
        "drift_score": result.drift,
        "is_aligned": result.is_aligned
    }
    
    # Example showing a business logic reaction over the API
    if not result.is_aligned:
        response["alert"] = "CRITICAL_DRIFT_DETECTED"
        response["message"] = "Agent must be realigned."
        
    return response

@app.get("/api/v1/history/{session_id}")
def get_session_history(session_id: str):
    """
    Retrieve the full log of how the agent drifted over the session.
    """
    if session_id not in session_store:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    sip = session_store[session_id]
    history = [
        {"step": r.step, "drift": r.drift, "text_snippet": r.text[:50]+"..."} 
        for r in sip.history
    ]
    return {"session_id": session_id, "history": history}

# HOW TO USE IT:
# 1. Start agent -> POST /anchor -> {'session_id':'123', 'intent_prompt': 'Summarize book'}
# 2. Agent task 1 done -> POST /observe -> {'session_id':'123', 'agent_output': 'Chapter 1 summary...'}
# 3. Agent task 2 done -> POST /observe -> {'session_id':'123', 'agent_output': 'The quick brown fox...'} -> (Alert: high drift!)
```

### Why this is powerful:
You can deploy this FastAPI microservice as a standalone "Reviewer". Then, completely separate agentic bots written in JavaScript, Python, or Go can just hit the API endpoints to ask: "*Am I still doing what I am supposed to do?*"
