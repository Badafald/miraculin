# Miraculin Encryption Web Page

## Overview
The **Miraculin Encryption Web Page** is a simple web application designed primarily as a **learning tool for DevOps practices**. It provides basic functionality for encryption and decryption, but its primary purpose is to serve as a foundation for exploring and applying DevOps methodologies, tools, and workflows.

## Implementation Details
- **3 Python Services**:
  - **Web Service**: A Python-based service that handles user inputs and manages API requests.
  - **Encryption Service**: A Python-based service that applies XOR encryption and decryption to the user input.
  - **Storage Service**: A Python-based service that interacts with the database to store and retrieve encrypted entries.
  
- **Dockerization**:
  - Each of the three services has been containerized into separate Docker images for easier deployment and scalability.

- **Docker Compose**:
  - A `docker-compose.yml` file has been created to allow for easy testing and running of the entire application stack, including the web service, encryption service, storage service, and the database.

---

## Key Features
1. **Basic Application Functionality**:
   - **Input Encoding**:
     - Accepts a 3-character string.
     - Salts the input with the word `miraculin`.
     - Applies XOR encryption to generate an encoded result.
   - **Database Storage**:
     - Stores encrypted results in a database.
     - Displays a list of the 100 most recent encrypted entries.
   - **Decryption**:
     - Allows users to select an entry and decode it to reveal the original string.

2. **Evolving Architecture**:
   - **Version 0.1.0**:
     - Built as a monolithic application.
   - **Version 0.2.0**:
     - Refactored into a microservices architecture:
       - **Web Service**: Handles user interactions and API requests.
       - **Encryption Service**: Performs XOR-based encryption and decryption.
       - **Storage Service**: Manages database operations.

---

## Future Directions
- Add examples of CI/CD pipelines tailored for monolithic and microservices setups.
- Include pre-configured deployment options for cloud platforms. 

This project is a stepping stone for understanding modern software development and DevOps workflows.
