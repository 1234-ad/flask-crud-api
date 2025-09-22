#!/usr/bin/env python3
"""
Flask CRUD API
A RESTful API with full CRUD operations for managing items in a SQLite database
"""

from flask import Flask, request, jsonify, g
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
DATABASE = 'items.db'
app.config['DATABASE'] = DATABASE

def get_db():
    """Get database connection"""
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Close database connection"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize the database with tables"""
    with app.app_context():
        db = get_db()
        db.executescript("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                price REAL,
                quantity INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TRIGGER IF NOT EXISTS update_timestamp 
            AFTER UPDATE ON items
            BEGIN
                UPDATE items SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
        """)
        
        # Insert sample data if table is empty
        count = db.execute('SELECT COUNT(*) FROM items').fetchone()[0]
        if count == 0:
            sample_items = [
                ('Laptop', 'High-performance laptop for development', 'Electronics', 999.99, 5),
                ('Coffee Mug', 'Ceramic mug for hot beverages', 'Kitchen', 12.99, 20),
                ('Python Book', 'Learn Python programming', 'Books', 39.99, 15),
                ('Wireless Mouse', 'Ergonomic wireless mouse', 'Electronics', 29.99, 30),
                ('Notebook', 'Spiral-bound notebook', 'Office', 4.99, 50)
            ]
            
            for item in sample_items:
                db.execute(
                    'INSERT INTO items (name, description, category, price, quantity) VALUES (?, ?, ?, ?, ?)',
                    item
                )
        
        db.commit()
        logger.info("Database initialized successfully")

@app.teardown_appcontext
def close_db(error):
    """Close database connection at the end of request"""
    close_db()

def dict_from_row(row):
    """Convert sqlite3.Row to dictionary"""
    return {key: row[key] for key in row.keys()}

def validate_item_data(data, required_fields=None):
    """Validate item data"""
    if required_fields is None:
        required_fields = ['name']
    
    errors = []
    
    # Check required fields
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"'{field}' is required")
    
    # Validate data types
    if 'price' in data and data['price'] is not None:
        try:
            float(data['price'])
        except (ValueError, TypeError):
            errors.append("'price' must be a valid number")
    
    if 'quantity' in data and data['quantity'] is not None:
        try:
            int(data['quantity'])
        except (ValueError, TypeError):
            errors.append("'quantity' must be a valid integer")
    
    return errors

# API Routes

@app.route('/')
def index():
    """API documentation endpoint"""
    return jsonify({
        'message': 'Flask CRUD API',
        'version': '1.0.0',
        'endpoints': {
            'GET /': 'API documentation',
            'GET /items': 'Get all items (supports pagination and filtering)',
            'GET /items/<id>': 'Get specific item by ID',
            'POST /items': 'Create new item',
            'PUT /items/<id>': 'Update existing item',
            'DELETE /items/<id>': 'Delete item',
            'GET /items/categories': 'Get all categories',
            'GET /health': 'Health check endpoint'
        },
        'sample_request': {
            'name': 'Sample Item',
            'description': 'This is a sample item',
            'category': 'Sample Category',
            'price': 19.99,
            'quantity': 10
        }
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        db = get_db()
        db.execute('SELECT 1').fetchone()
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/items', methods=['GET'])
def get_items():
    """Get all items with optional pagination and filtering"""
    try:
        db = get_db()
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)  # Max 100 items per page
        category = request.args.get('category')
        search = request.args.get('search')
        sort_by = request.args.get('sort_by', 'id')
        sort_order = request.args.get('sort_order', 'asc')
        
        # Build query
        query = 'SELECT * FROM items WHERE 1=1'
        params = []
        
        if category:
            query += ' AND category = ?'
            params.append(category)
        
        if search:
            query += ' AND (name LIKE ? OR description LIKE ?)'
            search_term = f'%{search}%'
            params.extend([search_term, search_term])
        
        # Add sorting
        valid_sort_fields = ['id', 'name', 'category', 'price', 'quantity', 'created_at']
        if sort_by in valid_sort_fields and sort_order.lower() in ['asc', 'desc']:
            query += f' ORDER BY {sort_by} {sort_order.upper()}'
        
        # Get total count for pagination
        count_query = query.replace('SELECT *', 'SELECT COUNT(*)')
        total_items = db.execute(count_query, params).fetchone()[0]
        
        # Add pagination
        offset = (page - 1) * per_page
        query += ' LIMIT ? OFFSET ?'
        params.extend([per_page, offset])
        
        # Execute query
        cursor = db.execute(query, params)
        items = [dict_from_row(row) for row in cursor.fetchall()]
        
        # Calculate pagination info
        total_pages = (total_items + per_page - 1) // per_page
        
        return jsonify({
            'items': items,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_items': total_items,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            },
            'filters': {
                'category': category,
                'search': search,
                'sort_by': sort_by,
                'sort_order': sort_order
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting items: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """Get a specific item by ID"""
    try:
        db = get_db()
        cursor = db.execute('SELECT * FROM items WHERE id = ?', (item_id,))
        item = cursor.fetchone()
        
        if item is None:
            return jsonify({'error': 'Item not found'}), 404
        
        return jsonify({'item': dict_from_row(item)})
        
    except Exception as e:
        logger.error(f"Error getting item {item_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/items', methods=['POST'])
def create_item():
    """Create a new item"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Validate required fields
        errors = validate_item_data(data, required_fields=['name'])
        if errors:
            return jsonify({'error': 'Validation failed', 'details': errors}), 400
        
        db = get_db()
        cursor = db.execute("""
            INSERT INTO items (name, description, category, price, quantity)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data['name'],
            data.get('description'),
            data.get('category'),
            data.get('price'),
            data.get('quantity', 0)
        ))
        
        db.commit()
        item_id = cursor.lastrowid
        
        # Return the created item
        cursor = db.execute('SELECT * FROM items WHERE id = ?', (item_id,))
        item = dict_from_row(cursor.fetchone())
        
        logger.info(f"Created item with ID: {item_id}")
        return jsonify({'message': 'Item created successfully', 'item': item}), 201
        
    except Exception as e:
        logger.error(f"Error creating item: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    """Update an existing item"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Check if item exists
        db = get_db()
        cursor = db.execute('SELECT * FROM items WHERE id = ?', (item_id,))
        existing_item = cursor.fetchone()
        
        if existing_item is None:
            return jsonify({'error': 'Item not found'}), 404
        
        # Validate data
        errors = validate_item_data(data)
        if errors:
            return jsonify({'error': 'Validation failed', 'details': errors}), 400
        
        # Build update query dynamically
        update_fields = []
        params = []
        
        for field in ['name', 'description', 'category', 'price', 'quantity']:
            if field in data:
                update_fields.append(f'{field} = ?')
                params.append(data[field])
        
        if not update_fields:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        params.append(item_id)
        query = f'UPDATE items SET {", ".join(update_fields)} WHERE id = ?'
        
        db.execute(query, params)
        db.commit()
        
        # Return updated item
        cursor = db.execute('SELECT * FROM items WHERE id = ?', (item_id,))
        item = dict_from_row(cursor.fetchone())
        
        logger.info(f"Updated item with ID: {item_id}")
        return jsonify({'message': 'Item updated successfully', 'item': item})
        
    except Exception as e:
        logger.error(f"Error updating item {item_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """Delete an item"""
    try:
        db = get_db()
        
        # Check if item exists
        cursor = db.execute('SELECT * FROM items WHERE id = ?', (item_id,))
        item = cursor.fetchone()
        
        if item is None:
            return jsonify({'error': 'Item not found'}), 404
        
        # Delete the item
        db.execute('DELETE FROM items WHERE id = ?', (item_id,))
        db.commit()
        
        logger.info(f"Deleted item with ID: {item_id}")
        return jsonify({'message': 'Item deleted successfully'})
        
    except Exception as e:
        logger.error(f"Error deleting item {item_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/items/categories', methods=['GET'])
def get_categories():
    """Get all unique categories"""
    try:
        db = get_db()
        cursor = db.execute('SELECT DISTINCT category FROM items WHERE category IS NOT NULL ORDER BY category')
        categories = [row[0] for row in cursor.fetchall()]
        
        return jsonify({'categories': categories})
        
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({'error': 'Method not allowed'}), 405

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Flask CRUD API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)