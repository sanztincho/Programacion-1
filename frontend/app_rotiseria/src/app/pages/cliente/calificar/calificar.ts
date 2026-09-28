import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Navbar } from '../../../components/shared/navbar/navbar';
import { Header } from '../../../components/shared/header/header';
import { Valoraciones } from '../../../services/valoraciones';
import { Pedidos } from '../../../services/pedidos';

@Component({
  selector: 'app-calificar',
  standalone: true,
  imports: [CommonModule, FormsModule, Navbar, Header],
  templateUrl: './calificar.html',
  styleUrl: './calificar.css'
})
export class Calificar implements OnInit {

  // Formatos y tamaño máximo (deben coincidir con lo que valida el backend)
  readonly TIPOS_PERMITIDOS = ['image/png', 'image/jpeg', 'image/gif', 'image/webp'];
  readonly MAX_MB = 5;

  pedidoId: number | null = null;
  pedidoData: any = null;
  cargando: boolean = false;
  enviando: boolean = false;

  // Datos de la calificación
  productoId: number | null = null;   // producto del pedido que se califica
  rating: number = 0;
  hoverRating: number = 0;
  comentario: string = '';

  // Imagen adjunta
  imagen: File | null = null;
  previewImagen: string | null = null;

  mensajeExito: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private valoracionesService: Valoraciones,
    private pedidosService: Pedidos
  ) { }

  ngOnInit(): void {
    // El id del pedido viene en la URL: /cliente/calificar/:idPedido
    this.route.paramMap.subscribe(params => {
      const idString = params.get('idPedido');
      if (idString) {
        this.pedidoId = +idString;
        this.cargarDatosPedido();
      }
    });
  }

  /**
   * Carga los datos del pedido desde el backend
   */
  cargarDatosPedido() {
    if (!this.pedidoId) return;

    this.cargando = true;
    this.pedidosService.getPedido(this.pedidoId).subscribe({
      next: (response: any) => {
        this.pedidoData = response;
        // Por defecto se preselecciona el primer producto del pedido
        this.productoId = response.productos?.length ? response.productos[0].id : null;
        this.cargando = false;
      },
      error: () => {
        this.cargando = false;
        this.mensajeExito = '⚠️ No se pudo cargar la información del pedido';
      }
    });
  }

  setRating(value: number): void {
    this.rating = value;
  }

  setHoverRating(value: number): void {
    this.hoverRating = value;
  }

  resetHoverRating(): void {
    this.hoverRating = 0;
  }

  /**
   * Se ejecuta cuando el usuario elige un archivo en el <input type="file">
   */
  onImagenSeleccionada(event: Event): void {
    const input = event.target as HTMLInputElement;
    const archivo = input.files && input.files.length ? input.files[0] : null;
    if (!archivo) return;

    if (!this.TIPOS_PERMITIDOS.includes(archivo.type)) {
      this.mensajeExito = '⚠️ Formato no permitido. Usá PNG, JPG, GIF o WEBP.';
      input.value = '';
      return;
    }
    if (archivo.size > this.MAX_MB * 1024 * 1024) {
      this.mensajeExito = `⚠️ La imagen supera los ${this.MAX_MB} MB.`;
      input.value = '';
      return;
    }

    this.mensajeExito = null;
    this.imagen = archivo;
    // FileReader convierte el archivo en una URL "data:" para mostrar la vista previa
    const lector = new FileReader();
    lector.onload = () => this.previewImagen = lector.result as string;
    lector.readAsDataURL(archivo);
  }

  quitarImagen(input: HTMLInputElement): void {
    this.imagen = null;
    this.previewImagen = null;
    input.value = '';
  }

  // --- Lógica de envío ---

  enviarCalificacion(): void {
    if (this.rating === 0) {
      this.mensajeExito = '⚠️ Por favor, seleccioná una calificación (1 a 5 estrellas) antes de enviar.';
      return;
    }
    if (!this.productoId) {
      this.mensajeExito = '⚠️ Elegí qué producto del pedido querés calificar.';
      return;
    }

    this.enviando = true;

    // FormData arma un cuerpo multipart/form-data: campos de texto + archivo
    const datos = new FormData();
    datos.append('id_producto', String(this.productoId));
    datos.append('puntuacion', String(this.rating));
    datos.append('comentario', this.comentario || '');
    if (this.imagen) {
      datos.append('imagen', this.imagen, this.imagen.name);
    }
    // El id del usuario NO se manda: el backend lo toma del token

    this.valoracionesService.createValoracion(datos).subscribe({
      next: () => {
        this.mensajeExito = '✅ Su valoración ha sido enviada con éxito.';
        this.enviando = false;
        // Redirigir a calificaciones después de 2 segundos
        setTimeout(() => this.router.navigate(['/cliente/calificaciones']), 2000);
      },
      error: (error) => {
        this.mensajeExito = '⚠️ ' + (error.error?.message || 'Error al enviar la calificación. Intentá nuevamente.');
        this.enviando = false;
      }
    });
  }
}
