# Local Graph-Based Chatbot

A local Python chatbot that uses sentence embeddings and a directed graph to manage conversations. It combines semantic similarity matching with a node-and-edge conversation structure, allowing responses and conversation paths to be defined and edited without training a dedicated intent-classification model.

## Features

- **Local semantic matching:** Uses Sentence Transformers with `all-MiniLM-L6-v2` to convert user messages into embedding vectors.
- **Graph-based conversations:** Represents conversation states as nodes and possible user responses as directed edges.
- **Configurable similarity threshold:** Controls how closely a user message must match a registered response.
- **Graph editor:** Provides a visual interface for creating and editing conversation nodes and connections.
- **Node management:** Add, update, and delete conversation nodes.
- **Edge management:** Define user responses connecting one node to another.
- **Chat testing:** Test the conversation flow through the graphical interface.
- **Configuration tab:** Edit the fallback response, initial node, fallback node, and similarity threshold.
- **Local model management:** Loads an existing embedding model or downloads it when necessary.
- **Command-line mode:** Run and test conversations directly in the terminal.
- **JSON-based storage:** Stores the conversation graph and application configuration in JSON files.

## Technologies

- Python
- PyQt6
- Sentence Transformers
- Sentence embedding model: `all-MiniLM-L6-v2`
- JSON for graph data and configuration
- Git for version control

## Project Architecture

The project separates data models, services, and graphical views.

```text
ChatBot/
├── main.py
├── config.json
├── graph.json
├── README.md
├── LICENSE
├── .gitignore
│
├── EmbeddinModel/
│   └── all-MiniLM-L6-v2/
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

The directory structure above describes the main components. Individual filenames may vary depending on the current project version.

### 1. Model Layer

The `Model/` directory defines the data structures used to represent the conversation graph.

#### Node

A node represents a conversation state and stores the answer displayed by the chatbot.

Conceptually, a node contains:

| Field | Description |
|---|---|
| `Id` | Unique node identifier |
| `Answer` | Text displayed when the node is reached |

#### Edge

An edge represents a possible transition between two conversation states.

| Field | Description |
|---|---|
| `Id` | Unique edge identifier |
| `NodeFromID` | ID of the source node |
| `NodeToID` | ID of the destination node |
| `UserResponse` | Example of a user message that triggers the transition |
| `Embedding` | Vector representation of the registered user response |

The graph is directed: an edge from node A to node B does not automatically create a transition from B to A.

### 2. Embedding Service

`Service/EmbeddingService.py` wraps the Sentence Transformers model.

Its responsibilities include:

- Loading the embedding model from local files.
- Converting a single text into an embedding.
- Converting multiple texts into embeddings.
- Normalizing embeddings for semantic similarity comparison.
- Validating input text before encoding.

The `all-MiniLM-L6-v2` model produces 384-dimensional sentence embeddings.

Instead of requiring an exact string match, the chatbot can compare the meaning of a user's message with registered responses using vector similarity.

### 3. Graph Service

`Service/Graph.py` manages the conversation graph and its active state.

Its responsibilities include:

- Loading nodes and edges from JSON storage.
- Tracking the active conversation node.
- Retrieving outgoing edges from the active node.
- Comparing user input with registered edge responses.
- Applying the configured similarity threshold.
- Moving to the destination node when a suitable match is found.
- Handling fallback behavior when no suitable match is available.
- Resetting the conversation to its initial state.

### 4. Registration Service

`Service/Register.py` imports the graph definition from `graph.json` into the application's JSON database.

The registration file defines nodes and their connections. During registration, edge responses are converted into embeddings so that they can be matched semantically during conversations.

This separates the graph definition from the runtime data structures.

### 5. Model Downloader

`Service/ModelDownloader.py` provides a graphical setup dialog and background worker for preparing the embedding model.

It checks whether the model is already stored locally. If available, it loads the local copy. Otherwise, it downloads the model and saves it to the project's model directory.

The background worker prevents the model preparation process from blocking the GUI thread while it runs. The interface displays status messages during preparation.

An internet connection is required when the model needs to be downloaded. After the model has been saved successfully, local loading can work without internet access.

### 6. Graphical Interface

The GUI is built with PyQt6.

The main interface provides separate areas for:

- **Nodes:** Manage conversation states and their answers.
- **Edges:** Manage user-response examples and graph transitions.
- **Graph:** Visualize and edit the conversation graph.
- **Chat Test:** Interact with the chatbot and test its behavior.
- **Configuration:** Edit application settings.

The graph editor supports selecting nodes and edges and editing graph connections through the visual interface.

The configuration tab edits `config.json`. After saving configuration changes, close and restart the application for the new settings to take effect.

## How Conversation Matching Works

The chatbot uses semantic similarity rather than relying exclusively on exact text matching.

The general processing flow is:

1. The user enters a message.
2. The embedding service converts the message into a vector.
3. The graph service retrieves the outgoing edges of the active node.
4. The input embedding is compared with the embeddings stored on those edges.
5. The best candidate is evaluated against the similarity threshold.
6. If the candidate meets the threshold, the graph transitions to its destination node.
7. If no candidate meets the threshold, the configured fallback behavior is used.

For normalized embeddings, cosine similarity can be calculated using the dot product:

\[
\operatorname{similarity}(A,B)=A\cdot B
\]

The threshold determines how strict the matching behavior is. A higher threshold generally requires a closer semantic match, while a lower threshold can accept more loosely related messages.

The threshold does not guarantee that a match is correct. Registered response examples and testing remain important.

## Data Storage

The application uses JSON files to keep its data readable and editable.

### `config.json`

Stores application settings.

Example:

```json
{
    "FALLBACK_ANSWER": "I didn't understand. Could you rephrase that?",
    "INITIAL_NODE_ID": 1,
    "FALLBACK_NODE_ID": 1,
    "SIMILARITY_THRESHOLD": 0.4
}
```

- `FALLBACK_ANSWER`: Response used when the chatbot cannot find a suitable match.
- `INITIAL_NODE_ID`: Node used to start a conversation.
- `FALLBACK_NODE_ID`: Configured fallback node identifier.
- `SIMILARITY_THRESHOLD`: Minimum similarity score accepted for matching.

### `graph.json`

Defines the graph that can be registered into the database.

Conceptually, it contains a `Nodes` collection and an `Edges` collection.

Example:

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

This is a simplified example of the expected structure. The graph can contain as many nodes and edges as needed, provided that the referenced node IDs are valid.

### `DB/Node.json`

Stores registered conversation nodes.

### `DB/Edge.json`

Stores registered edges, including their user-response text and embedding vectors.

The database files and source graph serve different purposes: `graph.json` defines the graph to register, while the `DB/` files hold the runtime records.

## Installation

### Requirements

- Python 3.10 or a compatible version supported by the installed dependencies.
- Internet access for the initial model download.
- Sufficient disk space for the Python dependencies and embedding model.

### 1. Clone the repository

```bash
git clone https://github.com/nour0u0/IntentChatbot.git
cd IntentChatbot
```

### 2. Create a virtual environment

On Windows:

```bash
python -m venv .venv
```

Activate it using Command Prompt:

```bat
.venv\Scripts\activate
```

Or PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install PyQt6 sentence-transformers
```

