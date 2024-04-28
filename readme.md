

# Prerequisites
1. Python 3.11

2. Gcov, GCC

3. Linux/WSL installed

# Supports

1. http protocols in python3

2. coap protocols in python2

3. BLE protocols with gcov, genhtml

# Steps to setup

1. `pip install poetry`

2. `poetry install`

3. Copy .coveragerc.dist and rename it .coveragerc and edit the data dir (where .coverage file will be generated)

4. Create a .env file at where main.py is and add a COVERAGE_PROCESS_START to point to where your .coveragerc is

5. Put your application into targets directory

6. Find a way to add coverage.py api (For examples refer to targets/DjangoWebApplication/middleware/coverage_middleware.py and targets/CoAPthon/coapthon/utils.py)

7. Test and ensure that running application and running requests adds .coverage files into data dir

8. Generate a openapi json for your application

9. Add some examples for your schema

10. Run `python main.py [protocol] [directory of application] [command to run (put under quotation)] --file [file of openapi] --restart`

# Additional Steps for COAP

1. install python2

2. `python2 -m pip install coverage`

# Dump commands
python main.py coap ./targets/CoAPthon "coapserver.py" --file coap/openapi.json --restart

python main.py http ./targets/DjangoWebApplication "manage.py runserver 8000 --noreload" --file django/openapi3_0.json --restart

python main.py ble ./targets/Zephyr "./zephyr.exe --bt-dev=127.0.0.1" --restart

# Credits
bumble: https://github.com/google/bumble
Aiocoap: https://github.com/chrysn/aiocoap
AioHttp: https://github.com/aio-libs/aiohttp
lcovparser: https://github.com/ChrisTimperley/lcovparser.py
openapi3-parser: https://github.com/manchenkoff/openapi3-parser
coverage-lcov: https://github.com/TheCleric/coverage-lcov
coveragepy: https://github.com/nedbat/coveragepy

