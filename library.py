import json
import os
from datetime import datetime, timedelta

DATA_FILE = "library.json"

class Book:
    def __init__(self, title, author, copies=1):
        self.title = title
        self.author = author
        self.copies = copies

    def to_dict(self):
        return {"title": self.title, "author": self.author, "copies": self.copies}

    def __str__(self):
        return f"{self.title} by {self.author} (Copies: {self.copies})"

class Member:
    def __init__(self, name):
        self.name = name
        self.borrowed_books = {}  # book_title : due_date string

    def borrow_book(self, book_title):
        due_date = datetime.now() + timedelta(days=14)
        self.borrowed_books[book_title] = due_date.strftime("%Y-%m-%d")

    def return_book(self, book_title):
        if book_title in self.borrowed_books:
            del self.borrowed_books[book_title]

    def to_dict(self):
        return {"name": self.name, "borrowed_books": self.borrowed_books}

    def __str__(self):
        if self.borrowed_books:
            books = ", ".join([f"{title} (due {due})" for title, due in self.borrowed_books.items()])
        else:
            books = "None"
        return f"{self.name} (Borrowed: {books})"

class Library:
    def __init__(self):
        self.books = []
        self.members = []
        self.load_data()

    def save_data(self):
        data = {
            "books": [b.to_dict() for b in self.books],
            "members": [m.to_dict() for m in self.members]
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                try:
                    data = json.load(f)
                    self.books = [Book(**b) for b in data.get("books", [])]
                    self.members = []
                    for m in data.get("members", []):
                        member = Member(m["name"])
                        member.borrowed_books = m.get("borrowed_books", {})
                        self.members.append(member)
                except json.JSONDecodeError:
                    pass

    def find_book(self, title):
        for book in self.books:
            if book.title.lower() == title.lower():
                return book
        return None

    def find_member(self, name):
        for member in self.members:
            if member.name.lower() == name.lower():
                return member
        return None

    def add_book(self, title, author, copies=1):
        book = self.find_book(title)
        if book:
            book.copies += copies
            print(f"Added {copies} more copies of '{title}'.")
        else:
            self.books.append(Book(title, author, copies))
            print(f"Added new book '{title}'.")
        self.save_data()
        self.print_data()

    def add_member(self, name):
        if self.find_member(name):
            print(f"Member '{name}' already exists.")
            return
        self.members.append(Member(name))
        print(f"Added new member '{name}'.")
        self.save_data()
        self.print_data()

    def borrow_book(self, member_name, book_title):
        member = self.find_member(member_name)
        book = self.find_book(book_title)

        if not member:
            print(f"Member '{member_name}' not found.")
            return
        if not book:
            print(f"Book '{book_title}' not found.")
            return
        if book.copies < 1:
            print(f"No copies of '{book_title}' available.")
            return

        book.copies -= 1
        member.borrow_book(book.title)
        print(f"{member.name} borrowed '{book.title}'. Due in 14 days.")
        self.save_data()
        self.print_data()

    def return_book(self, member_name, book_title):
        member = self.find_member(member_name)
        book = self.find_book(book_title)

        if not member or not book:
            print("Invalid member or book.")
            return

        if book_title not in member.borrowed_books:
            print(f"'{book_title}' is not borrowed by {member_name}.")
            return

        due_date_str = member.borrowed_books[book_title]
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
        days_late = (datetime.now() - due_date).days

        member.return_book(book_title)
        book.copies += 1

        if days_late > 0:
            print(f"Book returned late by {days_late} days! Please return on time next time.")
        else:
            print("Book returned on time. Thank you!")

        self.save_data()
        self.print_data()

    def show_books(self):
        if not self.books:
            print("No books in the library.")
        else:
            for book in self.books:
                print(book)

    def show_members(self):
        if not self.members:
            print("No members found.")
        else:
            for member in self.members:
                print(member)

    def print_data(self):
        print("\nCurrent Library Data:")
        print("Books:")
        for b in self.books:
            print(f" - {b}")
        print("Members:")
        for m in self.members:
            print(f" - {m}")
        print()

def main():
    lib = Library()
    while True:
        print("Library Menu:")
        print("1. Add Book")
        print("2. Add Member")
        print("3. Borrow Book")
        print("4. Return Book")
        print("5. Show Books")
        print("6. Show Members")
        print("7. Exit")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            title = input("Book Title: ")
            author = input("Author: ")
            copies_str = input("Copies (default 1): ").strip()
            copies = int(copies_str) if copies_str.isdigit() else 1
            lib.add_book(title, author, copies)

        elif choice == "2":
            name = input("Member Name: ")
            lib.add_member(name)

        elif choice == "3":
            member_name = input("Member Name: ")
            book_title = input("Book Title: ")
            lib.borrow_book(member_name, book_title)

        elif choice == "4":
            member_name = input("Member Name: ")
            book_title = input("Book Title: ")
            lib.return_book(member_name, book_title)

        elif choice == "5":
            lib.show_books()

        elif choice == "6":
            lib.show_members()

        elif choice == "7":
            print("Goodbye!")
            break

        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main()
