import os
import json
import matplotlib.pyplot as plt
import sys

def read_json(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def plot_line_graph(app_name, session_number):
    session_path = f'sessions/{app_name}/session {session_number}'
    interesting_path = os.path.join(session_path, 'interesting.json')
    tests_path = os.path.join(session_path, 'tests.json')

    interesting_data = read_json(interesting_path)
    tests_data = read_json(tests_path)

    # Extract the indices (keys) and sort them
    interesting_indices = sorted(interesting_data.keys(), key=int)
    test_indices = sorted(tests_data.keys(), key=int)

    # Map the indices to their corresponding sequence in the test execution
    interesting_test_indices = [test_indices.index(i) for i in interesting_indices if i in test_indices]

    # Generate the y-values for the graph: number of interesting tests found up to each test index
    y_values = []
    current_count = 0
    test_idx = 0
    for idx in range(len(test_indices)):
        if test_idx < len(interesting_test_indices) and idx == interesting_test_indices[test_idx]:
            current_count += 1
            test_idx += 1
        y_values.append(current_count)

    plt.plot(range(len(test_indices)), y_values, marker='o', linestyle='-')
    plt.xlabel('Tests (count)')
    plt.ylabel('Interesting Tests (count)')
    plt.title(f'Interesting Tests vs Tests')
    plt.grid(True)

    # Save the plot to the specified directory
    output_file_path = os.path.join(session_path, 'interesting_vs_tests_plot.png')
    plt.savefig(output_file_path)
    plt.close()

    print(f"Plot saved to {output_file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python plot_graph_1_3.py <app_name> <session_number>")
        sys.exit(1)

    app_name = sys.argv[1]
    session_number = int(sys.argv[2])

    plot_line_graph(app_name, session_number)
