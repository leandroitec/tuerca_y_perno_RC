from rest_framework import permissions


def roles_permitidos(*roles, lectura_publica=False):
    """
    Crea una clase de permiso que solo deja pasar a usuarios con alguno de
    los roles indicados (campo `rol` de UsuarioPersonalizado).

    - El superusuario de Django siempre tiene acceso.
    - Con lectura_publica=True, los métodos de solo lectura (GET, HEAD,
      OPTIONS) quedan abiertos a cualquiera, incluso sin token (lo usa el
      catálogo público del front).

    Uso: permission_classes = [roles_permitidos('ADMIN', 'DEPOSITO')]
    """

    class RolPermitido(permissions.BasePermission):
        message = "Tu rol no tiene permisos para realizar esta acción."

        def has_permission(self, request, view):
            if lectura_publica and request.method in permissions.SAFE_METHODS:
                return True

            user = request.user
            if not user or not user.is_authenticated:
                return False

            return user.is_superuser or getattr(user, 'rol', None) in roles

    RolPermitido.__name__ = f"RolPermitido_{'_'.join(roles)}"
    return RolPermitido
