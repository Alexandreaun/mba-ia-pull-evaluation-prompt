from pathlib import Path
import os
from dotenv import load_dotenv
import json
from langsmith import Client as LangSmithClient
from typing import Optional

load_dotenv()

SCRIPT_DIR = Path(__file__).parent
DATASET_FILE = SCRIPT_DIR / "bug_to_user_story.jsonl"
DATASET_NAME = "bug_to_user_story"

client = LangSmithClient()

def upload_langsmith_dataset(
    dataset_file: Path, 
    dataset_name: str,
    description: str, 
    langsmith_client
) -> int:
   
    with open(dataset_file, "r") as f:
        examples = [json.loads(line) for line in f if line.strip()]

    try:
        dataset = langsmith_client.read_dataset(dataset_name=dataset_name)

        for example in langsmith_client.list_examples(dataset_name=dataset_name):
            langsmith_client.delete_example(example.id)

    except Exception:
        dataset = langsmith_client.create_dataset(
            dataset_name=dataset_name, description=description
        )

    for example in examples:
        inputs = example["inputs"]
        outputs = example["outputs"]
        metadata = example.get("metadata", {})

        langsmith_client.create_example(
            inputs=inputs,
            outputs=outputs,
            metadata=metadata,  
            dataset_id=dataset.id,
        )

    return len(examples)

count = upload_langsmith_dataset(
    DATASET_FILE, 
    DATASET_NAME, 
    "Dataset bugs to user stories", 
    client
)

print(f"Dataset '{DATASET_NAME}' updated with {count} examples")
