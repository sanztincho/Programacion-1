import { Component, OnInit, inject } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CardProducto } from '../../../components/shared/producto/card-producto';
import { CartService } from '../../../services/cart.service';
import { Navbar } from '../../../components/shared/navbar/navbar';
import { Header } from '../../../components/shared/header/header';
import { Pagination } from '../../../components/shared/pagination/pagination';
import { Search } from '../../../components/shared/search/search';
import { Auth } from '../../../services/auth';
import { Productos, FiltrosProductos } from '../../../services/productos';

@Component({
  selector: 'app-cliente-home',
  standalone: true,
  imports: [CommonModule, FormsModule, Navbar, CardProducto, Header, Pagination, Search],
  templateUrl: './cliente-home.html',
  styleUrls: ['./cliente-home.css']
})
export class ClienteHome implements OnInit {
  private authService = inject(Auth);
  private router = inject(Router);
  private cart = inject(CartService);
  private productoService = inject(Productos);

  userRole: string | null = null;
  cargando: boolean = false;
  productos: any[] = [];

  // Filtros (se mandan al backend como query params)
  busqueda: string = '';
  valoracionMin: number | null = null;   // null = todas las calificaciones
  orden: string = '';                    // '' | 'valoracion' | 'precio_asc' | 'precio_desc'
  readonly opcionesValoracion = [
    { valor: null, texto: 'Todas las calificaciones' },
    { valor: 4, texto: '4 estrellas o más' },
    { valor: 3, texto: '3 estrellas o más' },
    { valor: 2, texto: '2 estrellas o más' }
  ];

  // Paginación
  currentPage: number = 1;
  totalPages: number = 1;
  totalItems: number = 0;
  readonly itemsPerPage: number = 9;

  // Resúmenes de reseñas hechos por la IA, indexados por id de producto
  resumenes: { [id: number]: { texto: string; fuente: string } | 'cargando' } = {};

  ngOnInit() {
    this.userRole = this.authService.getUserRole();
    this.cargarProductos();
  }

  /**
   * Carga los productos desde el backend aplicando filtros y paginación
   */
  cargarProductos(page: number = 1) {
    this.cargando = true;
    this.currentPage = page;

    const filtros: FiltrosProductos = {
      nombre: this.busqueda.trim(),
      valoracion_min: this.valoracionMin ?? undefined,
      orden: (this.orden || undefined) as FiltrosProductos['orden'],
      page,
      per_page: this.itemsPerPage
    };
    // El cliente solo ve lo que se puede pedir; admin y empleado ven todo
    if (this.userRole === 'cliente') {
      filtros.disponibilidad = 'disponible';
    }

    this.productoService.getProductos(filtros).subscribe({
      next: (response: any) => {
        this.totalPages = response.pages || 1;
        this.totalItems = response.total || 0;
        this.productos = (response.productos || []).map((p: any) => ({
          ...p,
          imagen: p.imagen || 'assets/buger1.jpg',
          disponible: p.disponibilidad === 'disponible'
        }));
        this.cargando = false;
      },
      error: () => {
        this.cargando = false;
        this.productos = [];
        alert('Error al cargar productos. Verificá tu conexión.');
      }
    });
  }

  /** Al cambiar cualquier filtro se vuelve a la página 1 */
  aplicarFiltros() {
    this.cargarProductos(1);
  }

  limpiarFiltros() {
    this.busqueda = '';
    this.valoracionMin = null;
    this.orden = '';
    this.cargarProductos(1);
  }

  onPageChange(page: number) {
    this.cargarProductos(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  agregarAlCarrito(p: any) {
    this.cart.addItem({
      id: p.id,
      nombre: p.nombre,
      precio: p.precio,
      cantidad: 1
    });
    alert(`🛒 ${p.nombre} agregado al carrito`);
  }

  /** Abre la pantalla para elegir cantidad, ingredientes y nota */
  personalizar(p: any) {
    this.router.navigate(['/cliente/hacer-pedido', p.id]);
  }

  /** Pide (o esconde) el resumen de reseñas generado por el LLM */
  verResumen(p: any) {
    if (this.resumenes[p.id] && this.resumenes[p.id] !== 'cargando') {
      delete this.resumenes[p.id];
      return;
    }
    this.resumenes[p.id] = 'cargando';
    this.productoService.getResumen(p.id).subscribe({
      next: (r: any) => this.resumenes[p.id] = { texto: r.resumen, fuente: r.fuente },
      error: () => this.resumenes[p.id] = { texto: 'No se pudo obtener el resumen.', fuente: 'error' }
    });
  }

  /** Helpers para el template (evitan lógica compleja en el HTML) */
  estaCargandoResumen(id: number): boolean {
    return this.resumenes[id] === 'cargando';
  }

  resumenDe(id: number): { texto: string; fuente: string } | null {
    const r = this.resumenes[id];
    return r && r !== 'cargando' ? r : null;
  }
}
