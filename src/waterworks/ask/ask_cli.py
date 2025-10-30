from conduit.cli.cli_class import ConduitCLI
from conduit.cli.query_function import QueryFunctionInputs
from conduit.sync import Model, Prompt, Conduit, Verbosity, Response
from conduit.prompt.prompt_loader import PromptLoader
from pathlib import Path
import platform
import subprocess
import os
import logging

PROMPT_DIR = Path(__file__).parent / "prompts"

logger = logging.getLogger(__name__)
prompt_loader = PromptLoader(PROMPT_DIR)


def get_system_info():
    os_info = platform.system() + " " + platform.release()
    python_version = platform.python_version()
    cpu_model = platform.processor()
    if platform.system() == "Darwin":
        memory_cmd = ["sysctl", "hw.memsize"]
        gpu_cmd = ["system_profiler", "SPDisplaysDataType"]
    elif platform.system() == "Linux":
        memory_cmd = ["grep", "MemTotal", "/proc/meminfo"]
        gpu_cmd = ["lshw", "-C", "display"]
    else:
        print("Unsupported OS")
        return

    try:
        memory_size = subprocess.run(
            memory_cmd, capture_output=True, text=True
        ).stdout.strip()
    except:
        memory_size = "Unknown"

    try:
        gpu_info = subprocess.run(
            gpu_cmd, capture_output=True, text=True
        ).stdout.strip()
    except:
        gpu_info = "Unknown"

    try:
        local_ip = subprocess.run(
            ["hostname", "-I"], capture_output=True, text=True
        ).stdout.strip()
    except:
        local_ip = "Unknown"

    shell = os.environ.get("SHELL")
    terminal = os.environ.get("TERM_PROGRAM", "Unknown")

    system_info = f"""
OS: {os_info}
Python: {python_version}
CPU: {cpu_model}
Memory: {memory_size}
GPU: {gpu_info}
Local IP: {local_ip}
Shell: {shell}
Terminal: {terminal}
""".strip()
    return system_info


def generate_script_contents(files: list[str]) -> list[tuple[str, str]] | None:
    """
    For debug mode.
    Given a list of file paths, return a list of tuples containing the file name and its content.
    """
    file_data = []
    for script_file in files:
        try:
            with open(script_file, "r") as file:
                file_data.append((script_file, file.read()))
        except FileNotFoundError:
            print(f"File not found: {script_file}")
            return
    return file_data


def generate_script_output(script_file: str) -> str:
    """
    For debug mode.
    Given a script file, run it and return the output.
    """
    command = ["python", script_file]
    try:
        # Run the command directly and capture both stdout and stderr
        result = subprocess.run(command, capture_output=True, text=True)
        output = result.stdout.strip() + "\n" + result.stderr.strip()
    except Exception as e:
        output = f"Error running script: {e}"
    return output


def ask_query_function(inputs: QueryFunctionInputs) -> "Response":
    logger.debug("Running default_query_function...")
    # Extract inputs from dict
    query_input = inputs.query_input
    context = inputs.context
    append = inputs.append
    local = inputs.local
    preferred_model = inputs.preferred_model
    verbose = inputs.verbose
    include_history = inputs.include_history

    # ConduitCLI's default POSIX philosophy: embrace pipes and redirection
    combined_query = "\n\n".join([query_input, context, append])

    # Inject system message if provided and message store exists
    if Conduit.message_store:
        system_message = inputs.system_message
        if system_message:
            Conduit.message_store.ensure_system_message(system_message)

    # Our chain
    if local:
        from conduit.model.models.modelstore import ModelStore
        from conduit.model.remote_model import RemoteModel

        logger.info("Using local model.")
        if preferred_model not in ModelStore().local_models():
            preferred_model = "gpt-oss:latest"
        logger.info(f"Using model: {preferred_model}")
        model = RemoteModel(preferred_model)
        prompt_str = combined_query
        response = model.query(query_input=prompt_str, verbose=verbose)
    else:
        logger.info("Using remote model.")
        model = Model(preferred_model)
        logger.info(f"Using model: {preferred_model}")
        prompt = Prompt(combined_query)
        conduit = Conduit(prompt=prompt, model=model)
        response = conduit.run(verbose=verbose, include_history=include_history)
    assert isinstance(response, Response), "Response is not of type Response"
    return response


def main():
    # Load and render system prompt
    system_prompt: Prompt = prompt_loader["system_prompt"]
    system_message: str = system_prompt.render(
        input_variables={
            "system_info": get_system_info(),
        }
    )

    cli = ConduitCLI(
        name="ask",
        description="Your helpful system administrator.",
        query_function=ask_query_function,
        verbosity=Verbosity.PROGRESS,
        cache=True,
        persistent=True,
        system_message=system_message,
        preferred_model="flash",
    )

    cli.run()


if __name__ == "__main__":
    main()
