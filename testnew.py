import json
import os
import uuid
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

PRODUCTS_FILE = "products.json"
ORDERS_FILE = "orders.json"

def load_products():
    if not os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, "w") as f:
            json.dump([
                {"id": str(uuid.uuid4()), "name": "Latte", "price": 4.5},
                {"id": str(uuid.uuid4()), "name": "Cappuccino", "price": 3.75}
            ], f)
    with open(PRODUCTS_FILE, "r") as f:
        return json.load(f)

def save_products(products):
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(products, f, indent=2)

def load_orders():
    if not os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "w") as f:
            json.dump([], f)
    with open(ORDERS_FILE, "r") as f:
        return json.load(f)

def save_orders(orders):
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

def show_error(message):
    popup = Popup(title="Error", content=Label(text=message),
                  size_hint=(0.6, 0.3))
    popup.open()

class POSLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='horizontal', **kwargs)
        self.products = load_products()
        self.orders = load_orders()

        # Compute next transaction number
        self.next_transaction_number = 1
        if self.orders:
            last_txn = max(order["transaction_number"] for order in self.orders if "transaction_number" in order)
            self.next_transaction_number = last_txn + 1

        # Left: product buttons
        self.product_grid = GridLayout(cols=2, spacing=10, size_hint=(0.7, None))
        self.product_grid.bind(minimum_height=self.product_grid.setter('height'))
        self.refresh_products()

        product_scroll = ScrollView(size_hint=(0.7, 1))
        product_scroll.add_widget(self.product_grid)

        # Right: cart, total, admin
        cart_layout = BoxLayout(orientation='vertical', size_hint=(0.3, 1), padding=10)

        self.cart_items = {}  # key: product id, value: {'product': product, 'quantity': int}

        self.cart_list = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.cart_list.bind(minimum_height=self.cart_list.setter('height'))

        cart_scroll = ScrollView(size_hint=(1, 0.6))
        cart_scroll.add_widget(self.cart_list)

        # Running total label
        self.total_label = Label(text="Total: $0.00", font_size=24, size_hint=(1, 0.1))

        # Buttons
        total_btn = Button(text="Checkout", size_hint=(1, 0.1), on_press=self.show_total)
        clear_btn = Button(text="Clear Cart", size_hint=(1, 0.1), on_press=self.confirm_clear_cart)
        admin_btn = Button(text="Admin", size_hint=(1, 0.1), on_press=self.open_admin_menu)

        cart_layout.add_widget(cart_scroll)
        cart_layout.add_widget(self.total_label)
        cart_layout.add_widget(total_btn)
        cart_layout.add_widget(clear_btn)
        cart_layout.add_widget(admin_btn)

        self.add_widget(product_scroll)
        self.add_widget(cart_layout)

    def refresh_products(self):
        self.product_grid.clear_widgets()
        for p in self.products:
            btn = Button(text=f"{p['name']}\n${p['price']:.2f}",
                         font_size=24, size_hint_y=None, height=120)
            btn.bind(on_press=lambda instance, item=p: self.add_to_cart(item))
            self.product_grid.add_widget(btn)

    def add_to_cart(self, product):
        pid = product["id"]
        if pid in self.cart_items:
            self.cart_items[pid]['quantity'] += 1
        else:
            self.cart_items[pid] = {'product': product, 'quantity': 1}
        self.refresh_cart()
    
    def refresh_cart(self):
        self.cart_list.clear_widgets()
        total = 0
        for pid, item in self.cart_items.items():
            prod = item['product']
            qty = item['quantity']
            price = prod['price'] * qty
            total += price
            btn = Button(
                text=f"{prod['name']} x{qty} - ${price:.2f}",
                size_hint_y=None,
                height=40,
                font_size=20
            )
            btn.bind(on_press=lambda instance, p=pid: self.remove_one_from_cart(p))
            self.cart_list.add_widget(btn)
        self.total_label.text = f"Total: ${total:.2f}"

    def remove_one_from_cart(self, product_id):
        if product_id in self.cart_items:
            self.cart_items[product_id]['quantity'] -= 1
            if self.cart_items[product_id]['quantity'] <= 0:
                del self.cart_items[product_id]
            self.refresh_cart()

    def show_total(self, instance):
        total = sum(item['product']['price'] * item['quantity'] for item in self.cart_items.values())
        if total == 0:
            show_error("Cart is empty!")
            return

        txn_number = self.next_transaction_number
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save order
        order_details = {
            "transaction_number": txn_number,
            "timestamp": timestamp,
            "items": [
                {"id": item['product']['id'], "name": item['product']['name'], "quantity": item['quantity'], "unit_price": item['product']['price']}
                for item in self.cart_items.values()
            ],
            "total": total
        }
        self.orders.append(order_details)
        save_orders(self.orders)
        self.next_transaction_number += 1

        popup = Popup(
            title=f"Total - Transaction #{txn_number}",
            content=Label(text=f"Total: ${total:.2f}\nTransaction #: {txn_number}"),
            size_hint=(0.5, 0.4)
        )

        def on_dismiss(instance):
            # Clear the cart after total is acknowledged
            self.cart_items.clear()
            self.refresh_cart()

        popup.bind(on_dismiss=on_dismiss)
        popup.open()

    def confirm_clear_cart(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(Label(text="Are you sure you want to clear the cart?"))
        btn_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        yes_btn = Button(text="Yes")
        no_btn = Button(text="No")
        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        content.add_widget(btn_layout)

        popup = Popup(title="Confirm Clear Cart", content=content,
                      size_hint=(0.5, 0.4))

        yes_btn.bind(on_press=lambda x: self.clear_cart_and_close(popup))
        no_btn.bind(on_press=popup.dismiss)

        popup.open()

    def clear_cart_and_close(self, popup):
        self.cart_items.clear()
        self.refresh_cart()
        popup.dismiss()

    def open_admin_menu(self, instance):
        popup = AdminSubMenu(self)
        popup.open()

# AdminSubMenu and AdminPopup unchanged — same as before with product remove button added

class AdminSubMenu(Popup):
    def __init__(self, pos_app, **kwargs):
        super().__init__(title="Admin Menu", size_hint=(0.6, 0.4), **kwargs)
        self.pos_app = pos_app
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        edit_btn = Button(text="Edit Products", size_hint=(1, 0.5))
        edit_btn.bind(on_press=self.open_edit)

        exit_btn = Button(text="Exit App", size_hint=(1, 0.5))
        exit_btn.bind(on_press=self.confirm_exit)

        layout.add_widget(edit_btn)
        layout.add_widget(exit_btn)
        self.content = layout

    def open_edit(self, instance):
        self.dismiss()
        popup = AdminPopup(self.pos_app)
        popup.open()

    def confirm_exit(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(Label(text="Are you sure you want to exit the app?"))
        btn_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        yes_btn = Button(text="Yes")
        no_btn = Button(text="No")
        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        content.add_widget(btn_layout)

        popup = Popup(title="Confirm Exit", content=content,
                      size_hint=(0.5, 0.4))

        yes_btn.bind(on_press=lambda x: App.get_running_app().stop())
        yes_btn.bind(on_press=popup.dismiss)
        no_btn.bind(on_press=popup.dismiss)

        popup.open()

class AdminPopup(Popup):
    def __init__(self, pos_app, **kwargs):
        super().__init__(title="Edit Products", size_hint=(0.9, 0.9), **kwargs)
        self.pos_app = pos_app
        self.products = pos_app.products

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        self.grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))

        for product in self.products:
            self.add_product_row(product)

        scroll = ScrollView(size_hint=(1, 0.8))
        scroll.add_widget(self.grid)

        add_btn = Button(text="Add New Product", size_hint=(1, 0.1), on_press=self.add_blank_row)
        save_btn = Button(text="Save Changes", size_hint=(1, 0.1), on_press=self.save_changes)

        layout.add_widget(scroll)
        layout.add_widget(add_btn)
        layout.add_widget(save_btn)
        self.content = layout

    def add_product_row(self, product=None):
        row = BoxLayout(size_hint_y=None, height=40)

        name_input = TextInput(text=product["name"] if product else "", multiline=False)
        price_input = TextInput(text=str(product["price"]) if product else "", multiline=False, input_filter='float')

        remove_btn = Button(text="Remove", size_hint_x=None, width=80)
        remove_btn.bind(on_press=lambda btn: self.remove_row(row))

        row.add_widget(name_input)
        row.add_widget(price_input)
        row.add_widget(remove_btn)

        self.grid.add_widget(row)

    def add_blank_row(self, instance):
        self.add_product_row()

    def remove_row(self, row):
        if row in self.grid.children:
            self.grid.remove_widget(row)

    def save_changes(self, instance):
        new_products = []
        for row in self.grid.children[::-1]:  # top to bottom
            children = row.children
            # children order: [remove_btn, price_input, name_input]
            name_input = children[2]
            price_input = children[1]

            name = name_input.text.strip()
            price_text = price_input.text.strip()

            if name and price_text:
                try:
                    price = float(price_text)
                    product_id = str(uuid.uuid4())
                    new_products.append({"id": product_id, "name": name, "price": price})
                except ValueError:
                    show_error(f"Invalid price: {price_text}")
                    return
            else:
                show_error("Name and price must not be empty.")
                return

        save_products(new_products)
        self.pos_app.products = new_products
        self.pos_app.refresh_products()
        self.dismiss()

class POSApp(App):
    def build(self):
        return POSLayout()

if __name__ == "__main__":
    POSApp().run()