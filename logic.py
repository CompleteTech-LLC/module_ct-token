# improved_code_base/core/logic.py

import os
import logging
import json
from advanced_tools import advanced_tools_manager
from core.token_optimizer import optimize_prompt, get_token_count, truncate_to_token_limit


PROJECT_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'project_management', 'project_db.json'))
PROJECT_MANAGEMENT_DIR = os.path.dirname(PROJECT_DB_PATH)
os.makedirs(PROJECT_MANAGEMENT_DIR, exist_ok=True)


def initialize_project_db():
    """
    Initialize the project_db.json file if it doesn't exist.
    """
    if not os.path.isfile(PROJECT_DB_PATH):
        default_data = {
            "tasks": {},
            "team": {},
            "features": {},
            "updates": {}
        }
        save_project_data(default_data)
        logging.info("Initialized new project database.")


def load_project_data():
    """
    Load project management data from project_db.json.
    """
    try:
        with open(PROJECT_DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        initialize_project_db()
        return load_project_data()
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse project_db.json: {e}")
        return {}
    except Exception as e:
        logging.error(f"Unexpected error loading project data: {e}")
        return {}


def save_project_data(data):
    """
    Save project management data to project_db.json.
    """
    try:
        with open(PROJECT_DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        logging.info("Project data saved successfully.")
    except Exception as e:
        logging.error(f"Failed to save project data: {e}")


def process_prompt(prompt):
    """
    Process a single prompt through various tools.

    Args:
        prompt (str): The prompt to process.
    """
    logging.info("Processing prompt from llm_prompt_raw.txt")

    tokens_before = get_token_count(prompt)
    logging.info(f"Tokens before optimization: {tokens_before}")

    # Optimize the prompt
    optimized_prompt = optimize_prompt(prompt)
    logging.debug(f"Optimized Prompt: {optimized_prompt}")

    tokens_after_optimization = get_token_count(optimized_prompt)
    logging.info(f"Tokens after optimization: {tokens_after_optimization}")

    # Truncate the optimized prompt to token limit if necessary
    final_prompt = truncate_to_token_limit(optimized_prompt)
    tokens_final = get_token_count(final_prompt)
    logging.info(f"Tokens after truncation: {tokens_final}")

    # Simulate calling LLM with optimized and truncated prompt
    response = advanced_tools_manager.execute("call_llm", prompt=final_prompt)
    llm_response = response.get('response', '')
    if llm_response:
        logging.info("LLM Response received.")
        logging.debug(f"LLM Response: {llm_response}")
    else:
        logging.error(f"Failed to get LLM response: {response.get('error')}")
        return

    # Continue processing the LLM response
    # Named Entity Recognition
    entities = advanced_tools_manager.execute("named_entity_recognition", text=llm_response)
    if "entities" in entities:
        logging.info("Named Entities extracted.")
        logging.debug(f"Named Entities: {entities['entities']}")
    else:
        logging.error(f"Failed to perform NER: {entities.get('error')}")

    # Language Detection
    language = advanced_tools_manager.execute("detect_language", text=llm_response)
    if "language" in language:
        logging.info(f"Language Detected: {language['language']}")
    else:
        logging.error(f"Failed to detect language: {language.get('error')}")



def update_project_tasks(new_task):
    """
    Update project data with a new task if it doesn't already exist.

    Args:
        new_task (dict): The new task to add.
    """
    try:
        project_data = load_project_data()
        if 'tasks' not in project_data:
            project_data['tasks'] = {}
        # Check if the task already exists based on description
        task_exists = any(
            task.get('description') == new_task['description'] for task in project_data.get('tasks', {}).values()
        )
        if task_exists:
            logging.info("Task already exists in project data.")
        else:
            existing_ids = [
                int(task_id[1:]) for task_id in project_data['tasks'].keys()
                if task_id.startswith('T') and task_id[1:].isdigit()
            ]
            next_task_number = max(existing_ids, default=0) + 1
            new_task_id = f"T{next_task_number:03d}"
            project_data['tasks'][new_task_id] = new_task
            save_project_data(project_data)
            logging.info(f"New task {new_task_id} added to project data.")
    except Exception as e:
        logging.error(f"Error updating project data: {e}")


def main_logic():
    """
    Main logic function to run the application.
    """
    logging.info("Starting application.")

    # Ensure project database is initialized
    initialize_project_db()

    # Load project data
    project_data = load_project_data()
    if not project_data:
        logging.error("Project data could not be loaded.")
        return
    logging.info("Project data loaded successfully.")

    # Read and process prompt from llm_prompt_raw.txt
    try:
        with open('llm_prompt_raw.txt', 'r', encoding='utf-8') as f:
            prompt = f.read()
        process_prompt(prompt)
    except FileNotFoundError:
        logging.error("llm_prompt_raw.txt not found.")
    except Exception as e:
        logging.error(f"Error reading llm_prompt_raw.txt: {e}")

    # Update project data with new tasks or updates
    new_task = {
        "description": "Implement more efficient token optimization in prompt processing",
        "deadline": "2025-03-15",
        "assigned": "Team Member D"
    }
    update_project_tasks(new_task)

    logging.info("All operations completed successfully.")
