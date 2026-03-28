@extends('layouts.app')
@section('title', $part['name'])

@section('content')
<div class="d-flex align-items-center mb-4">
  <a href="{{ route('parts.index') }}" class="btn btn-outline-secondary me-3">
    <i class="bi bi-arrow-left"></i>
  </a>
  <h3 class="fw-bold mb-0">{{ $part['name'] }}</h3>
</div>

<div class="row g-3">
  <div class="col-md-6">
    <div class="card border-0 shadow-sm">
      <div class="card-body">
        <span class="badge bg-secondary mb-2">{{ $part['category'] ?? 'General' }}</span>
        <h4 class="fw-bold">{{ $part['name'] }}</h4>
        <p class="text-muted"><code>{{ $part['sku'] }}</code> @if($part['brand']) · {{ $part['brand'] }} @endif</p>
        <p>{{ $part['description'] ?? 'Sin descripción.' }}</p>
        <hr>
        <div class="d-flex justify-content-between align-items-center">
          <span class="h3 fw-bold text-success">${{ number_format($part['price'], 2) }}</span>
          <span class="text-muted"><i class="bi bi-box-seam me-1"></i>{{ $part['stock_quantity'] }} disponibles</span>
        </div>
        @if(session('user'))
        <a href="{{ route('cart.index') }}" class="btn btn-warning w-100 mt-3">
          <i class="bi bi-cart3 me-1"></i>Ver carrito
        </a>
        @else
        <a href="{{ route('login') }}" class="btn btn-outline-warning w-100 mt-3">
          Inicia sesión para comprar
        </a>
        @endif
      </div>
    </div>
  </div>
</div>
@endsection
