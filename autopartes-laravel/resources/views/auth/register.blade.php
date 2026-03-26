<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Registro — AutoPartes</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
  <style>
    body { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); min-height: 100vh; }
  </style>
</head>
<body class="d-flex align-items-center justify-content-center min-vh-100">
  <div class="card shadow-lg" style="width: 460px;">
    <div class="card-body p-5">
      <div class="text-center mb-4">
        <i class="bi bi-person-plus-fill display-4 text-warning"></i>
        <h2 class="fw-bold mt-2">Crear Cuenta</h2>
        <p class="text-muted">Portal de Clientes — AutoPartes</p>
      </div>

      @if($errors->any())
        <div class="alert alert-danger py-2">
          @foreach($errors->all() as $e)<div>{{ $e }}</div>@endforeach
        </div>
      @endif

      <form method="POST" action="{{ route('register') }}">
        @csrf
        <div class="mb-3">
          <label class="form-label fw-semibold">Nombre completo</label>
          <div class="input-group">
            <span class="input-group-text"><i class="bi bi-person"></i></span>
            <input type="text" name="full_name" class="form-control" required
                   value="{{ old('full_name') }}">
          </div>
        </div>
        <div class="mb-3">
          <label class="form-label fw-semibold">Email</label>
          <div class="input-group">
            <span class="input-group-text"><i class="bi bi-envelope"></i></span>
            <input type="email" name="email" class="form-control" required
                   value="{{ old('email') }}">
          </div>
        </div>
        <div class="mb-3">
          <label class="form-label fw-semibold">Contraseña</label>
          <div class="input-group">
            <span class="input-group-text"><i class="bi bi-lock"></i></span>
            <input type="password" name="password" class="form-control" required minlength="6">
          </div>
        </div>
        <div class="mb-4">
          <label class="form-label fw-semibold">Confirmar contraseña</label>
          <div class="input-group">
            <span class="input-group-text"><i class="bi bi-lock-fill"></i></span>
            <input type="password" name="password_confirmation" class="form-control" required>
          </div>
        </div>
        <button type="submit" class="btn btn-warning fw-bold w-100">
          <i class="bi bi-check-lg me-1"></i>Registrarme
        </button>
      </form>

      <hr class="my-3">
      <p class="text-center mb-0">
        ¿Ya tienes cuenta?
        <a href="{{ route('login') }}" class="fw-semibold">Inicia sesión</a>
      </p>
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
