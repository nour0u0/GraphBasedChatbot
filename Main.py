
import sys
import json
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMessageBox

from Service.Register import RegisterService
from Service.Graph import Graph
from Service.ModelDownloader import ModelDownloader
from Service.EmbeddingService import EmbeddingService
from View.MainView import MainWindow


# -------------------------------------------------
# Configuration
# -------------------------------------------------

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"


def load_config():
    """Load and validate chatbot settings from config.json."""

    if not CONFIG_PATH.is_file():
        raise FileNotFoundError(
            f"Configuration file not found: {CONFIG_PATH}"
        )

    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        config = json.load(file)

    required_keys = {
        "FALLBACK_ANSWER",
        "INITIAL_NODE_ID",
        "FALLBACK_NODE_ID",
        "SIMILARITY_THRESHOLD",
    }

    missing_keys = required_keys - config.keys()

    if missing_keys:
        raise ValueError(
            "Missing configuration keys: "
            + ", ".join(sorted(missing_keys))
        )

    if not isinstance(config["FALLBACK_ANSWER"], str):
        raise ValueError("FALLBACK_ANSWER must be a string.")

    for key in ("INITIAL_NODE_ID", "FALLBACK_NODE_ID"):
        if type(config[key]) is not int or config[key] < 1:
            raise ValueError(
                f"{key} must be a positive integer."
            )

    threshold = config["SIMILARITY_THRESHOLD"]

    if (
        isinstance(threshold, bool)
        or not isinstance(threshold, (int, float))
        or not 0 <= threshold <= 1
    ):
        raise ValueError(
            "SIMILARITY_THRESHOLD must be between 0 and 1."
        )

    config["SIMILARITY_THRESHOLD"] = float(threshold)

    return config


# -------------------------------------------------
# Model Setup
# -------------------------------------------------

def prepare_embedding_service():
    """
    Load the local embedding model or download it if missing.
    Returns an EmbeddingService using the loaded model.
    """

    downloader = ModelDownloader()

    result = downloader.exec()

    if result != ModelDownloader.DialogCode.Accepted:
        if downloader.error_message:
            raise RuntimeError(
                "Embedding model setup failed:\n"
                + downloader.error_message
            )

        raise RuntimeError(
            "Embedding model setup was cancelled."
        )

    if downloader.model is None:
        raise RuntimeError(
            "Model setup finished without providing a model."
        )

    return EmbeddingService(model=downloader.model)


# -------------------------------------------------
# GUI
# -------------------------------------------------

def run_gui(config):
    app = QApplication(sys.argv)

    try:
        embedding_service = prepare_embedding_service()

        window = MainWindow(
            InNodeId=config["INITIAL_NODE_ID"],
            FallBackNodeId=config["FALLBACK_NODE_ID"],
            FallBackAnswer=config["FALLBACK_ANSWER"],
            Threshold=config["SIMILARITY_THRESHOLD"],
        )

        window.show()
        sys.exit(app.exec())

    except Exception as error:
        QMessageBox.critical(
            None,
            "Startup Error",
            str(error),
        )
        sys.exit(1)


# -------------------------------------------------
# CLI
# -------------------------------------------------

def run_cli(config):
    graph = Graph(
        Id=1,
        InNodeId=config["INITIAL_NODE_ID"],
        FallBackNodeId=config["FALLBACK_NODE_ID"],
        FallBackAnswer=config["FALLBACK_ANSWER"],
        Threshold=config["SIMILARITY_THRESHOLD"],
    )

    initial_node = graph.get_node(graph.ActiveNodeID)

    print(
        "Chatbot started. Type 'exit' to quit or "
        "'reset' to restart."
    )

    if initial_node is not None:
        print(f"Bot: {initial_node.Answer}")

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() == "exit":
                print("Bot: Goodbye!")
                break

            if user_input.lower() == "reset":
                graph.reset()
                node = graph.get_node(graph.ActiveNodeID)

                if node is not None:
                    print(f"Bot: {node.Answer}")

                continue

            response = graph.process(user_input)

            if response:
                print(f"Bot: {response}")

        except KeyboardInterrupt:
            print("\nBot: Goodbye!")
            break

        except Exception as error:
            print(f"Error: {error}")


# -------------------------------------------------
# Main
# -------------------------------------------------

def main():
    try:
        config = load_config()
    except Exception as error:
        print(
            f"Configuration Error: {error}",
            file=sys.stderr,
        )
        sys.exit(1)

    if "--register" in sys.argv:
        try:
            embedding_service = prepare_embedding_service()

            # RegisterService must support receiving the service
            # if registration should reuse this already-loaded model.
            RegisterService().register("graph.json")

        except Exception as error:
            print(
                f"Registration Error: {error}",
                file=sys.stderr,
            )
            sys.exit(1)

        return

    if "--cli" in sys.argv:
        run_cli(config)
    else:
        run_gui(config)


if __name__ == "__main__":
    main()
