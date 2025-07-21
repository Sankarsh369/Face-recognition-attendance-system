from .auth import auth_bp
from .teacher import teacher_bp
from .principal import principal_bp

# Blueprints for external imports
__all__ = ["auth_bp", "teacher_bp", "principal_bp"]