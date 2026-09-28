import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { CartService, CartItem } from '../../../services/cart.service';
import { Navbar } from '../../../components/shared/navbar/navbar';
import { Header } from '../../../components/shared/header/header';
import { Productos } from '../../../services/productos';

@Component({
  selector: 'app-hacer-pedido',
  standalone: true,
  imports: [CommonModule, FormsModule, Navbar,Header],
  templateUrl: './hacer-pedido.html',
  styleUrls: ['./hacer-pedido.css']
})
export class HacerPedido implements OnInit {
  producto: any = null;
  ingredientes = [
    { nombre: 'Cebolla', incluido: true },
    { nombre: 'Queso cheddar', incluido: true },
    { nombre: 'Lechuga', incluido: false },
    { nombre: 'Tomate', incluido: false }
  ];
  nota: string = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private cart: CartService,
    private productoService: Productos
  ) {}

  ngOnInit() {
    const data = localStorage.getItem('productoEditando');
    if (data) {
      this.producto = JSON.parse(data);
      localStorage.removeItem('productoEditando');
    } else {
      // El id llega por la URL: /cliente/hacer-pedido/:id -> se busca el producto real en la API
      const id = Number(this.route.snapshot.paramMap.get('id'));
      if (!id) {
        this.router.navigate(['/cliente/cliente-home']);
        return;
      }
      this.productoService.getProducto(id).subscribe({
        next: (p: any) => {
          this.producto = { id: p.id, nombre: p.nombre, precio: p.precio, cantidad: 1 };
          // Si ya estaba en el carrito, se cargan su cantidad, extras y nota para editarlo
          const enCarrito = this.cart.getItems().find(i => i.id === p.id);
          if (enCarrito) {
            this.producto.cantidad = enCarrito.cantidad;
            this.nota = enCarrito.nota || '';
            if (enCarrito.extras) {
              this.ingredientes.forEach(ing => ing.incluido = enCarrito.extras!.includes(ing.nombre));
            }
          }
        },
        error: () => {
          alert('No se encontró el producto');
          this.router.navigate(['/cliente/cliente-home']);
        }
      });
    }
  }

  guardarCambios() {
    const actualizado: CartItem = {
      id: this.producto.id,
      nombre: this.producto.nombre,
      precio: this.producto.precio,
      cantidad: this.producto.cantidad,
      extras: this.ingredientes.filter(i => i.incluido).map(i => i.nombre),
      nota: this.nota
    };
    this.cart.updateItem(actualizado);
    alert('✅ Pedido actualizado');
    this.router.navigate(['/cliente/carrito']);
  }

  agregarAlCarrito() {
    const nuevo: CartItem = {
      id: this.producto.id,
      nombre: this.producto.nombre,
      precio: this.producto.precio,
      cantidad: this.producto.cantidad,
      extras: this.ingredientes.filter(i => i.incluido).map(i => i.nombre),
      nota: this.nota
    };
    this.cart.addItem(nuevo);
    alert('🛒 Producto agregado');
    this.router.navigate(['/cliente/carrito']);
  }
}
