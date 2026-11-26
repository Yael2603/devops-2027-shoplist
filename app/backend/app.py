from flask import Flask, jsonify, request
import psycopg2
import os

app = Flask(__name__)

CATEGORIES = ['Produce', 'Dairy', 'Bakery', 'Pantry', 'Household', 'Other']
COLUMNS = 'id, name, price, quantity, category, bought'


def get_db():
    return psycopg2.connect(
        host=os.environ['DB_HOST'],
        database=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD']
    )


def to_json(row):
    return {
        'id': row[0],
        'name': row[1],
        'price': float(row[2]),
        'quantity': row[3],
        'category': row[4],
        'bought': row[5]
    }


@app.route('/health')
def health():
    return jsonify({'status': 'ok'})


@app.route('/categories')
def get_categories():
    return jsonify(CATEGORIES)


@app.route('/products', methods=['GET'])
def get_products():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f'SELECT {COLUMNS} FROM products ORDER BY id')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([to_json(r) for r in rows])


@app.route('/products', methods=['POST'])
def add_product():
    data = request.get_json() or {}
    name = str(data.get('name', '')).strip()
    if not name:
        return jsonify({'error': 'name is required'}), 400
    try:
        price = float(data['price'])
        quantity = int(data.get('quantity', 1))
    except (KeyError, TypeError, ValueError):
        return jsonify({'error': 'price and quantity must be numbers'}), 400
    category = data.get('category', 'Other')
    if category not in CATEGORIES:
        category = 'Other'

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        f'INSERT INTO products (name, price, quantity, category) '
        f'VALUES (%s, %s, %s, %s) RETURNING {COLUMNS}',
        (name, price, quantity, category)
    )
    product = to_json(cur.fetchone())
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(product), 201


# Change part of a product: any of name, price, quantity, category, bought.
# Example: {"bought": true}  or  {"name": "Oat milk", "price": 6.5}
@app.route('/products/<int:product_id>', methods=['PATCH'])
def update_product(product_id):
    data = request.get_json() or {}
    changes = {}
    try:
        if 'name' in data:
            name = str(data['name']).strip()
            if not name:
                return jsonify({'error': 'name cannot be empty'}), 400
            changes['name'] = name[:100]
        if 'price' in data:
            changes['price'] = max(0, float(data['price']))
        if 'quantity' in data:
            changes['quantity'] = max(1, int(data['quantity']))
    except (TypeError, ValueError):
        return jsonify({'error': 'price and quantity must be numbers'}), 400
    if 'category' in data:
        changes['category'] = data['category'] if data['category'] in CATEGORIES else 'Other'
    if 'bought' in data:
        changes['bought'] = bool(data['bought'])
    if not changes:
        return jsonify({'error': 'nothing to update'}), 400

    sets = ', '.join(f'{column} = %s' for column in changes)
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        f'UPDATE products SET {sets} WHERE id = %s RETURNING {COLUMNS}',
        (*changes.values(), product_id)
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if row is None:
        return jsonify({'error': 'not found'}), 404
    return jsonify(to_json(row))


@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM products WHERE id = %s', (product_id,))
    conn.commit()
    cur.close()
    conn.close()
    return '', 204


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
