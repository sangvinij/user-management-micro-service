# User management microservice

# Navigation
* ***[Software versions](#software-versions)***
* ***[Getting started](#getting-started)***
   * ***[Run via Docker Compose](#run-via-docker-compose)***
   * ***[Run locally](#run-locally)***
* ***[API](#api)***
* ***[Running tests](#running-tests)***

## Software versions
- Python: 3.10.12
- Pip: 23.3.1
- Poetry: 1.6.1

## Getting started
### Run via Docker Compose
To run this project, follow the steps below:
1. Install [Docker](https://docs.docker.com/engine/install/) and [Docker Compose](https://docs.docker.com/compose/install/) on your computer if they are not already installed.
2. Clone the repository to your local machine

        git clone git@github.com:sangvinij/user-management-micro-service.git
3. Navigate to the root directory of the project

        cd user-management-micro-service


4. configure `.env` file by assigning values to the variables defined in `.env.sample`

        cp .env_sample .env

 - ***NOTE: The variable values specified in `.env.sample` are just for example. You must configure `.env` file with your own settings***
 5. Start services

         docker compose up

### Run locally
To run this project locally, first of all make sure that you have `python 3.10.12` installed on your machine. Then follow next steps:
1. Make sure that you've got database available.
2. Make steps 2 - 4 of the instruction [above](#run-via-docker-compose).

3. If you have [Task](https://taskfile.dev/) installed:
 - Setup environment by running `task build`
 - Apply migrations by running `task db-migrate`
 - Start development server by running `task run-server`

4. If you haven't [Task](https://taskfile.dev/) installed:
 - Install `poetry v1.6.1` by running `pip install poetry==1.6.1`. 
 - Create and activate virtual environment by running `poetry shell`. 
 - Install dependencies by running `poetry install`. 
 - Apply migrations by running `alembic upgrade head`. 
 - Start development server by running `uvicorn user_management.main:app`.

After completing these steps, the project will be running and available on [http://localhost:8000/](http://localhost:8000/).

## API
The entire API-scheme of the application is available on the main page of the service as well as on
`/redoc` and `/openapi.json` endpoints.

## Running tests
You can run project's tests by running either `pytest` or `task run-tests` from the root directory of
the project. Make sure that you have `WEBAPP_TESTS_HOST` variable set in `.env` file correctly.
