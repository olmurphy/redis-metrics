[![Last Commit](https://img.shields.io/github/last-commit/olmurphy/redis-metrics?style=for-the-badge)](https://github.com/olmurphy/redis-metrics/master)
[![Contributors](https://img.shields.io/github/contributors/olmurphy/redis-metrics?style=for-the-badge)](https://github.com/olmurphy/redis-metrics/graphs/contributors)
[![Commit Activity](https://img.shields.io/github/commit-activity/y/olmurphy/redis-metrics?style=for-the-badge)](https://github.com/olmurphy/redis-metrics/graphs/commit-activity)
[![Repo Size](https://img.shields.io/github/repo-size/olmurphy/redis-metrics?style=for-the-badge)](https://github.com/olmurphy/redis-metrics)
[![Top Language](https://img.shields.io/github/languages/top/olmurphy/redis-metrics?style=for-the-badge)](https://github.com/olmurphy/redis-metrics/search?l=YOUR_TOP_LANGUAGE)
[![Forks](https://img.shields.io/github/forks/olmurphy/redis-metrics?style=for-the-badge)](https://github.com/olmurphy/redis-metrics/network/members)
[![Stars](https://img.shields.io/github/stars/olmurphy/redis-metrics?style=for-the-badge)](https://github.com/olmurphy/redis-metrics/stargazers)
[![Issues](https://img.shields.io/github/issues/olmurphy/redis-metrics?style=for-the-badge)](https://github.com/olmurphy/redis-metrics/issues)
[![Open Issues](https://img.shields.io/github/issues-raw/olmurphy/redis-metrics?state=open&style=for-the-badge)](https://github.com/olmurphy/redis-metrics/issues)
[![Closed Issues](https://img.shields.io/github/issues-closed-raw/olmurphy/redis-metrics?style=for-the-badge)](https://github.com/olmurphy/redis-metrics/issues?q=is%3Aclosed)
[![License](https://img.shields.io/github/license/olmurphy/redis-metrics?style=for-the-badge)](https://github.com/olmurphy/redis-metrics/blob/master/LICENSE)
![Created At](https://img.shields.io/github/created-at/olmurphy/redis-metrics?style=for-the-badge
)
[![LinkedIn](https://img.shields.io/badge/linkedin-%230077B5.svg?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/owenmurphy2022/)


<!-- Improved compatibility of back to top link: See: https://github.com/olmurphy/redis-metrics/pull/73 -->
<a id="readme-top"></a>


<!-- PROJECT LOGO -->
<br />
<div align="center">

  <h1 align="center">Redis Metrics Controller</h1>

  <p align="center">
    Redis Metrics Controller to run as a cron job to monitor metrics with Redis.
    <br />
    <a href="https://github.com/olmurphy/redis-metrics"><strong>Explore the docs » (pending)</strong></a>
    <br />
    <a href="https://github.com/olmurphy/redis-metrics/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    &middot;
    <a href="https://github.com/olmurphy/redis-metrics/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

This project aims to provide a robust and efficient solution for monitoring Redis metrics, offering developers valuable insights into their Redis server's performance. By leveraging Python, we create a user-friendly way to log out to to your metrics tracker (Granafa, Prometheus, etc.) to visualize and analyze key Redis metrics, enabling proactive optimization and troubleshooting.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

[![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/) [![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/) [![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



## Getting Started

To run this Redis metrics application locally, follow these steps:

### Prerequisites

* **Python:** Version 3.9 or higher.
* **Docker:** If you prefer running the application in a container.
* **Redis Server:** A running Redis server with a valid certificate.
* **Command-Line:** Familiarity with basic command-line operations.
* **Environment Variables:** Understanding of setting environment variables.

### Installation and Execution (Using Docker - Recommended)

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/olmurphy/redis-metrics.git](https://github.com/olmurphy/redis-metrics.git)
    cd redis-metrics
    ```

2.  **Build the Docker Image:**
    ```bash
    docker build -t redis-metrics-app .
    ```

3.  **Set Environment Variables:**
    * Create a `.env` file in the project's root directory.
    * Add your Redis connection details and certificate path, encoded in base64. Ensure the certificate is properly encoded.
        ```
        REDIS_URL=redis://<username>:<password>@<host>:<port>/<db>
        REDIS_CERT_PATH=/app/redis_cert.b64 #This path is relative to the docker container.
        ```
    * Place your base64 encoded certificate into the root directory of the project, and name it redis_cert.b64

4.  **Run the Docker Container:**
    ```bash
    docker run --env-file .env redis-metrics-app
    ```
    * This command will start the application within a Docker container, using the environment variables defined in your `.env` file. The application will then begin to log Redis metrics.

### Installation and Execution (Without Docker - Manual Setup)

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/olmurphy/redis-metrics.git
    cd redis-metrics
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python3.9 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate  # On Windows
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Environment Variables:**
    * Set the `REDIS_URL` and `REDIS_CERT_PATH` environment variables in your terminal or shell.
    * Ensure the certificate is properly encoded in base64.
    * Example (Linux/macOS):
        ```bash
        export REDIS_URL="redis://<username>:<password>@<host>:<port>/<db>"
        export REDIS_CERT_PATH="/path/to/your/redis_cert.b64"
        ```
    * Example (Windows):
        ```bash
        set REDIS_URL=redis://<username>:<password>@<host>:<port>/<db>
        set REDIS_CERT_PATH=C:\path\to\your\redis_cert.b64
        ```

5.  **Run the Application:**
    ```bash
    python app.py --redis-url "$REDIS_URL" --redis-cert-path "$REDIS_CERT_PATH"
    ```
    * Replace `"$REDIS_URL"` and `"$REDIS_CERT_PATH"` with your actual environment variables.

### Important Notes

* **Redis Certificate:** Ensure your Redis certificate is correctly encoded in base64 and that the path provided to the application is accurate.
* **Environment Variables:** Double-check that all environment variables are set correctly before running the application.
* **Docker:** Using Docker simplifies the setup process and ensures consistent execution across different environments.
* **Dependencies:** The `requirements.txt` file lists all necessary Python dependencies.
* **Security:** Be mindful of storing sensitive information such as Redis passwords and certificates. Avoid committing them directly to version control.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



## Usage

After installation, the application will provide a dashboard displaying key Redis metrics such as:

* Connected clients
* Memory usage
* Key space hits/misses
* Command statistics

You can navigate through different sections of the dashboard to view specific metrics and analyze Redis performance. The application may also allow for configuration of metric refresh intervals and alert thresholds.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



## Roadmap

See the [open issues](https://github.com/olmurphy/redis-metrics/issues) for a full list of proposed features (and known issues).

* [ ] Implement real-time metric updates.
* [ ] Add customizable dashboards.
* [ ] Implement alert system for critical metrics.
* [ ] Support for Redis Cluster monitoring.
* [ ] Add detailed command statistics.
* [ ] Enhance visual representation of metrics using charts and graphs.
* [ ] Implement user authentication and authorization.
* [ ] Add support for metric history and trend analysis.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Top contributors:

<a href="https://github.com/olmurphy/redis-metrics/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=olmurphy/redis-metrics" />
</a>

<p align="right">(<a href="#readme-top">back to top</a>)</p>



## License

Distributed under the Unlicense License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



## Contact

Your Name - [@owenmurphy2022](https://x.com/owenmurphy2022) - owen261@icloud.com

Project Link: [https://github.com/olmurphy/redis-metrics](https://github.com/olmurphy/redis-metrics)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



## Acknowledgments

TBD

<p align="right">(<a href="#readme-top">back to top</a>)</p>