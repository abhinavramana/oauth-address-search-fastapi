This initializes a FASTAPI instance for searching zip codes

## Prerequisites

1. You should have python installed based on the operating system of your choice (Windows, Linux, MacOS). Further instructions can be found [here](https://www.python.org/downloads/)
2. Ensure that pip is installed. You can check if pip is installed by running the following command in your terminal:
```bash
pip --version
```
If not installed, follow instructions here: [pip installation](https://pip.pypa.io/en/stable/installation/)
3. Make sure you have FastAPI and its dependencies installed. You can install them using pip:
```bash
pip install -r requirements.txt
```
4. Ensure you have a working internet connection to download the dependencies.
5. There is a zips.csv already provided in the repository. This is the file that will be used to search for zip codes. You can replace this file with your own file, but ensure that the file is in the same format as the provided file.

From here on, all instructions will be based on the assumption that you have met the above prerequisites and you are Running Linux (ubuntu) environment.

## Running the application

Open a terminal or command prompt, and run the following command to start the FastAPI server:
```bash
uvicorn application:app --reload
```

## Testing the application

Once the server is running, you can access the API endpoints using a tool like cURL or by sending HTTP requests from your application.
The 2 endpoints that are available are:
1. To retrieve zip code data for a specific zip code, send a GET request to http://localhost:8000/zip/{zip_code}, replacing {zip_code} with the desired zip code.
2. To match a city name and retrieve the top 3 closest zip codes, send a POST request to http://localhost:8000/match with a JSON payload containing the city field. For example:
```json
{
  "city": "Cheyenne"
}
```

## Auto-generated API documentation

You can also access the FastAPI automatic documentation by visiting http://localhost:8000/docs in your web browser. It provides an interactive interface to explore and test the API endpoints.

## Code structure

As you can see, the code is structured in a way that the main logic is in the `application.py` file. 
The `zips.csv` file is read and stored in a dictionary for easy access. 
The `zip_code` and `match` functions are the main functions that handle the API requests and are in application.py : The `zip_code` function retrieves the data for a specific zip code, while the `match` function matches a city name and retrieves the top 3 closest zip codes.
`bootup.py` is used to load the data from the csv file and store it in a optimized data structures. This is then used in the `application.py` file to retrieve the data.
`models.py` is used to define the data models for the API requests and responses.