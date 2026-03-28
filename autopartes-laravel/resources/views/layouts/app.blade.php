<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>@yield('title', 'Macuin Autopartes') — Tienda</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
  <style>
    body { background-color: #f4f6f9; }
    .navbar-brand { font-weight: 700; }
  </style>
</head>
<body>

<nav class="navbar navbar-expand-lg navbar-dark bg-dark shadow-sm">
  <div class="container">
    <a class="navbar-brand" href="{{ route('parts.index') }}">
      <i class="bi bi-car-front-fill me-1 text-warning"></i>Macuin Autopartes
    </a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#nav">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="nav">
      <ul class="navbar-nav me-auto">
        <li class="nav-item">
          <a class="nav-link" href="{{ route('parts.index') }}">
            <i class="bi bi-grid me-1"></i>Catálogo
          </a>
        </li>
        @if(session('user'))
        <li class="nav-item">
          <a class="nav-link" href="{{ route('orders.index') }}">
            <i class="bi bi-bag-check me-1"></i>Mis Pedidos
          </a>
        </li>
        @endif
      </ul>
      <ul class="navbar-nav">
        @if(session('user'))
          @php $cartCount = collect(session('cart', []))->sum('quantity') @endphp
          <li class="nav-item me-2">
            <a class="nav-link position-relative" href="{{ route('cart.index') }}">
              <i class="bi bi-cart3 fs-5"></i>
              @if($cartCount > 0)
                <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-warning text-dark">
                  {{ $cartCount }}
                </span>
              @endif
            </a>
          </li>
          <li class="nav-item">
            <span class="nav-link text-light">
              <i class="bi bi-person-circle me-1"></i>{{ session('user.full_name') }}
            </span>
          </li>
          <li class="nav-item">
            <form method="POST" action="{{ route('logout') }}" class="d-inline">
              @csrf
              <button type="submit" class="btn btn-link nav-link text-danger p-0 ms-2">
                <i class="bi bi-box-arrow-right"></i> Salir
              </button>
            </form>
          </li>
        @else
          <li class="nav-item">
            <a class="nav-link" href="{{ route('login') }}">
              <i class="bi bi-box-arrow-in-right"></i> Login
            </a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="{{ route('register') }}">
              <i class="bi bi-person-plus"></i> Registrarse
            </a>
          </li>
        @endif
      </ul>
    </div>
  </div>
</nav>

<div class="container py-4">
  @if(session('success'))
    <div class="alert alert-success alert-dismissible fade show">
      {{ session('success') }}
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
  @endif
  @if(session('error'))
    <div class="alert alert-danger alert-dismissible fade show">
      {{ session('error') }}
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
  @endif
  @if($errors->any())
    <div class="alert alert-danger alert-dismissible fade show">
      <ul class="mb-0">@foreach($errors->all() as $e)<li>{{ $e }}</li>@endforeach</ul>
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
  @endif

  @yield('content')
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
@yield('scripts')
</body>
</html>