If the project includes a `requirements.txt`, install the pinned dependencies instead:

```bash
python -m pip install -r requirements.txt
```

## Running the Application

### Graphical interface

```bash
python main.py
```

On the first run, the model setup dialog checks for the local model and downloads it if necessary. Once preparation succeeds, the main application opens.

### Command-line interface

```bash
python main.py --cli
```

The CLI accepts messages directly in the terminal.

Special commands:

- `reset` — reset the conversation.
- `exit` — close the CLI chatbot.

### Register the graph

```bash
python main.py --register
```

This imports the graph definition from `graph.json` into the JSON database using the registration service.

Run registration whenever you need to import or update the graph definition. Check the registration service's behavior before using it on an existing database, especially if you need to preserve existing records.

## Configuration and Customization

The Configuration tab provides a graphical way to modify the chatbot settings.

1. Open the application.
2. Navigate to the Configuration tab.
3. Edit the desired values.
4. Save the configuration.
5. Close and restart the application.

You can also edit `config.json` manually, provided that its JSON structure and value types remain valid.

To change the conversation itself, edit the graph through the GUI or update `graph.json` and register it.

## Development Notes

- Keep node IDs and edge references consistent.
- Ensure that edge embeddings correspond to their registered `UserResponse` text.
- Test multiple phrasings for each intended transition.
- Adjust the similarity threshold based on observed behavior.
- Keep the embedding model out of version control to avoid committing large model files.
- Keep the configuration and graph data separate from the embedding model.
- Back up the JSON database before bulk graph registration or changes.

## Limitations

- Semantic matching depends on the quality of the embedding model and registered examples.
- Similarity alone does not establish the user's intent with certainty.
- The graph must contain appropriate transitions to support the desired conversation paths.
- JSON storage is simple and transparent, but concurrent writes and large-scale data management require additional care.
- Model setup requires internet access when the model is not already available locally.

## License

MIT License
