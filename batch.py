#!/usr/bin/env python3
import argparse
import os
import json
import anthropic
from dotenv import load_dotenv
import sys
import time
import requests
import glob


def main():
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

    # Load environment variables from .env file
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Claude API Batch Processing with JSX Files"
    )
    parser.add_argument(
        "--prompts-dir",
        default="./prompts",
        help="Directory containing JSX files to process (default: ./prompts)",
    )
    parser.add_argument(
        "--system",
        default=os.path.join(script_dir, "system_prompt.txt"),
        help="Text file containing system prompt to cache (default: system_prompt.txt in script directory)",
    )
    parser.add_argument(
        "--model",
        help="Claude model to use",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        help="Maximum tokens in response",
    )
    parser.add_argument(
        "--output-dir",
        default="./responses",
        help="Directory to save responses",
    )
    parser.add_argument(
        "--api-key", help="Anthropic API key (overrides .env and env vars)"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        help="Temperature for generation (0.0-1.0). Lower = more deterministic.",
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=10,
        help="Seconds to wait between polling for batch completion",
    )
    parser.add_argument(
        "--fallback",
        action="store_true",
        help="Use HTTP fallback if SDK method fails",
    )
    parser.add_argument(
        "--file-pattern",
        default="*.jsx",
        help="File pattern to match in prompts directory (default: *.jsx)",
    )

    args = parser.parse_args()

    # API key priority: 1. Command line arg, 2. .env file, 3. Environment variable
    api_key = args.api_key or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "API key not found. Please provide it via --api-key argument, ANTHROPIC_API_KEY environment variable, or .env file."
        )

    # Set temperature from args or .env
    temperature = args.temperature or float(os.getenv("TEMPERATURE", "0.2"))
    max_tokens = args.max_tokens or int(os.getenv("MAX_TOKENS", "4000"))
    model = args.model or os.getenv("MODEL")

    # Check if system prompt file exists
    if not os.path.exists(args.system):
        raise FileNotFoundError(f"System prompt file not found: {args.system}")

    # Check if prompts directory exists
    if not os.path.exists(args.prompts_dir):
        raise FileNotFoundError(
            f"Prompts directory not found: {args.prompts_dir}"
        )

    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    # Read system prompt
    with open(args.system, "r") as f:
        system_prompt = f.read().strip()

    # Initialize Anthropic client
    client = anthropic.Anthropic(api_key=api_key)

    # Find all JSX files in the prompts directory
    jsx_files = glob.glob(os.path.join(args.prompts_dir, args.file_pattern))

    if not jsx_files:
        print(
            f"No {args.file_pattern} files found in {args.prompts_dir}. Exiting."
        )
        return

    print(f"Found {len(jsx_files)} JSX files to process.")

    # Prepare batch requests
    batch_requests = []
    id_to_filename = {}  # Map custom_id to filename for file naming

    # Process each JSX file
    for i, jsx_file in enumerate(jsx_files):
        # Read the JSX file content
        with open(jsx_file, "r", encoding="utf-8") as f:
            jsx_content = f.read().strip()

        # Get the base filename without extension for output naming
        base_filename = os.path.splitext(os.path.basename(jsx_file))[0]

        # Generate a custom_id for this request
        custom_id = f"request_{i}"
        id_to_filename[custom_id] = base_filename

        # Create request object
        batch_requests.append(
            anthropic.types.messages.batch_create_params.Request(
                custom_id=custom_id,
                params=anthropic.types.message_create_params.MessageCreateParamsNonStreaming(
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=[
                        {
                            "type": "text",
                            "text": system_prompt,
                            "cache_control": {"type": "ephemeral"},
                        }
                    ],
                    messages=[{"role": "user", "content": jsx_content}],
                ),
            )
        )

    print(f"Submitting batch of {len(batch_requests)} requests...")

    # Submit batch request
    try:
        # Create the batch
        message_batch = client.messages.batches.create(requests=batch_requests)
        batch_id = message_batch.id
        print(f"Batch submitted with ID: {batch_id}")
        print(f"Initial status: {message_batch.processing_status}")
        print(f"Request counts: {message_batch.request_counts}")

        # Poll for completion
        while True:
            print(
                f"Checking batch status... (polling every {args.poll_interval} seconds)"
            )
            # Correct method call - pass the ID as a positional argument
            batch_status = client.messages.batches.retrieve(batch_id)

            print(f"Status: {batch_status.processing_status}")
            print(f"Counts: {batch_status.request_counts}")

            if batch_status.processing_status == "ended":
                print("Batch processing complete!")
                break

            time.sleep(args.poll_interval)

        # Process results using SDK method
        print("Processing results using SDK method...")
        success = False

        try:
            # Use the SDK's results method to iterate through results
            for result in client.messages.batches.results(batch_id):
                # Access attributes directly as object properties
                custom_id = result.custom_id

                if custom_id in id_to_filename:
                    filename_base = id_to_filename[custom_id]
                    filename = os.path.join(
                        args.output_dir, f"{filename_base}.txt"
                    )

                    # Check result type (succeeded or error)
                    if result.result.type == "succeeded":
                        # Extract text content
                        message = result.result.message
                        content_item = message.content[0]
                        response_text = content_item.text

                        # Save response to file with UTF-8 encoding
                        with open(filename, "w", encoding="utf-8") as f:
                            f.write(response_text)

                        print(
                            f"Saved response for '{filename_base}' to {filename}"
                        )
                    else:
                        # Handle error case
                        error_obj = result.result.error
                        error_message = getattr(
                            error_obj, "message", "Unknown error"
                        )
                        print(
                            f"Error processing '{filename_base}': {error_message}"
                        )
                else:
                    print(
                        f"Warning: Received result with unknown custom_id: {custom_id}"
                    )

            success = True
            print("All results processed successfully!")

        except Exception as e:
            print(f"Error processing with SDK method: {str(e)}")
            if not args.fallback:
                raise
            success = False

        # Fall back to HTTP method if SDK method failed and fallback is enabled
        if not success and args.fallback:
            process_results_http(
                client, batch_status, id_to_filename, args.output_dir, api_key
            )

    except Exception as e:
        print(f"Error in batch processing: {str(e)}")

    print("All processing complete!")


