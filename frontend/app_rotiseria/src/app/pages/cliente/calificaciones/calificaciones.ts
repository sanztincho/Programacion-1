import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Navbar } from '../../../components/shared/navbar/navbar';
import { Header } from '../../../components/shared/header/header';
import { Pagination } from '../../../components/shared/pagination/pagination';
import { Valoraciones as ValoracionesService } from '../../../services/valoraciones';
import { Auth } from '../../../services/auth';

@Component({
  selector: 'app-calificaciones',
  standalone: true,
  imports: [CommonModule, FormsModule, Navbar, Header, Pagination],
  templateUrl: './calificaciones.html',
  styleUrls: ['./calificaciones.css']
})
export class Calificaciones implements OnInit {
  private valoracionesService = inject(ValoracionesService);
  private authService = inject(Auth);

  calificaciones: any[] = [];
  cargando: boolean = false;
  error: string = '';
  idUsuarioActual: number | null = null;

  // Filtros
  filtroEstrellas: number | null = null;  // null = todas
  soloConFoto: boolean = false;
  soloMias: boolean = false;

  // Imagen ampliada (al hacer clic en una miniatura)
  imagenAmpliada: string | null = null;

  // Datos de paginación
  currentPage: number = 1;
  totalPages: number = 1;
  totalItems: number = 0;
  itemsPerPage: number = 10;

  readonly estrellas = [1, 2, 3, 4, 5];

  ngOnInit() {
    this.idUsuarioActual = this.authService.getCurrentUserId();
    this.cargarCalificaciones();
  }

  cargarCalificaciones(page: number = 1) {
    this.cargando = true;
    this.error = '';
    this.currentPage = page;

    this.valoracionesService.getValoraciones({
      page: page,
      per_page: this.itemsPerPage,
      puntuacion: this.filtroEstrellas ?? undefined,
      con_imagen: this.soloConFoto || undefined,
      id_usuario: this.soloMias ? (this.idUsuarioActual ?? undefined) : undefined
    }).subscribe({
      next: (response) => {
        // El backend devuelve {valoraciones: [...], total, pages, page}
        this.totalPages = response.pages || 1;
        this.totalItems = response.total || 0;

        this.calificaciones = (response.valoraciones || []).map((v: any) => ({
          id: v.id,
          idUsuario: v.id_usuario,
          usuario: this.obtenerNombreUsuario(v.user),
          comentario: v.comentario || 'Sin comentario',
          estrellas: v.puntuacion || 0,
          producto: v.producto?.nombre || '',
          imagen: this.valoracionesService.urlImagen(v.imagen)
        }));
        this.cargando = false;
      },
      error: () => {
        this.error = 'Error al cargar las calificaciones';
        this.cargando = false;
      }
    });
  }

  aplicarFiltros() {
    this.cargarCalificaciones(1);
  }

  eliminar(c: any) {
    if (!confirm('¿Eliminar tu reseña?')) return;
    this.valoracionesService.deleteValoracion(c.id).subscribe({
      next: () => this.cargarCalificaciones(this.currentPage),
      error: () => alert('No se pudo eliminar la reseña.')
    });
  }

  obtenerNombreUsuario(user: any): string {
    if (!user) return 'Usuario desconocido';
    if (user.nombre && user.apellidos) {
      return `${user.nombre} ${user.apellidos}`;
    }
    return user.nombre || user.email || 'Usuario desconocido';
  }
}
