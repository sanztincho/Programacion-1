import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class Valoraciones {
  private http = inject(HttpClient);
  url = environment.apiUrl;

  /**
   * Obtiene las valoraciones con filtros y paginación
   */
  getValoraciones(params?: { page?: number; per_page?: number; puntuacion?: number;
                             id_producto?: number; id_usuario?: number; con_imagen?: boolean }): Observable<any> {
    let headers = new HttpHeaders({
      'content-type': 'application/json',
      'Authorization': 'Bearer ' + localStorage.getItem('token')
    });

    let httpParams = new HttpParams();
    Object.entries(params || {}).forEach(([clave, valor]) => {
      if (valor !== null && valor !== undefined) {
        httpParams = httpParams.set(clave, String(valor));
      }
    });

    return this.http.get(this.url + '/valoraciones', { headers, params: httpParams });
  }

  /**
   * Obtiene una valoración específica por ID
   */
  getValoracion(id: number): Observable<any> {
    let headers = new HttpHeaders({
      'content-type': 'application/json',
      'Authorization': 'Bearer ' + localStorage.getItem('token')
    });
    return this.http.get(this.url + '/valoracion/' + id, { headers });
  }

  /**
   * Crea una nueva valoración.
   * Recibe un FormData (multipart/form-data) para poder adjuntar una imagen.
   * IMPORTANTE: no se fija el 'content-type' a mano: el navegador lo arma solo
   * con el "boundary" que separa cada campo del formulario.
   */
  createValoracion(data: FormData): Observable<any> {
    let headers = new HttpHeaders({
      'Authorization': 'Bearer ' + localStorage.getItem('token')
    });
    return this.http.post(this.url + '/valoraciones', data, { headers });
  }

  /**
   * Elimina una valoración (autor o admin)
   */
  deleteValoracion(id: number): Observable<any> {
    let headers = new HttpHeaders({
      'Authorization': 'Bearer ' + localStorage.getItem('token')
    });
    return this.http.delete(this.url + '/valoracion/' + id, { headers });
  }

  /**
   * Convierte la ruta que devuelve la API (/uploads/...) en una URL completa
   */
  urlImagen(ruta: string | null | undefined): string | null {
    return ruta ? this.url + ruta : null;
  }
}
