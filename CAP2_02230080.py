################################
# Your Name: Tandin Wangchuk
# Your Section: 1 electrical
# Your Student ID Number:02230080
################################
# REFERENCES
#https://youtu.be/ZDa-Z5JzLYM?list=PL-osiE80TeTsqhIuOqKhwlXsIBIdSeYtc
#https://youtu.be/BJ-VvGyQxho?list=PL-osiE80TeTsqhIuOqKhwlXsIBIdSeYtc
#https://youtu.be/rq8cL2XMM5M?list=PL-osiE80TeTsqhIuOqKhwlXsIBIdSeYtc
#https://youtu.be/RSl87lqOXDE?list=PL-osiE80TeTsqhIuOqKhwlXsIBIdSeYtc

import os
import random
import hashlib
import base64
import string

#creating account
class Account:
    def __init__(self, account_number, password, account_type, salt=None, balance=0.0):
        self.account_number = account_number
        self.salt = salt or base64.b64encode(os.urandom(16)).decode('utf-8')
        self.password_hash = self.hash_password(password, self.salt)
        self.account_type = account_type
        self.balance = balance

    #hash password
    def hash_password(self, password, salt):
        """Hashes the password with the given salt."""
        return hashlib.sha256((salt + password).encode()).hexdigest()

    #check password
    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        return self.hash_password(password, self.salt) == self.password_hash

    #for deposit
    def deposit(self, amount):
        """Deposits the given amount into the account."""
        self.balance += amount
        return self.balance

    #for withdraw
    def withdraw(self, amount):
        """Withdraws the given amount from the account if sufficient funds are available."""
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        return self.balance

    def __str__(self):
        """Returns a string representation of the account."""
        return f"Account Number: {self.account_number}, Type: {self.account_type}, Balance: {self.balance:.2f}"

    def save_to_file(self, filename="accounts.txt"):
        """Saves the account details to a file."""
        try:
            with open(filename, "a") as file:
                file.write(f"{self.account_number},{self.salt},{self.password_hash},{self.account_type},{self.balance}\n")
        except IOError as e:
            print(f"Error saving account to file: {e}")

class PersonalAccount(Account):
    def __init__(self, account_number, password, salt=None, balance=0.0):
        super().__init__(account_number, password, "Personal", salt, balance)

class BusinessAccount(Account):
    def __init__(self, account_number, password, salt=None, balance=0.0):
        super().__init__(account_number, password, "Business", salt, balance)

class Bank:
    def __init__(self, accounts_file="accounts.txt"):
        self.accounts_file = accounts_file
        self.accounts = self.load_accounts()

    def load_accounts(self):
        """Loads accounts from the file into a dictionary."""
        accounts = {}
        if os.path.exists(self.accounts_file):
            try:
                with open(self.accounts_file, "r") as file:
                    for line in file:
                        account_number, salt, password_hash, account_type, balance = line.strip().split(",")
                        balance = float(balance)
                        if account_type == "Personal":
                            account = PersonalAccount(account_number, password_hash, salt, balance)
                        else:
                            account = BusinessAccount(account_number, password_hash, salt, balance)
                        accounts[account_number] = account
            except IOError as e:
                print(f"Error loading accounts from file: {e}")
        return accounts

    def save_account(self, account):
        """Saves or updates an account in the file."""
        if os.path.exists(self.accounts_file):
            try:
                with open(self.accounts_file, "r") as file:
                    lines = file.readlines()
                with open(self.accounts_file, "w") as file:
                    for line in lines:
                        if not line.startswith(account.account_number):
                            file.write(line)
            except IOError as e:
                print(f"Error updating account in file: {e}")
        account.save_to_file(self.accounts_file)

    def generate_password(self, length=12):
        """Generates a random password of the specified length."""
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(characters) for _ in range(length))
        return password

    def create_account(self, account_type):
        """Creates a new account with a random account number and generated password."""
        account_number = str(random.randint(10000, 99999))
        password = self.generate_password()
        account_type = account_type.lower()
        if account_type == "personal":
            account = PersonalAccount(account_number, password)
        elif account_type == "business":
            account = BusinessAccount(account_number, password)
        else:
            raise ValueError("Invalid account type")
        self.accounts[account_number] = account
        self.save_account(account)
        return account, password

    def login(self, account_number, password):
        """Logs in to the account with the provided account number and password."""
        account = self.accounts.get(account_number)
        if account and account.check_password(password):
            return account
        else:
            raise ValueError("Invalid account number or password")

    def transfer(self, from_account, to_account_number, amount):
        """Transfers the given amount from one account to another."""
        to_account = self.accounts.get(to_account_number)
        if not to_account:
            raise ValueError("Receiving account does not exist")
        from_account.withdraw(amount)
        to_account.deposit(amount)
        self.save_account(from_account)
        self.save_account(to_account)

def main():
    bank = Bank()
    print("Welcome to Bank of bhutan ")

    while True:
        print("\n1. Open Account\n2. Login\n3. Exit")
        user_choice = input("Enter your choice: ")

        if user_choice == '1':
            account_type = input("Enter account type (personal/business): ").lower()
            try:
                account, password = bank.create_account(account_type)
                print(f"Account created successfully. Your account number is {account.account_number}")
                print(f"Your generated password is: {password}")
            except ValueError as e:
                print(e)

        elif user_choice == '2':
            account_number = input("Enter your account number: ")
            password = input("Enter your password: ")
            try:
                account = bank.login(account_number, password)
                print(f"Welcome, {account.account_type} account holder!")
                while True:
                    print("\n1. Check Balance\n2. Deposit\n3. Withdraw\n4. Transfer\n5. Logout")
                    action_choice = input("Enter your choice: ")

                    if action_choice == '1':
                        print(f"Your balance is: {account.balance:.2f}")

                    elif action_choice == '2':
                        amount = float(input("Enter amount to deposit: "))
                        account.deposit(amount)
                        bank.save_account(account)
                        print(f"Deposited successfully. New balance: {account.balance:.2f}")

                    elif action_choice == '3':
                        amount = float(input("Enter amount to withdraw: "))
                        try:
                            account.withdraw(amount)
                            bank.save_account(account)
                            print(f"Withdrawn successfully. New balance: {account.balance:.2f}")
                        except ValueError as e:
                            print(e)

                    elif action_choice == '4':
                        to_account_number = input("Enter account number to transfer to: ")
                        amount = float(input("Enter amount to transfer: "))
                        try:
                            bank.transfer(account, to_account_number, amount)
                            print(f"Transferred successfully. New balance: {account.balance:.2f}")
                        except ValueError as e:
                            print(e)

                    elif action_choice == '5':
                        print("Logged out successfully.")
                        break

                    else:
                        print("Invalid choice. Please try again.")

            except ValueError as e:
                print(e)

        elif user_choice == '3':
            print("Thank you for using bank of bhutan")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
