#!/usr/bin/env python3
import argparse
import os
import json
import anthropic
import time


def main():
    parser = argparse.ArgumentParser(
        description="Retrieve results from a completed Claude batch using SDK"
    )
    parser.add_argument(
        "--batch-id",
        required=True,
        help="ID of the completed batch (e.g., msgbatch_01PN3XYMTxabV9tPkucuy9mG)",
    )
    parser.add_argument(
        "--output-dir",
        default="./responses",
        help="Directory to save responses",
    )
    parser.add_argument(
        "--api-key",
        help="Anthropic API key (defaults to ANTHROPIC_API_KEY env var)",
    )
    parser.add_argument(
        "--id-map", help="JSON file mapping custom_ids to titles (optional)"
    )
    parser.add_argument(
        "--fallback",
        action="store_true",
        help="Use HTTP fallback if SDK method fails",
    )

    args = parser.parse_args()

    # API key priority: 1. Command line arg, 2. Environment variable
    api_key = args.api_key or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "API key not found. Please provide it via --api-key argument or ANTHROPIC_API_KEY environment variable."
        )

    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    # Initialize id_to_title map
    id_to_title = {}
    if args.id_map and os.path.exists(args.id_map):
        with open(args.id_map, "r") as f:
            id_to_title = json.load(f)

    # Initialize Anthropic client
    client = anthropic.Anthropic(api_key=api_key)

    try:
        # Get batch status
        batch_status = client.messages.batches.retrieve(args.batch_id)
        print(f"Batch status: {batch_status.processing_status}")
        print(f"Request counts: {batch_status.request_counts}")

        if batch_status.processing_status != "ended":
            print(
                "Batch processing hasn't ended yet. Waiting for completion..."
            )
            while batch_status.processing_status != "ended":
                time.sleep(10)
                batch_status = client.messages.batches.retrieve(args.batch_id)
                print(f"Status: {batch_status.processing_status}")

        # Process results using SDK method
        print("Processing results using SDK method...")
        success = False

        try:
            # Use the SDK's results method to iterate through results
            for result in client.messages.batches.results(args.batch_id):
                # Access attributes directly as object properties
                custom_id = result.custom_id

                # If we don't have the title mapping, use custom_id
                title = id_to_title.get(custom_id, custom_id)

                filename = os.path.join(
                    args.output_dir, f"{title.replace(' ', '_')}.txt"
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

                    print(f"Saved response for '{title}' to {filename}")
                else:
                    # Handle error case
                    error_obj = result.result.error
                    error_message = getattr(
                        error_obj, "message", "Unknown error"
                    )
                    print(f"Error processing '{title}': {error_message}")

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
                client, batch_status, id_to_title, args.output_dir, api_key
            )

    except Exception as e:
        print(f"Error retrieving results: {str(e)}")


def process_results_http(
    client, batch_status, id_to_title, output_dir, api_key
):
    """Fallback method using HTTP requests if SDK method fails"""
    import requests

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

        # If we don't have the title mapping, use custom_id or index
        title = id_to_title.get(custom_id, custom_id)
        if not title:
            title = f"result_{i}"

        filename = os.path.join(output_dir, f"{title.replace(' ', '_')}.txt")

        if result["result"]["type"] == "succeeded":
            # Extract the text content from the response
            message = result["result"]["message"]
            content = message["content"]
            response_text = (
                content[0]["text"] if content else "No content returned"
            )

            # Save response to file
            with open(filename, "w", encoding="utf-8") as f:
                f.write(response_text)

            print(f"Saved response for '{title}' to {filename}")
        else:
            error_message = result.get("result", {}).get(
                "error", "Unknown error"
            )
            print(f"Error processing '{title}': {error_message}")

    print("All results processed successfully with HTTP method!")


if __name__ == "__main__":
    main()
