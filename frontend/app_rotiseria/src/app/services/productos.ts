import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

/** Filtros que acepta GET /productos (todos opcionales) */
export interface FiltrosProductos {
  nombre?: string;
  categoria?: string;
  disponibilidad?: string;
  precio_min?: number;
  precio_max?: number;
  valoracion_min?: number;                             // promedio mínimo de estrellas (1 a 5)
  orden?: 'valoracion' | 'precio_asc' | 'precio_desc'; // criterio de ordenamiento
  page?: number;
  per_page?: number;
}

@Injectable({
  providedIn: 'root'
})
export class Productos {
  private http = inject(HttpClient);
  url = environment.apiUrl;

  private headers(): HttpHeaders {
    return new HttpHeaders({
      'content-type': 'application/json',
      'Authorization': 'Bearer ' + localStorage.getItem('token')
    });
  }

  /**
   * Obtiene los productos. Los filtros viajan como query params:
   * /productos?valoracion_min=4&orden=valoracion&page=1&per_page=9
   */
  getProductos(filtros: FiltrosProductos = {}): Observable<any> {
    let params = new HttpParams();
    Object.entries(filtros).forEach(([clave, valor]) => {
      if (valor !== null && valor !== undefined && valor !== '') {
        params = params.set(clave, String(valor));
      }
    });
    return this.http.get(this.url + '/productos', { headers: this.headers(), params });
  }

  /**
   * Obtiene un producto específico por ID
   */
  getProducto(id: number): Observable<any> {
    return this.http.get(this.url + '/producto/' + id, { headers: this.headers() });
  }

  /**
   * Resumen de las reseñas del producto generado por el LLM del backend
   */
  getResumen(id: number): Observable<any> {
    return this.http.get(this.url + '/producto/' + id + '/resumen', { headers: this.headers() });
  }

  /**
   * Crea un nuevo producto (requiere rol admin)
   */
  createProducto(data: any): Observable<any> {
    return this.http.post(this.url + '/productos', data, { headers: this.headers() });
  }

  /**
   * Actualiza un producto por ID (requiere rol admin o empleado)
   */
  updateProducto(id: number, data: any): Observable<any> {
    return this.http.put(this.url + '/producto/' + id, data, { headers: this.headers() });
  }

  /**
   * Elimina un producto por ID (requiere rol admin)
   */
  deleteProducto(id: number): Observable<any> {
    return this.http.delete(this.url + '/producto/' + id, { headers: this.headers() });
  }
}
