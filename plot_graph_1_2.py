import os
import json
import matplotlib.pyplot as plt
import sys
from datetime import datetime

def read_json(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def plot_interesting_tests_over_time(app_name, session_number):
    session_dir = os.path.join('sessions', app_name, f'session {session_number}')
    if not os.path.exists(session_dir):
        os.makedirs(session_dir)

    interesting_path = os.path.join(session_dir, 'interesting.json')
    tests_path = os.path.join(session_dir, 'tests.json')

    interesting_data = read_json(interesting_path)
    tests_data = read_json(tests_path)

    # Extract the timestamps for interesting tests and all tests
    interesting_timestamps = sorted([datetime.fromisoformat(value["timestamp"]) for value in interesting_data.values() if isinstance(value, dict) and "timestamp" in value])
    test_timestamps = sorted([datetime.fromisoformat(timestamp) for timestamp in tests_data.values()])
    print(interesting_timestamps)
    print(test_timestamps)
    # Generate the y-values for the graph: number of interesting tests found up to each test timestamp
    y_values = []
    current_count = 0
    test_idx = 0
    for timestamp in test_timestamps:
        while test_idx < len(interesting_timestamps) and timestamp >= interesting_timestamps[test_idx]:
            current_count += 1
            test_idx += 1
        y_values.append(current_count)
    print(y_values)
    # Plot the graph
    plt.figure(figsize=(12, 6))
    plt.plot(test_timestamps, y_values, marker='o', linestyle='-')
    plt.xlabel('Time')
    plt.ylabel('Interesting Tests (count)')
    plt.title(f'Interesting Tests vs Time')
    plt.grid(True)
    plt.xticks(rotation=45)

    # Save the plot to the specified directory
    output_file_path = os.path.join(session_dir, 'interesting_tests_over_time.png')
    plt.savefig(output_file_path)
    plt.close()

    print(f"Plot saved to {output_file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python plot_graph_1_2.py <app_name> <session_number>")
        sys.exit(1)

    app_name = sys.argv[1]
    session_number = int(sys.argv[2])
    plot_interesting_tests_over_time(app_name, session_number)