import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-card-producto',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './card-producto.html',
  styleUrls: ['./card-producto.css']
})
export class CardProducto {
  /** ID del producto */
  @Input() id!: number;

  /** Nombre del producto */
  @Input() nombre!: string;

  /** Categoría del producto (ej: Hamburguesas, Bebidas) */
  @Input() categoria?: string;

  /** Precio del producto */
  @Input() precio!: number;

  /** URL de la imagen del producto */
  @Input() imagen?: string;

  /** Indica si el producto está disponible */
  @Input() disponible: boolean = true;

  /** Promedio de estrellas (null si no tiene reseñas) */
  @Input() promedio?: number | null;

  /** Cantidad de reseñas del producto */
  @Input() cantidadValoraciones?: number;

  /** Las 5 posiciones de estrellas */
  readonly estrellas = [1, 2, 3, 4, 5];

  /** Ícono de Bootstrap Icons para la estrella n (llena, media o vacía) */
  iconoEstrella(n: number): string {
    const valor = this.promedio ?? 0;
    if (valor >= n) return 'bi-star-fill';
    if (valor >= n - 0.5) return 'bi-star-half';
    return 'bi-star';
  }
}
