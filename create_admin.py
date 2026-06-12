import asyncio
from src.db.database import async_session
from src.auth.models import User
from src.auth.hashing import hash_password
from getpass import getpass
from email_validator import validate_email, EmailNotValidError
from sqlalchemy import select

async def create_admin():
    username = input("username: ")
    email = input("email: ")
    try:
        valid = validate_email(email)
        email = valid.email

        password = getpass("password: ")
        password2 = getpass("password again: ")
        if password != password2:
            print("password does not match")
            return
        async with async_session() as session:

            result = await session.execute(select(User).where(User.username == username | User.email == email))

            existing_user = result.scalar_one_or_none()

            if existing_user:
                print("User with this email or username already exists")
                return

            user = User(username=username, email=email, password=hash_password(password), is_admin=True)
                    
            session.add(user)
            await session.commit()
            print("user admin created")
    except EmailNotValidError as e:
        print("Invalid email:", str(e))

asyncio.run(create_admin())