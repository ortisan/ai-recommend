# import asyncio
# from surrealdb import Surreal
#
# async def main():
#     db = Surreal()
#
#     # Connect to the remote server
#     await db.connect("http://localhost:8000")  # or "https://your-server:8000"
#
#     # Sign in with root credentials
#     await db.signin({
#         "user": "root",
#         "pass": "Password"
#     })
#
#     # Select namespace and database
#     await db.use("test", "test")
#
#     # Create a record
#     created = await db.create("person", {
#         "name": "Alice",
#         "age": 30
#     })
#     print("Created:", created)
#
#     # Select records
#     people = await db.select("person")
#     print("People:", people)
#
#     await db.close()
#
# # Run the async function
# asyncio.run(main())


# Import the Surreal class
from surrealdb import Surreal

# Using a context manger to automatically connect and disconnect
with Surreal("ws://localhost:8000/rpc") as db:
    db.signin({"username": 'root', "password": 'Password'})
    db.use("user_product", "user_product_relation")

    # Create a record in the person table
    person_record = db.create(
        "person",
        {
            "name": "Marcelo Ortiz de Santana",
            "email": "tentativafc@gmail.com",
            "tags": [],
        },
    )
    print(person_record)
    print(db.select("person"))


    product_record = db.create(
        "product",
        {
            "sku": "123456",
            "name": "Lord Of The Rings",
            "tags": ["book", "adventure"],
        },
    )
    print(product_record)
    print(db.select("product"))



    # Read all the records in the table

    # # Update all records in the table
    # print(db.update("person", {
    #     "user": "you",
    #     "password": "very_safe",
    #     "marketing": False,
    #     "tags": ["Awesome"]
    # }))

    # # Delete all records in the table
    # print(db.delete("person"))
    #
    # # You can also use the query method
    # # doing all of the above and more in SurrealQl
    #
    # # In SurrealQL you can do a direct insert
    # # and the table will be created if it doesn't exist
    #
    # # Create
    # db.query("""
    #          insert into person {
    #              user : 'me',
    #              password: 'very_safe',
    #              tags: ['python', 'documentation']
    #              };
    #          """)
    #
    # # Read
    # print(db.query("select * from person"))
    #
    # # Update
    # print(db.query("""
    # update person content {
    #     user: 'you',
    #     password: 'more_safe',
    #     tags: ['awesome']
    # };
    # """))
    #
    # # Delete
    # print(db.query("delete person"))