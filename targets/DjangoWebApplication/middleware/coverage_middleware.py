import json
import coverage
from django.http import JsonResponse, HttpResponse
from django.template.response import TemplateResponse


class CoverageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # # Initialize coverage on startup
        # self.cov = coverage.Coverage(config_file="../../.coveragerc")
        # self.cov.start()

    def __call__(self, request):
        self.cov = coverage.Coverage(config_file="../../.coveragerc")
        self.cov.start()  # Start a new coverage measurement

        response = self.get_response(request)
        # Stop coverage measurement for the current request
        self.cov.stop()

        # Save the coverage data to a dictionary
        coverage_data = {}
        self.cov.get_data().lines
        for filename in self.cov.get_data().measured_files():
            lines = self.cov.get_data().lines(filename)
            coverage_data[filename] = lines
        # Attach coverage data to the response
        print(type(response))
        # try:
        #     if type(response) == TemplateResponse:
        #         response_data = json.loads(response.content)
        #         response_data["coverage"] = coverage_data
        #         response = JsonResponse(response_data)
        #     elif type(response) == HttpResponse:
        #         response_data = response.json()
        #         response_data["coverage"] = coverage_data
        #         response = JsonResponse(response_data)
        # except:
        #     response = JsonResponse(coverage_data)
        return response
