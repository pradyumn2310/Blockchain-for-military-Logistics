import hashlib
import json
import time
import random
from flask import Flask, render_template, jsonify


class User:
    def __init__(self, username, password, role, permissions):
        self.username = username
        self.password = hashlib.sha256(password.encode()).hexdigest()
        self.role = role
        self.permissions = permissions
        self.atm_card_details = None  # Added attribute for ATM card details


class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.create_block(proof=1, previous_hash='0')

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.last_block['index'] + 1

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def is_chain_valid(self):
        previous_block = self.chain[0]
        index = 1
        while index < len(self.chain):
            block = self.chain[index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            if not self.valid_proof(previous_block['proof'], block['proof']):
                return False
            previous_block = block
            index += 1
        return True


class MilitaryLogisticsSystem:
    def __init__(self):
        self.users = []
        self.blockchain = Blockchain()
        self.inventory = self.initialize_inventory()
        self.app = Flask(__name__)
        self.register_routes()
        self.register_admin()
        self.login_prompt()

    def register_routes(self):
        @self.app.route('/')
        def home():
            warehouse_locations = [
                {"name": "Warehouse Mumbai", "lat": 19.0760, "lng": 72.8777, "content": "This is Warehouse Mumbai"},
                # Mumbai
                {"name": "Warehouse Shimla", "lat": 31.1048, "lng": 77.1734, "content": "This is Warehouse Shimla"},
                # Shimla
                {"name": "Warehouse Bhopal", "lat": 23.2599, "lng": 77.4126, "content": "This is Warehouse Bhopal"},
                # Bhopal
                {"name": "Warehouse Tamil Nadu", "lat": 11.1271, "lng": 78.6569,
                 "content": "This is Warehouse Tamil Nadu"},
                # Tamil Nadu
                {"name": "Warehouse Assam", "lat": 26.2006, "lng": 92.9376, "content": "This is Warehouse Assam"}
                # Assam
            ]
            return render_template('warehouses.html', locations=warehouse_locations)

        @self.app.route('/routes')
        def routes():
            return render_template('routes.html')

    def register_admin(self):
        print("=== Admin Registration ===")
        username = input("Enter admin username: ")
        password = input("Enter admin password: ")
        admin = User(username, password, 'admin',
                     permissions={'routes': True, 'warehouse': True, 'inventory': True, 'resources': True,
                                  'atm_details': True})
        self.users.append(admin)
        print("Admin registered successfully!")
        self.register_initial_users()

    def register_initial_users(self):
        while True:
            print("\n=== Initial User Registration ===")
            username = input("Enter username: ")
            password = input("Enter password: ")
            permissions = self.assign_permissions()
            user = User(username, password, 'user', permissions)
            self.users.append(user)
            print("User registered successfully!")
            more_users = input("Do you want to add another user? (yes/no): ")
            if more_users.lower() != 'yes':
                break

    def assign_permissions(self):
        permissions = {'routes': False, 'warehouse': False, 'inventory': False, 'resources': False,
                       'atm_details': False}
        for permission in permissions.keys():
            response = input(f"Grant access to {permission.replace('_', ' ')}? (y/n): ")
            if response.lower() == 'y':
                permissions[permission] = True
        return permissions

    def register_user(self):
        print("\n=== User Registration ===")
        username = input("Enter username: ")
        password = input("Enter password: ")
        permissions = self.assign_permissions()
        user = User(username, password, 'user', permissions)
        self.users.append(user)
        print("User registered successfully!")

    def login(self):
        username = input("Enter username: ")
        password = hashlib.sha256(input("Enter password: ").encode()).hexdigest()
        for user in self.users:
            if user.username == username and user.password == password:
                print("Login successful!")
                return user
        print("Invalid username or password!")
        return None

    def login_prompt(self):
        print("\n=== Login ===")
        while True:
            user = self.login()
            if user:
                if user.role == 'admin':
                    self.display_admin_menu(user)
                else:
                    self.display_user_menu(user)
                break

    def initialize_inventory(self):
        return {
            "guns": 100,
            "grenades": 200,
            "missiles": 50,
            "tanks": 10,
            "rocket_launchers": 30,
            "jets": 50
        }

    def view_inventory(self, user):
        if user.permissions['inventory']:
            print("\nCurrent Inventory:")
            for item, quantity in self.inventory.items():
                print(f"{item.capitalize()}: {quantity}")
        else:
            print("You do not have permission to view the inventory.")

    def edit_inventory(self, user):
        if user.permissions['inventory']:
            print("\nEdit Inventory:")
            for index, item in enumerate(self.inventory.keys(), start=1):
                print(f"{index}. {item.capitalize()}")
            choice = int(input("Select an item to edit (by number): "))
            item_to_edit = list(self.inventory.keys())[choice - 1]
            new_quantity = int(input(f"Enter new quantity for {item_to_edit.capitalize()}: "))
            self.inventory[item_to_edit] = new_quantity
            print(f"Updated {item_to_edit.capitalize()} quantity to {new_quantity}")
        else:
            print("You do not have permission to edit the inventory.")

    def display_main_menu(self, user):
        print("\nMain Menu:")
        if user.role == 'admin':
            print("1. Add User")
        if user.permissions['routes']:
            print("2. Routes")
        if user.permissions['warehouse']:
            print("3. Warehouse")
        if user.permissions['inventory']:
            print("4. Inventory")
        if user.permissions['resources']:
            print("5. Resources")
        if user.permissions['atm_details']:
            print("6. ATM Card Details")
        print("7. Logout")

    def display_inventory_menu(self, user):
        while True:
            print("\nInventory Menu:")
            print("1. View Inventory")
            print("2. Edit Inventory")
            print("3. Back to Main Menu")
            choice = input("Enter your choice: ")
            if choice == '1':
                self.view_inventory(user)
            elif choice == '2':
                self.edit_inventory(user)
            elif choice == '3':
                break
            else:
                print("Invalid choice!")

    def display_admin_menu(self, admin):
        print("Welcome, Admin", admin.username)
        while True:
            self.display_main_menu(admin)
            choice = input("Enter your choice: ")
            if choice == '1':
                self.register_user()
            elif choice == '2' and admin.permissions['routes']:
                print("Routes functionality")
            elif choice == '3' and admin.permissions['warehouse']:
                self.show_warehouse_locations()
            elif choice == '4' and admin.permissions['inventory']:
                self.display_inventory_menu(admin)
            elif choice == '5' and admin.permissions['resources']:
                self.resources_show()
            elif choice == '6' and admin.permissions['atm_details']:
                self.atm_card_menu(admin)
            elif choice == '7':
                print("Logging out...")
                return  # Return to main menu
            else:
                print("Invalid choice or you do not have permission for this action!")

    def display_user_menu(self, user):
     print("Welcome, User", user.username)
     while True:
        self.display_main_menu(user)
        print("8. Attempt Attack")  # Option for the attacker to attempt an attack
        choice = input("Enter your choice: ")
        if choice == '2' and user.permissions['routes']:
            self.show_routes_locations()
        elif choice == '3' and user.permissions['warehouse']:
            self.show_warehouse_locations()
        elif choice == '4' and user.permissions['inventory']:
            self.display_inventory_menu(user)
        elif choice == '5' and user.permissions['resources']:
            self.resources_show()
        elif choice == '6' and user.permissions['atm_details']:
            self.atm_card_menu(user)
        elif choice == '7':
            print("Logging out...")
            return  # Return to main menu
        elif choice == '8':  # Option for the attacker to attempt an attack
            self.attempt_attack()
        else:
            print("Invalid choice or you do not have permission for this action!")

    def atm_card_menu(self, user):
        if user.permissions['atm_details']:
            print("\nATM Card Menu:")
            print("1. Add Card Details")
            print("2. Check Card Details")
            choice = input("Enter your choice: ")
            if choice == '1':
                self.add_card_details(user)
            elif choice == '2':
                self.check_card_details(user)
            else:
                print("Invalid choice!")
        else:
            print("You do not have permission to access ATM card details.")

    def add_card_details(self, user):
        if user.permissions['atm_details']:
            card_number = input("Enter card number: ")
            expiry_date = input("Enter expiry date (MM/YYYY): ")
            cvv = input("Enter CVV: ")
            user.atm_card_details = {  # Save card details to user object
                'card_number': card_number,
                'expiry_date': expiry_date,
                'cvv': cvv
            }
            print("Card details added successfully!")
        else:
            print("You do not have permission to add card details.")

    def check_card_details(self, user):
        if user.permissions['atm_details']:
            if user.atm_card_details:  # Check if card details are available
                print("Card Number:", user.atm_card_details['card_number'])
                print("Expiry Date:", user.atm_card_details['expiry_date'])
                print("CVV:", user.atm_card_details['cvv'])
            else:
                print("No card details available.")
        else:
            print("You do not have permission to check card details.")

    def check_registered_users(self, admin):
        if admin.role == 'admin':
            print("\nRegistered Users:")
            for user in self.users:
                if user.role == 'user':
                    print(user.username)
        else:
            print("You do not have permission to check registered users.")

    def show_warehouse_locations(self):
        print("Open the following URL in a web browser to see the warehouse locations:")
        print("http://127.0.0.1:5500/final/test_1.html")

    def show_routes_locations(self):
        print("Open the following URL in a web browser to see the warehouse locations:")
        print("http://127.0.0.1:5500/final/routes.html")

    def attempt_attack(self):
        print("Initiating attack...")
        print("Attacker is attempting to obtain user credentials...")
        loading_duration = random.randint(5, 10)  # Simulate loading time
        for _ in range(loading_duration):
            time.sleep(1)
            print(".", end="", flush=True)  # Print dots to simulate loading
        print("\nAttack successful! User credentials obtained.")
        print("Username: admin")
        print("Password: password123")
        for user in self.users:
            if user.role == 'user':
                print(f"Username: {user.username}")
                print("Password: [Hidden]")
        print("Attack completed.")

    def run_server(self):
        self.app.run(debug=True)

    def resources_show(self):
        print("Shivansh:980577715")
        print("Pradyumn:7807423021")
        print("Abhi:780744556")
        print("Pranav:7017100269")
        print("Shruti:788845784")


# Start the logistics system
if __name__ == '__main__':

    logistics_system = MilitaryLogisticsSystem()
    logistics_system.run_server()