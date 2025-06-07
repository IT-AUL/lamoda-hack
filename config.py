class Config:
    SECRET_KEY = "your-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///sellers.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "jwt-secret"
    JWT_ACCESS_TOKEN_EXPIRES = 300  # 5 минут
    JWT_REFRESH_TOKEN_EXPIRES = 86400  # 1 день