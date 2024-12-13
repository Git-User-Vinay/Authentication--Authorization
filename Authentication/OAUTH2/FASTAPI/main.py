import jwt
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model
from tortoise.contrib.fastapi import register_tortoise
from tortoise import fields
from passlib.hash import bcrypt


# Initialize the FastAPI application
app = FastAPI()

# Secret key used for signing JWT tokens
JWT_SECRET = 'myjwtsecret'


# Define the User model which will be stored in the database
class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(50, unique=True)
    password_hash = fields.CharField(128)
    
    def verify_password(self, password):
        """
        Verifies a given password against the stored hashed password.
        """
        return bcrypt.verify(password, self.password_hash)
    

# Create Pydantic models for serializing/deserializing User objects
User_Pydantic = pydantic_model_creator(User, name='User')
UserIn_Pydantic = pydantic_model_creator(User, name='UserIn', exclude_readonly=True) 


# OAuth2PasswordBearer is used for handling the bearer token in headers
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


# Function to authenticate a user by checking username and password
async def authenticate_user(username: str, password:str):
    """
    Authenticate a user by checking their credentials.
    Returns the user if valid, otherwise returns False.
    """
    user = await User.get(username=username)
    if not user:
        return False
    if not user.verify_password(password):
        return False
    return user


# Endpoint to generate a JWT token for the user
@app.post('/token')
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint to generate JWT token using the username and password.
    Returns a token if credentials are valid, otherwise returns an error message.
    """
    user = await authenticate_user(form_data.username, form_data.password)

    if not user:
        return {'error' : 'Invalid Credentials'}
    
     # Convert the user object into a Pydantic model for serialization
    user_obj = await User_Pydantic.from_tortoise_orm(user)

    # Generate JWT token by encoding the user data
    token = jwt.encode(user_obj.model_dump(), JWT_SECRET)

    # Return the JWT token with a token type of 'bearer'
    return {'access_token': token, 'token_type': 'bearer'}


# Function to retrieve the current user from the JWT token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Extract the current user from the JWT token.
    Raises HTTPException if the token is invalid.
    """
    try:
        # Decode the JWT token to retrieve user ID
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user = await User.get(id=payload.get('id'))
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid username or password')
    
    return await User_Pydantic.from_tortoise_orm(user)


# Endpoint to create a new user
@app.post('/users', response_model=User_Pydantic)
async def create_user(user: UserIn_Pydantic):
    """
    Endpoint to create a new user by providing a username and password.
    The password will be hashed before saving.
    """
    user_obj = User(username=user.username, password_hash=bcrypt.hash(user.password_hash))
    await user_obj.save()
    return await User_Pydantic.from_tortoise_orm(user_obj)


# Endpoint to get the current authenticated user’s details
@app.get('/users/me', response_model=User_Pydantic)
async def get_user(user : User_Pydantic = Depends(get_current_user)):
    return user


# Register the database with Tortoise ORM and set up the connection to the PostgreSQL database
register_tortoise(
    app,
    db_url='postgres://postgres:1234@localhost:5432/auth_db',
    modules={'models':['main']},
    generate_schemas=True,
    add_exception_handlers=True
)