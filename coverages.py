from datetime import datetime
from os import path
import os
import subprocess
import coverage
from lcovparser import parse_file, Record
async def get_latest_file(directory):
    """
    Returns the latest modified file in the specified directory.
    """
    files = []
    for file_name in os.listdir(directory):
        file_path = path.join(directory, file_name)
        if path.isfile(file_path):
            files.append((path.getmtime(file_path), file_path))

    if not files:
        return None
    latest_file = max(files, key=lambda x: x[0])[1]
    return latest_file


# def get_coverage_for_file(filename):
#     """
#     Retrieve coverage data for a specified file from the .coverage data file.
#     Returns a list of line numbers that have been covered.
#     """
#     try:
#         cov = coverage.Coverage()
#         cov.load()
#         file_coverage = cov.get_data().lines(filename)
#         return file_coverage
#     except coverage.CoverageException:
#         print(f"No coverage information found for file: {filename}")
#         return None
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#         return None


async def get_coverage_data(type):
    """
    Retrieves coverage data without combining data files.
    Returns a dictionary with file paths as keys and coverage data as values.
    """
    # Example usage
    if type == "http" or type == "coap":
        latest_file_path = await get_latest_file("./coverages")
        cov = coverage.Coverage(
            data_file=latest_file_path, config_file="./.coveragerc", auto_data=True
        )

        cov.load()
        cov_data = cov.get_data()
        coverage_dict = {}

        for filename in cov_data.measured_files():
            lines = cov_data.lines(filename)
            coverage_dict[filename] = lines
        
    else:
        subprocess.run(['lcov', '--capture', '--directory', './targets/Zephyr/', '--output-file', 'lcov.info', '-q'], 
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)
        coverage_dict = dict()
        report = parse_file("./lcov.info", ignore_incorrect_counts=True, merge_duplicate_line_hit_counts=True)
        file:Record
        for file in report:
            coverage_dict[file] = sorted(report[file].lines_executed)

    return coverage_dict


async def has_new_coverage(total_coverage_data: dict, current_coverage_data: dict):
    is_interesting = False
    """Compare old and new coverage data to determine if any new lines of code are covered, and updates the total coverage data"""
    for file, current_cover in current_coverage_data.items():
        previous_cover = total_coverage_data.get(file, [])
        c = list(filter(lambda x: x not in previous_cover, current_cover))
        # If the current coverage is greater than the previous coverage, a new line of code is considered covered
        if len(c) != 0:
            combined = list(set(previous_cover) | set(current_cover))
            is_interesting = True
            total_coverage_data[file] = combined
    return is_interesting


async def is_interesting(total_coverage_data, current_coverage_data, interesting_time, mutated_input_seed, method):
    """
    Check if the response indicates a potential error, contains sensitive information,
    or if new coverage was detected.
    """
    # # Check if the status code is None or non-standard for successful responses
    # if status_code is None or not (200 <= int(status_code) < 300):
    #     print("Found a non-successful status code.")
    #     return True

    # # Lowercase payload for case-insensitive searching
    # lower_payload = response_payload.lower()

    # # Check for indicators of errors or sensitive information in the response
    # error_indicators = ["exception", "error", "unhandled", "failure", "traceback"]
    # sensitive_info_indicators = ["password", "username", "private key", "API key", "secret"]

    # # Check for error indicators
    # if any(indicator in lower_payload for indicator in error_indicators):
    #     print("Found a potential error indicator in the response.")
    #     return True

    # # Check for sensitive information indicators
    # if any(indicator in lower_payload for indicator in sensitive_info_indicators):
    #     print("Found potential sensitive information in the response.")
    #     return True

    # Check for new coverage
    new_coverage = await has_new_coverage(total_coverage_data, current_coverage_data)
    if new_coverage:
        print("New code coverage detected, which is interesting.")
        interesting_time[len(interesting_time.keys())] = {"timestamp": datetime.now().isoformat(), "route": str(method), "input": mutated_input_seed}
        return True
    # No indicators of interest found
    return False