# Content Processing API

A FastAPI application for content processing with CRUD operations and Educative course content generation.

## Features

- FastAPI framework with automatic API documentation
- Pydantic models for data validation
- CRUD operations for items
- Health check endpoint
- **Educative course content generation** with authentication
- Environment variable configuration
- Interactive API documentation with Swagger UI

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Setup environment variables:
```bash
# Copy the example environment file
copy .env.example .env

# Edit .env file with your actual Educative credentials
```

## Environment Configuration

Create a `.env` file in the project root with the following variables:

```env
# Educative API Configuration
EDUCATIVE_TOKEN=your-educative-token
EDUCATIVE_COOKIE=your-full-cookie-string

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### Getting Educative Credentials

1. **Login to Educative.io** in your browser
2. **Open Developer Tools** (F12)
3. **Go to Network tab**
4. **Navigate to any course** (e.g., https://www.educative.io/courses/grokking-the-system-design-interview)
5. **Look for API calls** to `educative.io/api/collection/`
6. **Copy the request headers**:
   - `Cookie`: Copy the entire cookie string
   - `magicbox-auth`: Extract the token from this cookie

## Running the Application

### Development Mode
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
python main.py
```

## API Endpoints

### Basic CRUD Operations
- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /items` - Get all items
- `GET /items/{item_id}` - Get item by ID
- `POST /items` - Create new item
- `PUT /items/{item_id}` - Update item
- `DELETE /items/{item_id}` - Delete item

### Content Generation
- `POST /generate-book-content` - **NEW!** Generate book content from Educative course

#### Generate Book Content Request:
```json
{
  "educative_course_name": "grokking-the-system-design-interview",
  "use_env_credentials": true,  // Use credentials from .env file
  "token": "optional-override-token",
  "cookie": "optional-override-cookie"
}
```

#### Response:
```json
{
  "success": true,
  "data": { /* Course content data */ },
  "error_message": null,
  "source": "credentials_from_environment"
}
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

You can test the API using:
1. Interactive Swagger UI at `/docs`
2. Run the test script: `python test_api.py`
3. curl commands (see examples below)
4. Postman or similar API testing tools

### Example curl commands:

```bash
# Health check
curl -X GET "http://localhost:8000/health"

# Generate book content (using environment credentials)
curl -X POST "http://localhost:8000/generate-book-content" \
     -H "Content-Type: application/json" \
     -d '{
       "educative_course_name": "grokking-the-system-design-interview",
       "use_env_credentials": true
     }'

# Generate book content (using custom credentials)
curl -X POST "http://localhost:8000/generate-book-content" \
     -H "Content-Type: application/json" \
     -d '{
       "educative_course_name": "grokking-the-system-design-interview",
       "use_env_credentials": false,
       "token": "your-token",
       "cookie": "your-cookie"
     }'

# Create a new item
curl -X POST "http://localhost:8000/items" \
     -H "Content-Type: application/json" \
     -d '{"name": "Test Item", "description": "A test item", "price": 29.99}'
```

## Security Notes

- Never commit your `.env` file to version control
- Keep your Educative credentials secure
- The `.env` file is already included in `.gitignore`
- Use environment variables for production deployments
