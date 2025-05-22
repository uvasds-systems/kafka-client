from quixstreams import Application
import json
from collections import defaultdict
from datetime import datetime

def main():
    # Initialize the Kafka application
    app = Application(
        broker_address="localhost:19092",
        loglevel="DEBUG",
        consumer_group="github_event_aggregator",
        # auto_offset_reset="earliest",
    )

    # Initialize counter for event types
    event_counts = defaultdict(int)
    last_print_time = datetime.now()

    with app.get_consumer() as consumer:
        # Subscribe to the GitHub events topic
        consumer.subscribe(["github_events"])

        print("Starting to consume GitHub events...")
        print("Press Ctrl+C to stop and see final counts")

        while True:
            msg = consumer.poll(1)

            if msg is None:
                # Print current counts every 10 seconds
                current_time = datetime.now()
                if (current_time - last_print_time).seconds >= 10:
                    print("\nCurrent Event Type Counts:")
                    for event_type, count in sorted(event_counts.items()):
                        print(f"{event_type}: {count}")
                    last_print_time = current_time
                continue
            elif msg.error() is not None:
                raise Exception(msg.error())
            else:
                try:
                    # Parse the message value
                    value = json.loads(msg.value())
                    
                    # Extract and count the event type
                    event_type = value.get('type')
                    if event_type:
                        event_counts[event_type] += 1
                    
                    # Store the offset
                    consumer.store_offsets(msg)
                except json.JSONDecodeError:
                    print("Error: Invalid JSON message received")
                except Exception as e:
                    print(f"Error processing message: {str(e)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nFinal Event Type Counts:")
        for event_type, count in sorted(event_counts.items()):
            print(f"{event_type}: {count}") 