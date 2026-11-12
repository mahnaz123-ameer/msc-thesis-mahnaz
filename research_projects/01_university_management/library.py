# =============================================================
# library.py — Library Book and Borrowing Management
# University Management System
# =============================================================


def add_book(catalog, book_id, title, author, isbn, copies=1, category="General"):
    """Add a book to the library catalog."""
    if book_id in catalog:
        return False, "Book ID already exists"
    if copies < 1:
        return False, "Copies must be at least 1"
    catalog[book_id] = {
        "title": title,
        "author": author,
        "isbn": isbn,
        "copies": copies,
        "borrowed": 0,
        "category": category,
    }
    return True, "Book added"


def remove_book(catalog, book_id):
    """Remove a book from the catalog."""
    if book_id not in catalog:
        return False, "Book not found"
    if catalog[book_id]["borrowed"] > 0:
        return False, "Cannot remove book with active borrows"
    del catalog[book_id]
    return True, "Book removed"


def borrow_book(catalog, borrowed, book_id, student_id, borrow_date, due_days=14):
    """Borrow a book from the library."""
    if book_id not in catalog:
        return False, "Book not found"
    available = catalog[book_id]["copies"] - catalog[book_id]["borrowed"]
    if available <= 0:
        return False, "No copies available"
    if student_id not in borrowed:
        borrowed[student_id] = []
    already = [b for b in borrowed[student_id] if b["book_id"] == book_id]
    if already:
        return False, "Student already has this book"
    catalog[book_id]["borrowed"] += 1
    borrowed[student_id].append({
        "book_id": book_id,
        "borrow_date": borrow_date,
        "due_days": due_days,
    })
    return True, "Book borrowed"


def return_book(catalog, borrowed, book_id, student_id):
    """Return a borrowed book to the library."""
    if book_id not in catalog:
        return False, "Book not found"
    if student_id not in borrowed:
        return False, "No borrow record found"
    record = next((b for b in borrowed[student_id] if b["book_id"] == book_id), None)
    if not record:
        return False, "Student has not borrowed this book"
    catalog[book_id]["borrowed"] -= 1
    borrowed[student_id].remove(record)
    return True, "Book returned"


def calculate_fine(days_overdue, fine_per_day=10, max_fine=500):
    """Calculate fine for overdue book return."""
    if days_overdue < 0:
        return None
    return min(days_overdue * fine_per_day, max_fine)


def get_available_copies(catalog, book_id):
    """Get number of available (not borrowed) copies."""
    if book_id not in catalog:
        return 0
    return catalog[book_id]["copies"] - catalog[book_id]["borrowed"]


def is_book_available(catalog, book_id):
    """Check if at least one copy of a book is available."""
    return get_available_copies(catalog, book_id) > 0


def get_borrowed_books(borrowed, student_id):
    """Get all books currently borrowed by a student."""
    return borrowed.get(student_id, [])


def get_borrow_count(borrowed, student_id):
    """Get number of books currently borrowed by a student."""
    return len(borrowed.get(student_id, []))


def has_exceeded_borrow_limit(borrowed, student_id, max_books=5):
    """Check if student has exceeded borrowing limit."""
    return get_borrow_count(borrowed, student_id) >= max_books


def search_by_title(catalog, keyword):
    """Search books by keyword in title (case-insensitive)."""
    keyword = keyword.lower()
    return {bid: info for bid, info in catalog.items()
            if keyword in info["title"].lower()}


def search_by_author(catalog, author):
    """Search books by author name."""
    author = author.lower()
    return {bid: info for bid, info in catalog.items()
            if author in info["author"].lower()}


def search_by_category(catalog, category):
    """Get all books in a specific category."""
    return {bid: info for bid, info in catalog.items()
            if info["category"].lower() == category.lower()}


def get_total_books(catalog):
    """Get total number of book titles in catalog."""
    return len(catalog)


def get_total_copies(catalog):
    """Get total number of physical copies in library."""
    return sum(info["copies"] for info in catalog.values())


def get_total_borrowed(catalog):
    """Get total number of copies currently borrowed."""
    return sum(info["borrowed"] for info in catalog.values())


def add_copies(catalog, book_id, additional_copies):
    """Add more copies of an existing book."""
    if book_id not in catalog:
        return False, "Book not found"
    if additional_copies <= 0:
        return False, "Must add at least 1 copy"
    catalog[book_id]["copies"] += additional_copies
    return True, f"{additional_copies} copies added"


def get_most_borrowed_books(catalog, top_n=5):
    """Get the most borrowed books."""
    sorted_books = sorted(catalog.items(), key=lambda x: x[1]["borrowed"], reverse=True)
    return sorted_books[:top_n]
