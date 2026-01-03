from enum import Enum
from functools import wraps
from utils.session import Session


class Role(Enum):
    """User role levels"""
    ADMIN = "admin"
    MANAGER = "manager"
    VENDEUR = "vendeur"


class Permission(Enum):
    """User permissions"""
    # Dashboard
    VIEW_DASHBOARD = "view_dashboard"
    VIEW_STATISTICS = "view_statistics"
    
    # Clients
    VIEW_CLIENTS = "view_clients"
    CREATE_CLIENT = "create_client"
    EDIT_CLIENT = "edit_client"
    DELETE_CLIENT = "delete_client"
    
    # Products
    VIEW_PRODUCTS = "view_products"
    CREATE_PRODUCT = "create_product"
    EDIT_PRODUCT = "edit_product"
    DELETE_PRODUCT = "delete_product"
    
    # Sales
    VIEW_SALES = "view_sales"
    CREATE_SALE = "create_sale"
    EDIT_SALE = "edit_sale"
    DELETE_SALE = "delete_sale"
    VALIDATE_SALE = "validate_sale"
    
    # Users
    VIEW_USERS = "view_users"
    CREATE_USER = "create_user"
    EDIT_USER = "edit_user"
    DELETE_USER = "delete_user"
    
    # Settings
    VIEW_SETTINGS = "view_settings"
    EDIT_SETTINGS = "edit_settings"
    EXPORT_DATA = "export_data"


# Role permissions mapping
ROLE_PERMISSIONS = {
    Role.ADMIN: {
        # Admin has all permissions
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_STATISTICS,
        Permission.VIEW_CLIENTS,
        Permission.CREATE_CLIENT,
        Permission.EDIT_CLIENT,
        Permission.DELETE_CLIENT,
        Permission.VIEW_PRODUCTS,
        Permission.CREATE_PRODUCT,
        Permission.EDIT_PRODUCT,
        Permission.DELETE_PRODUCT,
        Permission.VIEW_SALES,
        Permission.CREATE_SALE,
        Permission.EDIT_SALE,
        Permission.DELETE_SALE,
        Permission.VALIDATE_SALE,
        Permission.VIEW_USERS,
        Permission.CREATE_USER,
        Permission.EDIT_USER,
        Permission.DELETE_USER,
        Permission.VIEW_SETTINGS,
        Permission.EDIT_SETTINGS,
        Permission.EXPORT_DATA,
    },
    Role.MANAGER: {
        # Manager can view and validate
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_STATISTICS,
        Permission.VIEW_CLIENTS,
        Permission.VIEW_PRODUCTS,
        Permission.VIEW_SALES,
        Permission.VALIDATE_SALE,
        Permission.EXPORT_DATA,
    },
    Role.VENDEUR: {
        # Seller can create sales and view clients/products
        Permission.VIEW_CLIENTS,
        Permission.CREATE_SALE,
        Permission.VIEW_SALES,
        Permission.VIEW_PRODUCTS,
        Permission.VIEW_DASHBOARD,
    }
}


def get_user_permissions(role_name):
    """Get all permissions for a given role"""
    try:
        role = Role(role_name)
        return ROLE_PERMISSIONS.get(role, set())
    except ValueError:
        return set()


def user_has_permission(permission: Permission):
    """Decorator to check if user has required permission"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = Session.get_user()
            if not user:
                raise PermissionError("Utilisateur non authentifié")
            
            user_permissions = get_user_permissions(user['role'])
            if permission not in user_permissions:
                raise PermissionError(
                    f"Permission refusée: {permission.value} "
                    f"requise pour {user['role']}"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator


def user_has_role(*roles):
    """Decorator to check if user has one of the required roles"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = Session.get_user()
            if not user:
                raise PermissionError("Utilisateur non authentifié")
            
            if user['role'] not in roles:
                raise PermissionError(
                    f"Accès refusé: rôle(s) {roles} requis, "
                    f"vous avez le rôle {user['role']}"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator



def check_role(*roles):
    """Check if current user has one of the roles (returns bool)"""
    user = Session.get_user()
    if not user:
        return False
    return user['role'] in roles


def check_permission(permission: Permission):
    """Check if current user has a specific permission (returns bool)"""
    user = Session.get_user()
    if not user:
        return False
    user_permissions = get_user_permissions(user['role'])
    return permission in user_permissions
