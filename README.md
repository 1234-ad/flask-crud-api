# Flask CRUD API 🚀

A comprehensive RESTful API built with Flask featuring full CRUD operations, SQLite database integration, pagination, filtering, and robust error handling.

## Features

- ✅ **Full CRUD Operations**: Create, Read, Update, Delete items
- 🗄️ **SQLite Database**: Lightweight, file-based database with automatic initialization
- 📄 **Pagination**: Efficient data retrieval with customizable page sizes
- 🔍 **Filtering & Search**: Filter by category and search across name/description
- 📊 **Sorting**: Sort by any field in ascending or descending order
- ✔️ **Input Validation**: Comprehensive data validation with detailed error messages
- 🌐 **CORS Support**: Cross-Origin Resource Sharing enabled
- 📝 **Comprehensive Logging**: Detailed logging for debugging and monitoring
- 🏥 **Health Check**: Built-in health monitoring endpoint
- 📚 **API Documentation**: Self-documenting API with endpoint descriptions

## Quick Start

### Installation

```bash
git clone https://github.com/1234-ad/flask-crud-api.git
cd flask-crud-api
pip install -r requirements.txt
```

### Run the Application

```bash
python app.py
```

The API will be available at `http://localhost:5000`

### Docker Support (Optional)

```bash
# Build image
docker build -t flask-crud-api .

# Run container
docker run -p 5000:5000 flask-crud-api
```

## API Endpoints

### Base URL: `http://localhost:5000`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API documentation |
| GET | `/health` | Health check |
| GET | `/items` | Get all items (with pagination/filtering) |
| GET | `/items/<id>` | Get specific item |
| POST | `/items` | Create new item |
| PUT | `/items/<id>` | Update existing item |
| DELETE | `/items/<id>` | Delete item |
| GET | `/items/categories` | Get all categories |

## Usage Examples

### 1. Get API Documentation
```bash
curl http://localhost:5000/
```

### 2. Get All Items
```bash
curl http://localhost:5000/items
```

### 3. Get Items with Pagination
```bash
curl "http://localhost:5000/items?page=1&per_page=5"
```

### 4. Filter Items by Category
```bash
curl "http://localhost:5000/items?category=Electronics"
```

### 5. Search Items
```bash
curl "http://localhost:5000/items?search=laptop"
```

### 6. Sort Items
```bash
curl "http://localhost:5000/items?sort_by=price&sort_order=desc"
```

### 7. Create New Item
```bash
curl -X POST http://localhost:5000/items \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Gaming Keyboard",
    "description": "Mechanical gaming keyboard with RGB lighting",
    "category": "Electronics",
    "price": 89.99,
    "quantity": 15
  }'
```

### 8. Update Item
```bash
curl -X PUT http://localhost:5000/items/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Laptop",
    "price": 1199.99
  }'
```

### 9. Delete Item
```bash
curl -X DELETE http://localhost:5000/items/1
```

### 10. Get Specific Item
```bash
curl http://localhost:5000/items/1
```

## Request/Response Examples

### Create Item Request
```json
{
  "name": "Wireless Headphones",
  "description": "Noise-cancelling wireless headphones",
  "category": "Electronics",
  "price": 199.99,
  "quantity": 25
}
```

### Create Item Response
```json
{
  "message": "Item created successfully",
  "item": {
    "id": 6,
    "name": "Wireless Headphones",
    "description": "Noise-cancelling wireless headphones",
    "category": "Electronics",
    "price": 199.99,
    "quantity": 25,
    "created_at": "2024-09-22 12:00:00",
    "updated_at": "2024-09-22 12:00:00"
  }
}
```

### Get Items Response
```json
{
  "items": [
    {
      "id": 1,
      "name": "Laptop",
      "description": "High-performance laptop for development",
      "category": "Electronics",
      "price": 999.99,
      "quantity": 5,
      "created_at": "2024-09-22 10:00:00",
      "updated_at": "2024-09-22 10:00:00"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total_items": 5,
    "total_pages": 1,
    "has_next": false,
    "has_prev": false
  },
  "filters": {
    "category": null,
    "search": null,
    "sort_by": "id",
    "sort_order": "asc"
  }
}
```

## Database Schema

### Items Table
```sql
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    price REAL,
    quantity INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Query Parameters

### GET /items

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `page` | integer | Page number (default: 1) | `?page=2` |
| `per_page` | integer | Items per page (max: 100, default: 10) | `?per_page=20` |
| `category` | string | Filter by category | `?category=Electronics` |
| `search` | string | Search in name/description | `?search=laptop` |
| `sort_by` | string | Sort field (id, name, category, price, quantity, created_at) | `?sort_by=price` |
| `sort_order` | string | Sort direction (asc, desc) | `?sort_order=desc` |

## Error Handling

The API returns appropriate HTTP status codes and detailed error messages:

### Validation Error (400)
```json
{
  "error": "Validation failed",
  "details": ["'name' is required", "'price' must be a valid number"]
}
```

### Not Found (404)
```json
{
  "error": "Item not found"
}
```

### Server Error (500)
```json
{
  "error": "Internal server error"
}
```

## Testing

Run the comprehensive test suite:

```bash
python -m pytest test_app.py -v
```

Or with unittest:
```bash
python test_app.py
```

### Test Coverage
- API endpoint functionality
- CRUD operations
- Input validation
- Error handling
- Database operations

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | 5000 |
| `FLASK_ENV` | Environment (development/production) | production |

### Development Mode
```bash
export FLASK_ENV=development
python app.py
```

## Sample Data

The application automatically creates sample data on first run:
- Laptop (Electronics) - $999.99
- Coffee Mug (Kitchen) - $12.99
- Python Book (Books) - $39.99
- Wireless Mouse (Electronics) - $29.99
- Notebook (Office) - $4.99

## Project Structure

```
flask-crud-api/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── test_app.py        # Unit tests
├── README.md          # Documentation
├── items.db           # SQLite database (created automatically)
└── Dockerfile         # Docker configuration (optional)
```

## Production Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker
```bash
docker build -t flask-crud-api .
docker run -p 5000:5000 flask-crud-api
```

### Environment Setup
```bash
export FLASK_ENV=production
export PORT=8000
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Flask web framework
- SQLite for lightweight database storage
- Flask-CORS for cross-origin support
- Comprehensive error handling and validation