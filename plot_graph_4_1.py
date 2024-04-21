import os
import json
import matplotlib.pyplot as plt
import sys

def count_entries(file_path):
    try:
        with open(file_path, 'r') as file:
            data: dict
            data = json.load(file)
            data.pop("0")
            return len(data)
    except FileNotFoundError:
        return 0

def plot_graph(app_name, num_sessions):
    sessions_dir = f'sessions/{app_name}'
    interesting_counts = []
    crash_counts = []

    for i in range(1, num_sessions + 1):
        session_path = os.path.join(sessions_dir, f'session {i}')
        interesting_path = os.path.join(session_path, 'interesting.json')
        crash_path = os.path.join(session_path, 'failure.json')
        interesting_counts.append(count_entries(interesting_path))
        
        crash_counts.append(count_entries(crash_path))

    sessions = [f'Session {i}' for i in range(1, num_sessions + 1)]

    x = range(len(sessions))
    width = 0.35

    fig, ax = plt.subplots()
    rects1 = ax.bar(x, interesting_counts, width, label='Interesting Tests')
    rects2 = ax.bar([p + width for p in x], crash_counts, width, label='Crashes/Bugs')

    ax.set_ylabel('Counts')
    ax.set_title('Test Results by Session')
    ax.set_xticks([p + width / 2 for p in x])
    ax.set_xticklabels(sessions)
    ax.legend()

    plot_file_path = os.path.join(sessions_dir, 'stability_graph.png')
    plt.savefig(plot_file_path)
    plt.close()

    print(f"Plot saved as {plot_file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python plot_graph_4_1.py <app_name> <num_sessions>")
        sys.exit(1)

    app_name = sys.argv[1]
    num_sessions = int(sys.argv[2])

    plot_graph(app_name, num_sessions)
