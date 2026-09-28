import { Component, Input } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { Auth } from '../../../services/auth';
import { inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CartService } from '../../../services/cart.service';

/**
 * Componente de encabezado reutilizable para páginas
 * Muestra un recuadro con un título centrado
 */
@Component({
  selector: 'app-header',
  imports: [CommonModule, RouterModule],
  templateUrl: './header.html',
  styleUrl: './header.css'
})
export class Header {
  /**
   * Título que se mostrará en el header
   * Ejemplo: "Productos", "Pedidos", "Usuarios"
   */
  @Input() titulo: string = '';
  
  private authService = inject(Auth);
  private router = inject(Router);
  private cart = inject(CartService);
  
  /**
   * Cierra la sesión y redirige al home
   */
  cerrarSesion() {
    this.authService.logout();
    // Vaciar el carrito para que el próximo usuario no vea los productos de este
    this.cart.clear();
    this.router.navigate(['/home']);
  }
}