def process_results_http(
    client, batch_status, id_to_filename, output_dir, api_key
):
    """Fallback method using HTTP requests if SDK method fails"""
    if not batch_status.results_url:
        print("No results URL available. Unable to retrieve responses.")
        return

    print(
        f"Falling back to HTTP method. Downloading results from: {batch_status.results_url}"
    )
    headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01"}
    response = requests.get(batch_status.results_url, headers=headers)

    if response.status_code != 200:
        print(
            f"Error downloading results: {response.status_code} - {response.text}"
        )
        return

    # Process JSONL results
    for i, line in enumerate(response.text.strip().split("\n")):
        result = json.loads(line)
        custom_id = result.get("custom_id") or result.get("id")

        if custom_id in id_to_filename:
            filename_base = id_to_filename[custom_id]
            filename = os.path.join(output_dir, f"{filename_base}.txt")

            if result["result"]["type"] == "succeeded":
                # Extract the text content from the response
                message = result["result"]["message"]
                content = message["content"]
                response_text = (
                    content[0]["text"] if content else "No content returned"
                )

                # Save response to file with UTF-8 encoding
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(response_text)

                print(f"Saved response for '{filename_base}' to {filename}")
            else:
                error_message = result.get("result", {}).get(
                    "error", "Unknown error"
                )
                print(f"Error processing '{filename_base}': {error_message}")
        else:
            print(
                f"Warning: Received result with unknown custom_id: {custom_id}"
            )

    print("All results processed successfully with HTTP method!")


if __name__ == "__main__":
    main()
