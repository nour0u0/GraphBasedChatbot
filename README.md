# GraphBasedChatbot

A local graph-based conversational engine built with Python, PyQt6, and Sentence Transformers.

GraphBasedChatbot combines **directed graph traversal** with **semantic similarity matching** to create structured conversations without requiring a dedicated intent-classification model.

Instead of selecting an answer from a global list, the chatbot evaluates the user's message against the transitions available from its current conversation state. This makes conversation paths explicit, editable, and easier to reason about.

**Repository:** https://github.com/nour0u0/graphBasedChatbot

## Features

- **Graph-based conversation management:** Represent conversation states as nodes and transitions as directed edges.
- **Semantic response matching:** Use `all-MiniLM-L6-v2` to compare the meaning of user messages with registered transition examples.
- **Configurable similarity threshold:** Control how closely a message must match a registered response.
- **Visual graph editor:** Inspect and edit the conversation structure through a PyQt6 interface.
- **Node management:** Create, edit, and delete conversation states.
- **Edge management:** Define the responses that trigger transitions between states.
- **Interactive chat testing:** Test conversation paths directly through the graphical interface.
- **Command-line interface:** Run conversations from a terminal.
- **JSON persistence:** Store graph definitions, nodes, edges, and application configuration in JSON files.
- **Local model support:** Load the embedding model from local storage or download it when needed.
- **Configurable fallback behavior:** Define the fallback answer and fallback node for unmatched messages.

## Technologies

| Technology | Purpose |
|---|---|
| Python | Application logic |
| PyQt6 | Desktop graphical interface |
| Sentence Transformers | Sentence embedding generation |
| `all-MiniLM-L6-v2` | Semantic representation of text |
| JSON | Graph definitions, configuration, and data storage |
| Git | Version control |

The `all-MiniLM-L6-v2` model produces 384-dimensional sentence embeddings.

## Architecture

The application separates graph data structures, embedding operations, conversation logic, registration, and graphical components.

```text
GraphBasedChatbot/
├── Main.py
├── Graph.json
├── config.json
├── README.md
├── .gitignore
│
├── DB/
│   ├── Node.json
│   └── Edge.json
│
├── Model/
│   ├── Node.py
│   └── Edge.py
│
├── Service/
│   ├── EmbeddingService.py
│   ├── Graph.py
│   ├── Register.py
│   └── ModelDownloader.py
│
└── View/
    ├── MainView.py
    ├── NodeTab.py
    ├── EdgeTab.py
    ├── ChatTab.py
    ├── ConfigTab.py
    └── GraphView/
        ├── GraphView.py
        ├── GraphCanvas.py
        ├── GraphNodeItem.py
        ├── GraphEdgeItem.py
        └── GraphProperties.py
```

This tree describes the documented application structure. Consult the repository for the exact current contents of each directory.

### 1. Model layer

The `Model/` directory contains the data structures used by the conversation engine.

#### Node

A node represents a conversation state and stores the answer associated with that state.

| Field | Description |
|---|---|
| `Id` | Unique node identifier |
| `Answer` | Text displayed by the chatbot when the node is reached |

#### Edge

An edge represents a directed transition between two conversation states.

| Field | Description |
|---|---|
| `Id` | Unique edge identifier |
| `NodeFromID` | Source node identifier |
| `NodeToID` | Destination node identifier |
| `UserResponse` | Example of a user message that triggers the transition |
| `Embedding` | Vector representation of the registered response |

The graph is directed. An edge from node A to node B does not automatically create an edge from B to A.

### 2. Embedding service

`Service/EmbeddingService.py` provides the interface to the sentence embedding model.

Its documented responsibilities include:

- Loading the embedding model.
- Encoding individual text inputs.
- Encoding multiple text inputs.
- Normalizing embeddings for similarity calculations.
- Validating input text.

Semantic embeddings allow the chatbot to compare messages that express similar meanings without requiring exact string equality.

For example, a registered response such as:

`I want to know the price`

may be semantically similar to:

`How much does it cost?`

