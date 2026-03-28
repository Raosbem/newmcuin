@extends('layouts.app')
@section('title', 'Catálogo de Autopartes')

@section('content')
<div class="mb-4">
  <h3 class="fw-bold mb-3">
    <i class="bi bi-grid-fill me-2 text-warning"></i>Catálogo de Autopartes
  </h3>

  {{-- Buscador y filtros --}}
  <form method="GET" action="{{ route('parts.index') }}" class="row g-2">
    <div class="col-md-5">
      <div class="input-group">
        <span class="input-group-text"><i class="bi bi-search"></i></span>
        <input type="text" name="search" class="form-control"
               placeholder="Buscar por nombre..."
               value="{{ request('search') }}">
      </div>
    </div>
    <div class="col-md-3">
      <select name="brand_id" class="form-select">
        <option value="">Todas las marcas</option>
        @foreach($brands as $b)
          <option value="{{ $b['id'] }}" {{ request('brand_id') == $b['id'] ? 'selected' : '' }}>
            {{ $b['name'] }}
          </option>
        @endforeach
      </select>
    </div>
    <div class="col-md-3">
      <select name="category_id" class="form-select">
        <option value="">Todas las categorías</option>
        @foreach($categories as $c)
          <option value="{{ $c['id'] }}" {{ request('category_id') == $c['id'] ? 'selected' : '' }}>
            {{ $c['name'] }}
          </option>
        @endforeach
      </select>
    </div>
    <div class="col-md-1 d-flex gap-1">
      <button type="submit" class="btn btn-warning flex-grow-1">
        <i class="bi bi-search"></i>
      </button>
      @if(request('search') || request('brand_id') || request('category_id'))
        <a href="{{ route('parts.index') }}" class="btn btn-outline-secondary" title="Limpiar filtros">
          <i class="bi bi-x-lg"></i>
        </a>
      @endif
    </div>
  </form>
</div>

@php $publicApiUrl = env('PUBLIC_API_URL', 'http://localhost:8000') @endphp

<div class="row row-cols-1 row-cols-md-3 g-4">
  @forelse($parts as $part)
  <div class="col">
    <div class="card h-100 border-0 shadow-sm">

      {{-- Imagen --}}
      @if(!empty($part['image_url']))
        <img src="{{ $publicApiUrl . $part['image_url'] }}"
             class="card-img-top" alt="{{ $part['name'] }}"
             style="height:180px;object-fit:cover;">
      @else
        <div class="d-flex align-items-center justify-content-center bg-light"
             style="height:180px;">
          <i class="bi bi-image text-muted" style="font-size:3rem;"></i>
        </div>
      @endif

      <div class="card-body">
        <div class="d-flex justify-content-between">
          <span class="badge bg-secondary mb-2">{{ $part['category'] ?? 'General' }}</span>
          @if($part['stock_quantity'] <= 5)
            <span class="badge bg-danger">Stock bajo</span>
          @endif
        </div>
        <h5 class="card-title fw-bold">{{ $part['name'] }}</h5>
        <p class="text-muted small mb-1">
          <code>{{ $part['sku'] }}</code>
          @if($part['brand']) · {{ $part['brand'] }} @endif
        </p>
        <p class="card-text small text-muted">
          {{ Str::limit($part['description'] ?? '', 80) }}
        </p>
      </div>

      <div class="card-footer bg-white">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <span class="h5 fw-bold text-success mb-0">${{ number_format($part['price'], 2) }}</span>
          <span class="text-muted small">
            <i class="bi bi-box-seam me-1"></i>{{ $part['stock_quantity'] }} uds.
          </span>
        </div>
        @if(session('user') && $part['stock_quantity'] > 0)
          @php $inCart = session('cart.'.$part['id']) @endphp
          <form method="POST" action="{{ route('cart.add') }}" class="d-flex gap-2 align-items-center">
            @csrf
            <input type="hidden" name="part_id" value="{{ $part['id'] }}">
            <input type="hidden" name="name"    value="{{ $part['name'] }}">
            <input type="hidden" name="sku"     value="{{ $part['sku'] }}">
            <input type="hidden" name="price"   value="{{ $part['price'] }}">
            <input type="hidden" name="stock"   value="{{ $part['stock_quantity'] }}">
            <input type="number" name="quantity" value="1" min="1"
                   max="{{ $part['stock_quantity'] }}"
                   class="form-control form-control-sm" style="width:70px">
            <button type="submit" class="btn btn-sm {{ $inCart ? 'btn-warning' : 'btn-outline-warning' }} fw-semibold flex-grow-1">
              <i class="bi bi-cart-plus me-1"></i>
              {{ $inCart ? 'En carrito ('.$inCart['quantity'].')' : 'Añadir al carrito' }}
            </button>
          </form>
        @elseif($part['stock_quantity'] <= 0)
          <button class="btn btn-sm btn-secondary w-100" disabled>Sin stock</button>
        @endif
      </div>
    </div>
  </div>
  @empty
  <div class="col-12">
    <div class="alert alert-info">
      No se encontraron autopartes.
      @if(request('search') || request('brand_id') || request('category_id'))
        <a href="{{ route('parts.index') }}">Ver todo el catálogo</a>
      @endif
    </div>
  </div>
  @endforelse
</div>
@endsection
