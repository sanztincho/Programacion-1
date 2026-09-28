import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { Header } from '../../../components/shared/header/header';
import { Auth } from '../../../services/auth';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';

@Component({
  selector: 'app-login',
  imports: [CommonModule, RouterLink, Header, ReactiveFormsModule],
  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class Login {

  loginForm: FormGroup;
  mensajeError: string = '';
  enviando: boolean = false;

  constructor(
    private authservice: Auth,
    private router: Router,
    private formBuilder: FormBuilder
  ) {
    // Formulario reactivo: cada campo con su valor inicial y sus validadores
    this.loginForm = this.formBuilder.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required]
    });
  }

  login() {
    this.enviando = true;
    this.mensajeError = '';
    this.authservice.login(this.loginForm.value).subscribe({
      next: (response: LoginResponse) => {
        // Se guarda el token: desde ahora viaja en el header Authorization de cada petición
        localStorage.setItem('token', response.access_token);
        localStorage.setItem('email', response.email);
        this.enviando = false;
        // Cada rol arranca en su propia pantalla
        this.router.navigateByUrl(this.authservice.rutaInicio());
      },
      error: (error) => {
        this.enviando = false;
        localStorage.removeItem('token');
        localStorage.removeItem('email');
        if (error.status === 401) {
          this.mensajeError = 'Email o contraseña incorrectos.';
        } else if (error.status === 403) {
          this.mensajeError = error.error?.message || 'Tu cuenta está bloqueada.';
        } else if (error.status === 0) {
          this.mensajeError = 'No se pudo conectar con el servidor. ¿Está corriendo el backend?';
        } else {
          this.mensajeError = 'Error al iniciar sesión. Intentá nuevamente.';
        }
      }
    });
  }

  logout() {
    this.authservice.logout();
  }

  submit() {
    if (this.loginForm.valid) {
      this.login();
    } else {
      this.loginForm.markAllAsTouched();
      this.mensajeError = 'Completá un email válido y la contraseña.';
    }
  }
}
