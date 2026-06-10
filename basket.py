class Item:
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price

class ShoppingCart:
    def __init__(self):
        self.items = {}  # Stores item_name: {"item": Item, "quantity": int}

    def add_item(self, item: Item, quantity: int = 1):
        """Adds an item to the cart or updates its quantity if it exists."""
        if quantity <= 0:
            print("Quantity must be greater than 0.")
            return
        
        if item.name in self.items:
            self.items[item.name]["quantity"] += quantity
        else:
            self.items[item.name] = {"item": item, "quantity": quantity}
        print(f"Added {quantity}x '{item.name}' to the cart.")

    def remove_item(self, item_name: str, quantity: int = None):
        """Removes an item completely, or reduces its quantity."""
        if item_name not in self.items:
            print(f"'{item_name}' is not in your cart.")
            return

        if quantity is None or quantity >= self.items[item_name]["quantity"]:
            del self.items[item_name]
            print(f"Removed '{item_name}' completely from the cart.")
        else:
            self.items[item_name]["quantity"] -= quantity
            print(f"Reduced '{item_name}' quantity by {quantity}.")

    def calculate_total(self) -> float:
        """Calculates the total price of all items currently in the cart."""
        return sum(details["item"].price * details["quantity"] for details in self.items.values())

    def display_receipt(self):
        """Prints a clean, formatted receipt layout of the cart items."""
        if not self.items:
            print("\nYour shopping cart is empty.")
            return

        print("\n" + "="*40)
        print(f"{'SHOPPING CART RECEIPT':^40}")
        print("="*40)
        print(f"{'Item':<20}{'Qty':<5}{'Price':<8}{'Total':<7}")
        print("-"*40)
        
        for details in self.items.values():
            item = details["item"]
            qty = details["quantity"]
            item_total = item.price * qty
            print(f"{item.name:<20}{qty:<5}${item.price:<7.2f}${item_total:<7.2f}")
            
        print("-"*40)
        print(f"{'SUBTOTAL:':<32}${self.calculate_total():.2f}")
        print("="*40 + "\n")

# --- Example Execution Usage ---
if __name__ == "__main__":
    # Create inventory products
    laptop = Item("Gaming Laptop", 1200.00)
    mouse = Item("Wireless Mouse", 25.50)
    keyboard = Item("Mechanical Keyboard", 85.00)

    # Initialize the user's shopping session
    cart = ShoppingCart()

    # Perform typical ecommerce checkout actions
    cart.add_item(laptop, 1)
    cart.add_item(mouse, 2)
    cart.add_item(keyboard, 1)
    
    # Show initial receipt state
    cart.display_receipt()

    # Modify items (user removes one mouse)
    cart.remove_item("Wireless Mouse", 1)
    
    # Show updated receipt state
    cart.display_receipt()
