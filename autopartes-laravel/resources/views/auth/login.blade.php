<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Login — AutoPartes</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
  <style>
    body { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); min-height: 100vh; }
  </style>
</head>
<body class="d-flex align-items-center justify-content-center min-vh-100">
  <div class="card shadow-lg" style="width: 420px;">
    <div class="card-body p-5">
      <div class="text-center mb-4">
        <i class="bi bi-car-front-fill display-4 text-warning"></i>
        <h2 class="fw-bold mt-2">AutoPartes</h2>
        <p class="text-muted">Portal de Clientes</p>
      </div>

      @if(session('success'))
        <div class="alert alert-success py-2">{{ session('success') }}</div>
      @endif
      @if($errors->any())
        <div class="alert alert-danger py-2">
          @foreach($errors->all() as $e)<div>{{ $e }}</div>@endforeach
        </div>
      @endif

      <form method="POST" action="{{ route('login') }}">
        @csrf
        <div class="mb-3">
          <label class="form-label fw-semibold">Email</label>
          <div class="input-group">
            <span class="input-group-text"><i class="bi bi-envelope"></i></span>
            <input type="email" name="email" class="form-control" required autofocus
                   value="{{ old('email') }}">
          </div>
        </div>
        <div class="mb-4">
          <label class="form-label fw-semibold">Contraseña</label>
          <div class="input-group">
            <span class="input-group-text"><i class="bi bi-lock"></i></span>
            <input type="password" name="password" class="form-control" required>
          </div>
        </div>
        <button type="submit" class="btn btn-warning fw-bold w-100">
          <i class="bi bi-box-arrow-in-right me-1"></i>Iniciar Sesión
        </button>
      </form>

      <hr class="my-3">
      <p class="text-center mb-0">
        ¿No tienes cuenta?
        <a href="{{ route('register') }}" class="fw-semibold">Regístrate aquí</a>
      </p>
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
