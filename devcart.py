import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)
DB_FILE = "cart.db"


def init_db():
    """Initializes the database and seeds dummy products."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        # Create Products table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL
            )
        """
        )
        # Create Cart table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cart (
                product_id INTEGER PRIMARY KEY,
                quantity INTEGER NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        """
        )
        # Seed dummy products if table is empty
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO products (name, price) VALUES (?, ?)",
                [("Laptop", 999.99), ("Mouse", 25.50), ("Keyboard", 75.00)],
            )
        conn.commit()


def get_db_connection():
    """Helper to connect to the database with row factory enabled."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/cart", methods=["GET"])
def get_cart():
    """Retrieves all items in the cart with product details and totals."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT p.id, p.name, p.price, c.quantity 
        FROM cart c 
        JOIN products p ON c.product_id = p.id
    """
    )
    items = [dict(row) for row in cursor.fetchall()]

    # Calculate cart summary
    total_items = sum(item["quantity"] for item in items)
    total_price = sum(item["price"] * item["quantity"] for item in items)

    conn.close()
    return jsonify(
        {"items": items, "total_items": total_items, "total_price": total_price}
    )


@app.route("/cart", methods=["POST"])
def add_to_cart():
    """Adds an item to the cart or increments its quantity."""
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    if not product_id:
        return jsonify({"error": "Missing product_id"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if product exists in database
    cursor.execute("SELECT id FROM products WHERE id = ?", (product_id,))
    if not cursor.fetchone():
        return jsonify({"error": "Product not found"}), 44
        conn.close()

    # Insert or update quantity if item already exists
    cursor.execute(
        """
        INSERT INTO cart (product_id, quantity) 
        VALUES (?, ?) 
        ON CONFLICT(product_id) DO UPDATE SET quantity = quantity + excluded.quantity
    """,
        (product_id, quantity),
    )

    conn.commit()
    conn.close()
    return jsonify({"message": "Item added to cart successfully"}), 200


@app.route("/cart/<int:product_id>", methods=["PUT"])
def update_cart_quantity(product_id):
    """Updates the specific quantity of an item in the cart."""
    data = request.get_json()
    quantity = data.get("quantity")

    if quantity is None or quantity < 1:
        return jsonify({"error": "Quantity must be 1 or greater"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE cart SET quantity = ? WHERE product_id = ?",
        (quantity, product_id),
    )
    if cursor.rowcount == 0:
        return jsonify({"error": "Item not in cart"}), 404

    conn.commit()
    conn.close()
    return jsonify({"message": "Cart updated successfully"}), 200


@app.route("/cart/<int:product_id>", methods=["DELETE"])
def remove_from_cart(product_id):
    """Removes an item completely from the cart."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM cart WHERE product_id = ?", (product_id,))
    if cursor.rowcount == 0:
        return jsonify({"error": "Item not in cart"}), 404

    conn.commit()
    conn.close()
    return jsonify({"message": "Item removed from cart"}), 200


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
