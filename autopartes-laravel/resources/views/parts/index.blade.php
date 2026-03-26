@extends('layouts.app')
@section('title', 'Catálogo de Autopartes')

@section('content')
<div class="d-flex justify-content-between align-items-center mb-4">
  <h3 class="fw-bold mb-0">
    <i class="bi bi-grid-fill me-2 text-warning"></i>Catálogo de Autopartes
  </h3>
  @if(session('user'))
  <a href="{{ route('orders.create') }}" class="btn btn-warning">
    <i class="bi bi-cart-plus me-1"></i>Hacer Pedido
  </a>
  @endif
</div>

<div class="row row-cols-1 row-cols-md-3 g-4">
  @forelse($parts as $part)
  <div class="col">
    <div class="card h-100 border-0 shadow-sm">
      <div class="card-body">
        <div class="d-flex justify-content-between">
          <span class="badge bg-secondary mb-2">{{ $part['category'] ?? 'General' }}</span>
          @if($part['stock_quantity'] <= 5)
            <span class="badge bg-danger">Stock bajo</span>
          @endif
        </div>
        <h5 class="card-title fw-bold">{{ $part['name'] }}</h5>
        <p class="text-muted small mb-1"><code>{{ $part['sku'] }}</code>
          @if($part['brand']) · {{ $part['brand'] }} @endif
        </p>
        <p class="card-text small text-muted">
          {{ Str::limit($part['description'] ?? '', 80) }}
        </p>
      </div>
      <div class="card-footer bg-white d-flex justify-content-between align-items-center">
        <span class="h5 fw-bold text-success mb-0">${{ number_format($part['price'], 2) }}</span>
        <span class="text-muted small">
          <i class="bi bi-box-seam me-1"></i>{{ $part['stock_quantity'] }} uds.
        </span>
      </div>
    </div>
  </div>
  @empty
  <div class="col-12">
    <div class="alert alert-info">No hay autopartes disponibles.</div>
  </div>
  @endforelse
</div>
@endsection