Whether a particular message is accepted depends on the model, the available transition examples, and the configured similarity threshold.

### 3. Graph service

`Service/Graph.py` manages the conversation graph and its active state.

Its responsibilities include:

- Loading registered nodes and edges.
- Tracking the active node.
- Retrieving outgoing edges from the active node.
- Comparing user input with registered edge responses.
- Selecting the best matching transition.
- Applying the similarity threshold.
- Moving to a destination node when a suitable transition is found.
- Handling unmatched input through fallback behavior.
- Resetting the conversation to its initial state.

The graph constrains the set of candidate transitions. Only edges available from the active node are considered, rather than treating every registered response as a globally available answer.

### 4. Registration service

`Service/Register.py` provides the graph registration workflow.

The graph definition describes nodes and their connections. During registration, the transition responses are converted into embeddings and stored with the runtime records.

This separates the editable graph definition from the data used during conversation processing.

**Important:** Back up the existing JSON database before registering a modified graph. Check the registration implementation before reusing an existing database, especially if existing records must be preserved.

### 5. Model downloader

`Service/ModelDownloader.py` handles preparation of the embedding model.

The documented workflow checks for an available local model and downloads it when necessary. The setup process provides status information through the graphical interface.

An internet connection is required if the model must be downloaded. Once the required model files are available locally, model loading can operate without downloading them again.

### 6. Graphical interface

The graphical interface is built with PyQt6.

The main interface provides the following areas:

- **Nodes:** Manage conversation states and their answers.
- **Edges:** Manage transition examples and graph connections.
- **Graph:** Visualize and edit the directed graph.
- **Chat Test:** Test the conversation engine interactively.
- **Configuration:** Modify chatbot settings.

The visual graph editor makes the conversation structure explicit. Rather than encoding every conversational branch in a large collection of conditional statements, the developer can inspect the states and transitions directly.

## How conversation matching works

The conversation engine follows this general processing sequence:

1. The user submits a message.
2. The embedding service converts the message into a vector.
3. The graph service identifies the outgoing edges of the active node.
4. The input embedding is compared with the registered embeddings of those edges.
5. The best candidate is selected.
6. The candidate's similarity is evaluated against the configured threshold.
7. If the candidate is accepted, the conversation moves to the destination node.
8. If no candidate meets the threshold, the configured fallback behavior is applied.

For normalized embedding vectors, cosine similarity can be calculated using their dot product:

\[
\operatorname{similarity}(A,B)=A\cdot B
\]

A higher threshold generally makes acceptance stricter, while a lower threshold allows more loosely related messages to match.

A similarity score is not a guarantee of correctness. Good transition examples, appropriate thresholds, and testing with different user phrasings remain important.

## Data storage

The application uses JSON files to separate graph definitions, runtime records, and configuration.

### `config.json`

This file stores the chatbot's configuration.

Example:

```json
{
    "FALLBACK_ANSWER": "I didn't understand. Could you rephrase that?",
    "INITIAL_NODE_ID": 1,
    "FALLBACK_NODE_ID": 1,
    "SIMILARITY_THRESHOLD": 0.4
}
```

| Setting | Description |
|---|---|
| `FALLBACK_ANSWER` | Text returned when no suitable match is found |
| `INITIAL_NODE_ID` | Node used to start a conversation |
| `FALLBACK_NODE_ID` | Configured fallback node identifier |
| `SIMILARITY_THRESHOLD` | Minimum similarity score accepted for matching |

The values shown are an example. The appropriate threshold depends on the application and should be evaluated empirically.

### `Graph.json`

This file defines the conversation graph to be registered.

A simplified conceptual example is:

```json
{
    "Nodes": [
        {
            "Id": 1,
            "Answer": "Hello! How can I help you?"
        },
        {
            "Id": 2,
            "Answer": "I can help you with product information."
        }
    ],
    "Edges": [
        {
            "UserResponse": "Hello",
            "StartNodeId": 1,
            "DestinationNodeId": 2
        }
    ]
}
```

