# Fliiply Backend

This repository contains the backend API for the Fliiply application built with Django and Django REST Framework.

## Installation

### Docker

1. Build and start the containers:

```bash
docker compose up --build
```

This launches the Django web server along with Postgres and a MinIO service as defined in `docker-compose.yml`.

### Local Django setup

1. Create and activate a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Configure environment variables (see below) in a `.env` file at the project root.
3. Apply migrations and start the development server:

```bash
python manage.py migrate
python manage.py runserver
```

The application will be available at `http://localhost:8000`.

## Environment variables

The project loads variables from a `.env` file. Important keys include:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `STRIPE_SECRET_KEY`
- `STRIPE_PUBLIC_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_ONBOARDING_RETURN_URL`
- `STRIPE_ONBOARDING_REFRESH_URL`
- `NGROK_HOST` (optional for allowing external callbacks)
- `PLATFORM_COMMISSION_PERCENT` (defaults to `0.05`)
- `CART_RESERVATION_MINUTES` (defaults to `30`)

## Running tests

Install the Python dependencies and run:

```bash
pytest
```

When using Docker you can run the suite inside the container:

```bash
docker compose run web pytest
```

## Search suggestions

`GET /api/search/suggestions/?query=<text>` returns an array of suggestion strings
matching the given query. Suggestions are pulled from product names, series and
block fields and may include frequent search terms.

## Search endpoint

The `/api/search/` URL returns active listings matching a query. Example:

```http
GET /api/search/?q=pikachu&language=EN&min_price=5&max_price=20
```

Available filters include:

- `tcg_type`, `block`, `series`
- `language`, `version`, `condition`, `grade`
- `min_price`, `max_price`, and `availability` (`in_stock` or `out_of_stock`)

Results are paginated using DRF's standard paginator.
