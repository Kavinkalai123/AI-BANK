#banking 2
import json
import os
from datetime import datetime

# ---------------------------------------
# 📁 Database File Name
# ---------------------------------------
DB_FILE = "data.json"

# ---------------------------------------
# 🧠 Step 1: Load or Initialize Database
# ---------------------------------------
def load_database():
    """Load existing data.json file or create new one."""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    else:
        data = {
            "customers": [],
            "accounts": [],
            "transactions": [],
            "last_account_number": 99  # Start before 100 (next = 100)
        }
        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=4)
        return data


def save_database(data):
    """Save updated data to data.json."""
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4, default=str)


# Global variable — loaded once at start
DATABASE = load_database()

# ---------------------------------------
# 👤 Customer Class
# ---------------------------------------
class Customer:
    """Represents a customer with name and age."""

    def __init__(self, name, age):
        self.name = name
        self.age = age
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        """Convert customer object to dictionary for saving."""
        return {
            "name": self.name,
            "age": self.age,
            "created_at": self.created_at
        }


# ---------------------------------------
# 💳 BankAccount Class
# ---------------------------------------
class BankAccount:
    """Handles all account operations like deposit, withdraw, etc."""

    def __init__(self, customer, account_number, password, balance=0,mpin=None):
        self.customer = customer
        self.account_number = account_number
        self.password = password
        self.balance = balance
        self.mpin = mpin
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        """Convert account object to dictionary for saving."""
        return {
            "customer_name": self.customer.name,
            "account_number": self.account_number,
            "password": self.password,
            "balance": self.balance,
            "mpin" : self.mpin,
            "created_at": self.created_at,
        }

    def deposit(self, amount):
        """Add amount to balance."""
        self.balance += amount
        self._record_transaction("deposit", amount)
        print(f"✅ Deposited ₹{amount}. New Balance: ₹{self.balance}")
        self._update_database()

    def withdraw(self, amount):
        """Withdraw money if enough balance available."""
        if amount > self.balance:
            print("❌ Insufficient funds!")
        else:
            self.balance -= amount
            self._record_transaction("withdraw", amount)
            print(f"✅ Withdrawn ₹{amount}. Remaining Balance: ₹{self.balance}")
            self._update_database()

    def check_balance(self):
        """Show current balance."""
        print(f"💰 Current Balance: ₹{self.balance}")

    def calculate_interest(self, rate_percent):
        """Simple interest calculation on current balance."""
        interest = self.balance * (rate_percent / 100)
        print(f"📈 Interest ({rate_percent}%): ₹{round(interest, 2)}")
        return interest

    # ---------------------------
    # 🔒 Internal Utility Methods
    # ---------------------------
    def _record_transaction(self, txn_type, amount):
        """Save transaction entry to database."""
        DATABASE["transactions"].append({
            "type": txn_type,
            "amount": amount,
            "account_number": self.account_number,
            "customer": self.customer.name,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
        save_database(DATABASE)

    def _update_database(self):
        """Update current balance in data.json."""
        for acc in DATABASE["accounts"]:
            if acc["account_number"] == self.account_number:
                acc["balance"] = self.balance
        save_database(DATABASE)

    def money_transfer(self,to_account_number,amount):
        """Transfering money securely using mpin"""
        mpin_input = input("Enter your 4-digit mpin to confirm:")
        
        #verify mpin
        if self.mpin != mpin_input:
            print("Incorrect mpin!Transfer cancelled.")
            return
        if amount <=0:
            print("Invalid amount.")
            return
        if amount > self.balance:
            print("Insufficient fund.")
            return
        # find the recipient accout
        recipient=None
        for acc in DATABASE ["accounts"]:
            if acc ["account_number"]==int(to_account_number):
                recipient=acc
                break
        if not recipient:
            print("Recipient account not found")
            return
        # perform tranfer
        self.balance-=amount
        recipient["balance"] += amount

        #Record transactions for both users
        DATABASE["transactions"].append({
            "type":"transfer_out",
            "amount":amount,
            "from_account":self.account_number,
            "to_account":recipient["account_number"],
            "customer":self.customer.name,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

        DATABASE["transactions"].append({
            "type":"transfer_in",
            "amount":amount,
            "from_account":self.account_number,
            "to_account":recipient["account_number"],
            "customer":recipient["customer_name"],
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
        save_database(DATABASE)
        print(f" ₹{amount} transferred successfully to A/C{to_account_number}")
        print(f"Remaining balance: ₹{self.balance}")
        self._update_database()

           




# ---------------------------------------
# 🏦 Bank Class
# ---------------------------------------
class Bank:
    """Main bank class that handles signup, login, and reporting."""

    def __init__(self, name):
        self.name = name

    def _next_account_number(self):
        """Generate next sequential account number."""
        DATABASE["last_account_number"] += 1
        save_database(DATABASE)
        return DATABASE["last_account_number"]

    def open_account(self, customer, password, initial_deposit,mpin):
        """Create a new bank account for a new customer."""
        account_number = self._next_account_number()
        account = BankAccount(customer, account_number, password, initial_deposit,mpin)

        DATABASE["customers"].append(customer.to_dict())
        DATABASE["accounts"].append(account.to_dict())
        save_database(DATABASE)

        print(f"\n🎉 Account created successfully!")
        print(f"🪪 Account Number: {account_number}")
        print(f"Welcome to {self.name}, {customer.name}!\n")
        return account

    def login(self, account_number, password):
        """Check login credentials and return account object."""
        for acc in DATABASE["accounts"]:
            if acc["account_number"] == int(account_number) and acc["password"] == password:
                # Find the corresponding customer info
                for cust in DATABASE["customers"]:
                    if cust["name"] == acc["customer_name"]:
                        customer = Customer(cust["name"], cust["age"])
                        account = BankAccount(customer, acc["account_number"], acc["password"], acc["balance"],acc.get("mpin"))
                        print(f"\n✅ Login successful! Welcome back, {customer.name}.")
                        return account
        print("❌ Invalid account number or password.")
        return None

    def transaction_summary(self, account_number):
        """Display all transactions for the given account."""
        print("\n📊 Transaction Summary:")
        found = False
        for txn in DATABASE["transactions"]:
            if txn["account_number"] == account_number:
                print(f"- {txn['time']} | {txn['type'].capitalize()} ₹{txn['amount']}")
                found = True
        if not found:
            print("No transactions yet.")
        print()

    def total_bank_balance(self):
        """Show total amount stored in all accounts."""
        total = sum(acc["balance"] for acc in DATABASE["accounts"])
        print(f"🏦 Total Bank Balance in {self.name}: ₹{total}")


# ---------------------------------------
# 💬 User Menus
# ---------------------------------------
def main():
    """Main entry point for user interaction."""
    print("🏦 Welcome to AI Bank 🏦")
    bank = Bank("AI Bank")

    while True:
        print("\n1. Login")
        print("2. Create New Account")
        print("3. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            acc_no = input("Enter account number: ")
            pwd = input("Enter password: ")
            account = bank.login(acc_no, pwd)
            if account:
                atm_menu (bank, account)

        elif choice == "2":
            name = input("Enter your name: ")
            age = int(input("Enter your age: "))
            pwd = input("Set your password: ")
            initial = float(input("Initial deposit amount: ₹"))
            mpin = input("set your 4-digit mpin:")
            customer = Customer(name, age)
            bank.open_account(customer, pwd,initial,mpin)

        elif choice == "3":
            print("👋 Thank you for using AI Bank!")
            bank.total_bank_balance()
            break

        else:
            print("❌ Invalid choice. Try again.")


def atm_menu(bank, account):
    """Customer menu after login (like ATM)."""
    while True:
        print("\nATM Menu:")
        print("1. Deposit")
        print("2. Withdraw")
        print("3. Check Balance")
        print("4. Calculate Interest")
        print("5. View Transactions")
        print("6. Money transfer")
        print("7. Logout")

        choice = input("Select option: ")

        if choice == "1":
            amt = float(input("Enter deposit amount: ₹"))
            account.deposit(amt)
        elif choice == "2":
            amt = float(input("Enter withdraw amount: ₹"))
            account.withdraw(amt)
        elif choice == "3":
            account.check_balance()
        elif choice == "4":
            rate = float(input("Enter interest rate (%): "))
            account.calculate_interest(rate)
        elif choice == "5":
            bank.transaction_summary(account.account_number)
        elif choice == "6":
            to_acc=input("Enter recipient account number:")
            mpin=input("Enter your 4-digit mpin:")
            amt=float(input("Enter amount: ₹"))
            account.money_transfer (to_acc,amt)
        elif choice == "7":
            print(f"👋 Logged out successfully, {account.customer.name}.")
            break
        else:
            print("❌ Invalid option. Try again.")


# ---------------------------------------
# 🚀 Run the Program
# ---------------------------------------
if __name__ == "__main__":
    main ()