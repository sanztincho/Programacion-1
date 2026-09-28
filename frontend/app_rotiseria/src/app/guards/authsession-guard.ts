import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';
import { Auth } from '../services/auth';

/**
 * Guard de rutas: decide si se puede entrar a una ruta.
 * - Sin token válido (o expirado) -> al login.
 * - Con token pero rol no permitido -> a la pantalla de inicio de su rol.
 * Uso en app.routes.ts: canActivate: [authsessionGuard(['admin'])]
 */
export const authsessionGuard = (allowedRoles?: string[]): CanActivateFn => {
  return (route, state) => {
    const router = inject(Router);
    const auth = inject(Auth);

    // Verificar si está autenticado (existe el token y no expiró)
    if (!auth.isAuthenticated()) {
      auth.logout();
      return router.createUrlTree(['/auth/login']);
    }

    // Si no se especifican roles, alcanza con estar autenticado
    if (!allowedRoles || allowedRoles.length === 0) {
      return true;
    }

    // Verificar roles
    const userRole = auth.getUserRole();
    if (userRole && allowedRoles.includes(userRole)) {
      return true;
    }

    // Si no tiene permiso, redirigir a la pantalla de inicio de su rol
    return router.createUrlTree([auth.rutaInicio(userRole)]);
  };
};
