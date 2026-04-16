from fastapi import Body, FastAPI

app = FastAPI()

BOOKS = [
  {"title": "A Brief History of Time", "author": "Stephen Hawking", "category": "science"},
  {"title": "Sapiens: A Brief History of Humankind", "author": "Yuval", "category": "history"},
  {"title": "The Alchemist", "author": "Paulo Coelho", "category": "fiction"},
  {"title": "To Kill a Mockingbird", "author": "Harper Lee", "category": "classic"},
  {"title": "Atomic Habits", "author": "James Clear", "category": "self-help"},
  {"title": "The Lean Startup", "author": "Eric Ries", "category": "business"},
  {"title": "Clean Code", "author": "Robert C. Martin", "category": "programming"},
  {"title": "The Pragmatic Programmer", "author": "Andrew Hunt", "category": "programming"},
  {"title": "Thinking, Fast and Slow", "author": "Daniel Kahneman", "category": "psychology"},
  {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "category": "classic"}
]

@app.get("/books")
def read_all_book():
    return BOOKS


@app.get("/books/{book_title}")
def read_all_book(book_title: str):
    for book in BOOKS:
        if book.get('title').casefold() == book_title.casefold():
            return book
    

@app.get("/books/")
def read_category_by_query(category: str):
    books_return = []
    for book in BOOKS:
        if book.get("category").casefold() == category.casefold():
            books_return.append(book)
    
    return books_return


@app.get("/books/{book_author}/")    # add slash(/) at the end for query pamater
def read_author_category_by_query(book_author: str, category: str):
    books_return = []
    print(category, book_author)
    for book in BOOKS:
        if book.get("author").casefold() == book_author.casefold() and book.get("category").casefold() == category.casefold():
            books_return.append(book)
    return books_return


@app.post("/books/create_book")
def create_book(new_book = Body()):
    BOOKS.append(new_book)


@app.put("/books/update")
def update_book(update_book = Body()):
    for i in range(len(BOOKS)):
        if BOOKS[i].get("title").casefold() == update_book.get("title").casefold():
            BOOKS[i] = update_book


@app.delete("/books/delete/{book_title}")
def delete_book(book_title: str):
    for book in BOOKS:
        if book.get("title").casefold() == book_title.casefold():
            BOOKS.remove(book)