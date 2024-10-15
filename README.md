# RubHew FastAPI Project

Welcome to the RubHew FastAPI project! This project is designed to provide a robust API for managing user data and other related functionalities. Below you'll find instructions for setting up the environment, running the FastAPI application, and using Jenkins for CI/CD.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Running the API](#running-the-api)
- [Running Tests](#running-tests)
- [Jenkins Pipeline](#jenkins-pipeline)

## Prerequisites

Before you start, ensure you have the following installed on your machine:

- Python 3.12 or higher
- [Poetry](https://python-poetry.org/docs/#installation) for dependency management
- [Jenkins](https://www.jenkins.io/doc/book/installing/) (if you plan to use Jenkins for CI/CD)

## Setup

1. **Create a Virtual Environment:**

   To isolate your project dependencies, create a virtual environment. In your terminal, navigate to the project directory and run:

   ```bash
   python -m venv venv
   ```

2. **Activate the Virtual Environment:**

   - **On macOS/Linux:**

     ```bash
     source venv/bin/activate
     ```

   - **On Windows:**

     ```bash
     venv\Scripts\activate
     ```

3. **Install Dependencies Using Poetry:**

   First, make sure Poetry is installed on your machine. If it’s not, you can install it by following the instructions on the [Poetry website](https://python-poetry.org/docs/#installation).

   Then, install the project dependencies by running:

   ```bash
   poetry install
   ```

## Running the API

To run the FastAPI application, use one of the following methods:

- **Using the provided script:**

   - **On macOS/Linux:**

     ```bash
     ./scripts/run-api
     ```

     If you encounter permission issues, run the following command to change the file permissions:

     ```bash
     chmod +x ./scripts/run-api
     ```

   - **On Windows:**

     ```bash
     ./scripts/run-api.bat
     ```

- **Directly using Uvicorn:**

   If you prefer to run the application using a standard command, you can do so with:

   ```bash
   uvicorn "rubhew.main:create_app" --factory --reload
   ```

## Running Tests

To run tests for your FastAPI application, ensure your virtual environment is activated and run:

```bash
pytest
```

## Jenkins Pipeline

To set up a Jenkins pipeline for this project, follow these steps:

1. **Create a New Pipeline Job:**
   - In Jenkins, click on "New Item" and select "Pipeline".

2. **Define the Pipeline Script:**
   - In the pipeline configuration, define your Jenkins pipeline script to include stages for building, testing, and deploying your FastAPI application. Below is a sample pipeline script:

   ```groovy
   pipeline {
       agent any

       stages {
           stage('Checkout') {
               steps {
                   git 'https://github.com/aempee1/RubHew-MobileAppProject.git'  // Replace with your repository URL
               }
           }
           stage('Setup Environment') {
               steps {
                   sh 'python -m venv venv'
                   sh 'source venv/bin/activate && pip install poetry'
                   sh 'source venv/bin/activate && poetry install'
               }
           }
           stage('Run Tests') {
               steps {
                   sh 'source venv/bin/activate && pytest'
               }
           }
           stage('Deploy') {
               steps {
                   // Add your deployment steps here
               }
           }
       }

       post {
           always {
               // Clean up or send notifications if needed
           }
       }
   }
   ```

3. **Save and Build the Pipeline:**
   - Save your pipeline configuration and click on "Build Now" to run the pipeline.

## Contributing

If you want to contribute to this project, feel free to submit a pull request or open an issue for discussion.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
```

### Notes:
- Make sure to replace the Git repository URL in the Jenkins pipeline with your actual repository.
- Adjust any project-specific details in the `README.md` as necessary.

You can now copy this content directly into your `README.md` file. If you need any further modifications, let me know!