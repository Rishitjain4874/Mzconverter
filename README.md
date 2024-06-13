# MzConverter.py

## Overview

MzConverter.py is a Python script designed to convert Ultra Data Language Format (UDLF) files into Go code. It takes UDLF files as input and generates corresponding Go struct definitions based on the structure and declarations present in the UDLF files.

## Author

This project was developed by Rishit Jain under the guidance of Mr. Manish Gandhi, Senior Vice President at Jio Platform Limited.

## Features

- Lexical analysis of UDLF files
- Token generation
- Abstract Syntax Tree (AST) generation
- Conversion of AST to Go code

## Usage

1. Place your UDLF files in the `UDLF files` directory.
2. Run the `MzConverter.py` script.
3. The generated Go code will be printed to the console.

Alternatively, you can use the Flask app provided in the script by running the `flask_app()` function. This will start a Flask server on `http://localhost:5011`. You can then send POST requests to the `/` endpoint with the UDLF file content in the request body, and the server will respond with the generated Go code.

## Testing

The script includes a `main_check_test` function that runs a series of tests against the UDLF files in the `UDLF files` directory. It reports the number of passed and failed cases, along with a list of failed case numbers.

To run the tests, call the `main_check_test` function with the starting file number and the maximum file number to be tested:

```python
main_check_test(starting_file_number, max_file_number)

Dependencies
This project utilizes the following Python libraries:

re (Regular Expressions)
nltk (Natural Language Toolkit)
flask (Web Framework)
request (Flask Request Handling)
string (String Operations)

Make sure to install these libraries before running the script.
Note
Please note that this script was created for a specific use case and may require modifications to work with different UDLF file structures or to generate code in other programming languages.
