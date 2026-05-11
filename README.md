# 🩸 BloodConnect 

BloodConnect is a distributed web platform that connects hospitals and donors while integrating an automated blood demand forecasting system. Hospitals can manage blood requests and campaigns, donors can view and respond to requests, and an AI service predicts next-month blood demand using an explainable EMA-based model directly from live database data.

## 🚀 Architecture Overview

The system consists of four primary components running within Docker containers:

1.  **`db`**: PostgreSQL database (Persistent storage).
2.  **`ai`**: Pure Python gRPC service for ML predictions (runs on `ai:50051`).
3.  **`hospital`**: Django backend for hospital management and coordination (Web/API on `localhost:8000`).
4.  **`donor`**: Django backend for donor management and scheduling (Web/API on `localhost:8001`).


---

## ⚙️ Prerequisites

You must have the following installed on your machine:

1.  **Git**
2.  **Docker** and **Docker Compose** (must be installed and running).

---

## 👨‍💻 Local Setup and Launch

### 1. Configuration

1.  **Clone the Repository:**
    ```bash
    git clone [your_repo_url]
    cd bloodConnect
    ```

2.  **Create `.env` File:** Copy the template and fill in your secrets. **Do not commit the resulting `.env` file!**
    ```bash
    cp .env.template .env
    # Now, edit the new .env file with your specific passwords/keys.
    ```

### 2. Build and Run

Launch all four services with a single command. The `--build` flag ensures your service images are up-to-date.

```bash
docker-compose up --build
```


### 3. Verification (Critical)

Once all four services show **`Up`** in the `docker-compose ps` output, verify the core inter-service communication.

 **Test 1: AI Service gRPC Connection**

This test confirms that the **`hospital_service`** can successfully resolve the **`ai_service`** hostname and perform a gRPC call (`HealthCheck`).

* **Test URL (Browser):**
  ```
  http://localhost:8000/test-ai-grpc/
  ```

* **Expected Successful Output (JSON):**
  ```json
  {"status": "SUCCESS", "grpc_target": "ai:50051", "ai_service_response": "AI Service OK. Time: 1763837576.9651697"}
  ```
  > **Note:** If this test passes, the core network, service startup, and gRPC stubs are all fully operational.

 **Test 2: Database and Service Stability**

Run the following command to confirm all parts of the system are stable:

```bash
docker-compose ps
```

**Expected Result:**
All four services (`ai_service`, `blood_db`, `donor_service`, `hospital_service`) must show a status of **`Up`**.

---

## 🗄️ Database Structure

The BloodConnect platform uses PostgreSQL with a multi-schema architecture:

- **`donor_schema`**: Contains all donor-related tables
- **`hospital_schema`**: Contains all hospital-related tables


### Database Access

**Direct PostgreSQL Access:**
- URL: http://localhost:5050
- Email: admin@bloodconnect.com
- password: admin123

Than create a server connection to view the schemas

- Host: db
- Port: 5432
- Database: blood_db
- User_name: blood_user
- Password: blood_pass

**Django Admin Interfaces:**
- Hospital Admin: http://localhost:8000/admin
- Donor Admin: http://localhost:8001/admin

To access the admin interfaces:
Apply the migrations:

```bash
# For Hospital service
docker exec -it hospital_service python manage.py migrate

# For Donor service
docker exec -it donor_service python manage.py migrate
```

Create superusers:

```bash
# For Hospital service
docker exec -it hospital_service python manage.py createsuperuser

# For Donor service
docker exec -it donor_service python manage.py createsuperuser
```

### Insert mock data for the hospital side:

Run the below command to insert hospital service data for test

```bash
# Runs the created commands hospital_app\management\commands\insert_sample_data.py
docker exec hospital_service python manage.py insert_sample_data

```

---

## 🔎Testing the Forecasting service (unitests) & the integration with the Hospital service  

This project includes **unit tests** and **integration tests** to ensure the reliability of the distributed system.

### Run AI service tests
```bash
docker-compose exec ai python -m unittest discover tests/ -v
```
### Run backend integration tests
```bash
docker-compose exec hospital python manage.py test hospital_app.tests -v 2
```
What is tested?
* AI forecasting logic (EMA, confidence score, validation)
* gRPC communication between backend and AI service
* API responses and error handling

All tests are executed inside Docker containers to ensure consistency and reproducibility.

## Common Docker Commands (helpful)
```bash
# View running containers
docker-compose ps

# View logs for a specific service
docker-compose logs [service_name]

# Stop all services
docker-compose down

# Restart services
docker-compose up -d

# Rebuild services
docker-compose up -d --build
```


## 📚 Additional Documentation (Just for information on details)

For more detailed information, please refer to:
- [Database Documentation](DATABASE.md) - Detailed information about the database structure and access methods
<!-- - [Team Guidelines](TEAM_GUIDELINES.md) - Development guidelines for team collaboration -->

---