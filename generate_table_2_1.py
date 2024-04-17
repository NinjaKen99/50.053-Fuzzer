import os
import json
import sys
import csv

def read_json(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def generate_csv_table(app_name, session_number):
    session_path = f'sessions/{app_name}/session {session_number}'
    gen_times_path = os.path.join(session_path, 'test_gen_times.json')
    exec_times_path = os.path.join(session_path, 'test_exec_times.json')

    gen_times = read_json(gen_times_path)
    exec_times = read_json(exec_times_path)

    if not gen_times or not exec_times:
        print("Data files are missing or empty.")
        return

    csv_file_path = os.path.join(session_path, 'efficiency_table.csv')

    with open(csv_file_path, 'w', newline='') as csvfile:
        fieldnames = ['Test ID', 'Generation Time (s)', 'Execution Time (s)']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        total_gen = 0
        total_exec = 0

        for test_id, gen_time in gen_times.items():
            exec_time = exec_times.get(test_id, 0)
            total_gen += gen_time
            total_exec += exec_time
            writer.writerow({'Test ID': test_id, 'Generation Time (s)': gen_time, 'Execution Time (s)': exec_time})

        avg_gen = total_gen / len(gen_times)
        avg_exec = total_exec / len(exec_times)

        writer.writerow({'Test ID': 'Average', 'Generation Time (s)': avg_gen, 'Execution Time (s)': avg_exec})

    print(f"CSV table has been generated at {csv_file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_table.py <app_name> <session_number>")
        sys.exit(1)

    app_name = sys.argv[1]
    session_number = int(sys.argv[2])

    generate_csv_table(app_name, session_number)