The example illustrates the graph's basic structure. Use the exact field names and data format expected by the current registration implementation when editing the real file.

Node identifiers must be unique, and edge references must point to valid nodes.

### `DB/Node.json`

Stores the registered conversation nodes used by the application.

### `DB/Edge.json`

Stores registered transition records, including user-response text and embedding vectors.

The graph definition and runtime database serve different purposes:

- `Graph.json` describes the graph to register.
- `DB/Node.json` and `DB/Edge.json` hold the registered records used by the application.

## Installation

### Requirements

- Python 3.10 or another Python version compatible with the installed dependencies.
- Git.
- Internet access for the initial model download, if the model is not already available locally.
- Sufficient disk space for the Python packages and embedding model.

The commands below use Windows Command Prompt or PowerShell.

### 1. Clone the repository

```bash
git clone https://github.com/nour0u0/graphBasedChatbot.git
cd graphBasedChatbot
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it in Windows Command Prompt:

```bat
.venv\Scripts\activate
```

Or activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell prevents activation because of its execution policy, use Command Prompt or follow the appropriate PowerShell policy guidance for your environment.

### 3. Install dependencies

Upgrade `pip`:

```bash
python -m pip install --upgrade pip
```

Install the principal application dependencies:

```bash
python -m pip install PyQt6 sentence-transformers
```

If a `requirements.txt` file is present in the version you cloned, prefer its declared dependencies:

```bash
python -m pip install -r requirements.txt
```

## Running the application

Run commands from the repository root with the virtual environment activated.

### Graphical interface

```bash
python Main.py
```

The application prepares the embedding model before opening the main interface. If the model is missing, the setup workflow may require an internet connection to download it.

### Command-line interface

```bash
python Main.py --cli
```

The CLI accepts messages directly in the terminal.

Special commands:

| Command | Action |
|---|---|
| `reset` | Reset the conversation to its initial state |
| `exit` | Exit the chatbot |

### Register the graph

```bash
python Main.py --register
```

This invokes the graph registration workflow, which imports the graph definition into the JSON database.

Back up the existing database before registering changes. Do not assume registration preserves or merges existing records without checking the implementation.

**Platform note:** The source currently references `graph.json` in the registration call, while the repository's tracked file is named `Graph.json`. Windows normally resolves this capitalization difference, but case-sensitive filesystems may not. The source and filename should be made consistent before claiming Linux compatibility.

## Configuration and customization

The Configuration tab provides a graphical way to modify the chatbot's settings.

1. Launch the application.
2. Open the Configuration tab.
3. Edit the desired settings.
4. Save the configuration.
5. Restart the application if necessary for the changes to take effect.

Alternatively, edit `config.json` directly. Preserve valid JSON syntax and the expected data types.

To change the conversation itself, edit the graph through the graphical interface or modify the graph definition and run the registration workflow.

## Development notes

When extending the project, consider the following:

- Keep node identifiers unique.
- Ensure every edge references valid source and destination nodes.
- Ensure stored embeddings correspond to the associated `UserResponse` text.
- Test several phrasings for every important transition.
- Evaluate the similarity threshold against both expected matches and unrelated messages.
- Back up the runtime database before bulk registration.
- Keep large model files out of version control.
- Keep configuration, graph definitions, runtime records, and model files logically separate.
- Test fallback behavior and conversation resets.
- Verify behavior after registration, not just the validity of the source JSON.

## Limitations

- Semantic similarity does not guarantee that a user's intent has been identified correctly.
- Matching quality depends on the embedding model and the registered response examples.
- Conversation paths are limited to the transitions defined in the graph.
- Fallback behavior must be designed and tested to ensure the conversation remains understandable after an unmatched message.
- JSON storage is simple and transparent, but concurrent writes and larger datasets may require a more robust storage solution.
- Model setup requires internet access when the model is not available locally.
- The documented workflows have not been independently validated across operating systems or Python environments.



Explore the source code, inspect the graph architecture, and experiment with semantic matching:

[GitHub: GraphBasedChatbot](https://github.com/nour0u0/graphBasedChatbot)
