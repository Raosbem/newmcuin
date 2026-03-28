@extends('layouts.app')
@section('title', 'Mi Carrito')

@section('content')
<div class="d-flex align-items-center mb-4 gap-3">
  <a href="{{ route('parts.index') }}" class="btn btn-outline-secondary">
    <i class="bi bi-arrow-left"></i>
  </a>
  <h3 class="fw-bold mb-0">
    <i class="bi bi-cart3 me-2 text-warning"></i>Mi Carrito
  </h3>
</div>

@if(empty($cart))
  <div class="card border-0 shadow-sm">
    <div class="card-body text-center py-5">
      <i class="bi bi-cart-x display-3 text-muted"></i>
      <p class="text-muted mt-3 mb-4">Tu carrito está vacío.</p>
      <a href="{{ route('parts.index') }}" class="btn btn-warning">
        <i class="bi bi-grid me-1"></i>Ver catálogo
      </a>
    </div>
  </div>
@else
  <div class="card border-0 shadow-sm mb-4">
    <div class="card-body p-0">
      <table class="table table-hover align-middle mb-0">
        <thead class="table-dark">
          <tr>
            <th>Producto</th>
            <th>Precio unitario</th>
            <th style="width:140px">Cantidad</th>
            <th>Subtotal</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          @foreach($cart as $item)
          <tr>
            <td>
              <div class="fw-semibold">{{ $item['name'] }}</div>
              <small class="text-muted"><code>{{ $item['sku'] }}</code></small>
            </td>
            <td>${{ number_format($item['price'], 2) }}</td>
            <td>
              <form method="POST" action="{{ route('cart.update') }}" class="d-flex align-items-center gap-1">
                @csrf
                <input type="hidden" name="part_id" value="{{ $item['part_id'] }}">
                <input type="number" name="quantity" value="{{ $item['quantity'] }}"
                       min="1" max="{{ $item['stock'] }}"
                       class="form-control form-control-sm" style="width:70px"
                       onchange="this.form.submit()">
              </form>
            </td>
            <td class="fw-bold">${{ number_format($item['price'] * $item['quantity'], 2) }}</td>
            <td class="text-end">
              <form method="POST" action="{{ route('cart.remove') }}">
                @csrf
                <input type="hidden" name="part_id" value="{{ $item['part_id'] }}">
                <button type="submit" class="btn btn-sm btn-outline-danger"
                        onclick="return confirm('¿Eliminar del carrito?')">
                  <i class="bi bi-trash"></i>
                </button>
              </form>
            </td>
          </tr>
          @endforeach
        </tbody>
      </table>
    </div>
  </div>

  <div class="d-flex justify-content-between align-items-center">
    <a href="{{ route('parts.index') }}" class="btn btn-outline-secondary">
      <i class="bi bi-grid me-1"></i>Seguir comprando
    </a>
    <div class="d-flex align-items-center gap-4">
      <div class="text-end">
        <div class="text-muted small">Total estimado</div>
        <div class="h3 fw-bold text-success mb-0">${{ number_format($total, 2) }}</div>
      </div>
      <form method="POST" action="{{ route('cart.checkout') }}">
        @csrf
        <button type="submit" class="btn btn-warning btn-lg fw-bold px-4">
          <i class="bi bi-check-lg me-1"></i>Confirmar pedido
        </button>
      </form>
    </div>
  </div>
@endif
@endsection
