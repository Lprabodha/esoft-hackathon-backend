# cognitive_navigator_backend/schemas/__init__.py
from fastapi.security import OAuth2PasswordBearer

# Define the OAuth2 scheme, pointing to your login endpoint
# This makes `oauth2_scheme` available directly when importing `schemas`
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")