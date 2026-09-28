import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class Auth {

  private http = inject(HttpClient);
  url = environment.apiUrl;

  login(dataLogin: LoginRequest): Observable<any> {
    return this.http.post(this.url + '/auth/login', dataLogin);
  }

  /**
   * Registra un nuevo usuario
   */
  register(dataRegister: RegisterRequest): Observable<any> {
    return this.http.post(this.url + '/auth/register', dataRegister);
  }

  /**
   * Decodifica el payload del JWT guardado en localStorage.
   * El token tiene 3 partes separadas por puntos: header.payload.firma
   * Cada parte está codificada en Base64URL (usa - y _ en lugar de + y /, y sin relleno =),
   * por eso se convierte a Base64 común antes de usar atob().
   */
  getPayload(): any | null {
    const token = localStorage.getItem('token');
    if (!token) {
      return null;
    }
    try {
      const base64Url = token.split('.')[1];
      let base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      while (base64.length % 4) {
        base64 += '=';
      }
      // decodeURIComponent permite leer tildes y ñ (caracteres UTF-8)
      const json = decodeURIComponent(
        atob(base64).split('').map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).join('')
      );
      return JSON.parse(json);
    } catch (error) {
      return null;
    }
  }

  /**
   * Obtiene el id del usuario desde el token (claim "sub")
   */
  getCurrentUserId(): number | null {
    const payload = this.getPayload();
    const userId = payload?.sub || payload?.id;
    return userId ? Number(userId) : null;
  }

  /**
   * Obtiene el rol del usuario actual desde el token
   */
  getUserRole(): string | null {
    return this.getPayload()?.rol || null;
  }

  /**
   * Verifica si hay un token y si todavía no expiró (claim "exp", en segundos)
   */
  isAuthenticated(): boolean {
    const payload = this.getPayload();
    if (!payload) {
      return false;
    }
    if (payload.exp && Date.now() >= payload.exp * 1000) {
      this.logout();
      return false;
    }
    return true;
  }

  /**
   * Ruta de inicio según el rol (se usa después del login y en el guard)
   */
  rutaInicio(rol: string | null = this.getUserRole()): string {
    switch (rol) {
      case 'admin': return '/admin/pedidos';
      case 'empleado': return '/empleado/estado-p';
      case 'cliente': return '/cliente/cliente-home';
      default: return '/home';
    }
  }

  /**
   * Cierra la sesión del usuario
   */
  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('email');
    localStorage.removeItem('carrito');
  }
}

interface LoginRequest {
  email: string;
  password: string;
}

interface RegisterRequest {
  nombre: string;
  apellidos: string;
  email: string;
  cellphone: string;
  password: string;
}
