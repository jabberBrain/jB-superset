# jB-Superset 💻

**A customized fork of [Apache Superset](https://superset.apache.org/) for visualizing chat analytics at [jabberBrain](https://www.stats.jabberbrain.com/)**

---

## 📖 Overview

**jB-Superset** is a tailored version of Apache Superset, designed to visualize and analyze data from chat sessions, agent activity, user feedback, and related KPIs. It features enhanced integrations that bridge Superset with internal chat tools, enabling direct navigation from dashboards to relevant chats. Built for both internal analytics and client reporting, it offers:

* **📊 Chat Platform Integration**: Seamlessly link dashboards with chat solutions.
* **📂 Automatic Backups**: Protect PostgreSQL metadata with automated backups in production.
* **⚙️ Optimized Configs**: Preconfigured for development, staging, and production via Docker Compose and Github Actions.

---

## 🛠️ Technologies Used

| Technology                                                  | Purpose                            |
| ----------------------------------------------------------- | ---------------------------------- |
| [Python (Flask, SQLAlchemy)](https://www.python.org/)       | Backend framework & ORM            |
| [JavaScript (React, Webpack)](https://reactjs.org/)         | Frontend UI for dashboards         |
| [Node.js](https://nodejs.org/)                              | Build frontend assets              |
| [PostgreSQL](https://www.postgresql.org/)                   | Metadata database                  |
| [Redis](https://redis.io/)                                  | Caching and async queues           |
| [Celery](https://docs.celeryq.dev/)                         | Task scheduling & background jobs  |
| [Docker + Docker Compose](https://docs.docker.com/compose/) | Containerization and orchestration |

---

## 🚀 Getting Started

### 📚 Development Environment

This setup is ideal for building and testing new features. It uses `docker-compose.yml` and produces a larger image (\~5GB) with full dev dependencies.

**Steps:**

1. **Clone the repository:**

   ```bash
   git clone https://github.com/jabberBrain/jb-superset.git
   cd jb-superset
   ```

2. **Configure environment variables:**

   * Defaults are in `/docker/.env`
   * To override, create `/docker/.env-local`
   * Do not edit `/docker/.env` directly

3. **Start the containers:**

   ```bash
   docker compose up -d
   ```

   * This builds the Superset image and runs `npm ci && npm run build` for the frontend
   * If the build fails, increase Docker's memory allocation and retry

4. **Access Superset:**

   * Navigate to [http://localhost:8088](http://localhost:8088) or the port defined in `.env`
   * Login with user `admin` and password `admin`.

---

### 🏠 Production-like Environment (Local)

Uses `docker-compose-local.yml` for a lighter-weight setup (\~1.5GB) without backups, useful for staging or client demos.

**Steps:**

1. **Clone the repository:**

   ```bash
   git clone https://github.com/jabberBrain/jb-superset.git
   cd jb-superset
   ```

2. **Build the frontend manually:**

   ```bash
   cd superset-frontend
   npm ci
   npm run build
   cd ..
   ```

3. **Set up environment variables:**

   ```bash
   cp /docker/.env .env
   # Edit .env with secrets or custom settings
   ```

4. **Start the services:**

   ```bash
   docker compose -f docker-compose-local.yml up -d
   ```

5. **Access Superset:**

   * [http://localhost:8088](http://localhost:8088) or as defined in `.env`
   * Login with user `admin` and password `admin`.

---

### 📆 Production Environment

This mode runs with backups and production optimizations using `docker-compose-prod.yml`.

**Steps:**

1. **Clone the repository:**

   ```bash
   git clone https://github.com/jabberBrain/jb-superset.git
   cd jb-superset
   ```

2. **Build frontend manually (if building locally):**

   ```bash
   cd superset-frontend
   npm ci
   npm run build
   cd ..
   ```

3. **Set up environment variables:**

   ```bash
   cp /docker/.env .env
   # Specify SUPERSET_IMAGE if using a pre-built image
   ```

4. **Start production services:**

   ```bash
   docker compose -f docker-compose-prod.yml up -d
   ```

5. **Access Superset:**

   * As configured in `.env` (default: [http://localhost:8088](http://localhost:8088))
   * Login with user `admin` and password `admin`.

---

## 💾 Backup Strategy

In production, the PostgreSQL metadata is automatically backed up at regular intervals. This ensures that dashboards, charts, and configurations can be recovered in case of system failure.

---

## 📅 Branching Strategy

| Branch        | Purpose                                |
| ------------- | -------------------------------------- |
| `development` | Active development and feature testing |
| `main`        | Production-ready, stable releases      |

* Always commit to `development` or feature branches.
* Only merge into `main` after passing QA and staging tests.

---

## 📚 Documentation

* **Apache Superset Docs**: [https://superset.apache.org/docs](https://superset.apache.org/docs)
* **jB-Superset Internal Docs**: Refer to your team wiki or documentation hub

---

## 🧰 CI/CD Pipeline

This repository uses **GitHub Actions** to automate builds and deployments:

* **Push to `main`**: Triggers deployment to the production environment. We will also run jest in the future.
* **Push to `development`**: In the future we might run tests.
* Future work includes integrating automated testing into the pipeline
