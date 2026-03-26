@extends('layouts.app')
@section('title', 'Nuevo Pedido')

@section('content')
<div class="d-flex align-items-center mb-4">
  <a href="{{ route('parts.index') }}" class="btn btn-outline-secondary me-3">
    <i class="bi bi-arrow-left"></i>
  </a>
  <h3 class="fw-bold mb-0">
    <i class="bi bi-cart-plus-fill me-2 text-warning"></i>Nuevo Pedido
  </h3>
</div>

<div class="card border-0 shadow-sm">
  <div class="card-body">
    <p class="text-muted mb-4">Ingresa la cantidad deseada para cada autoparte. Deja en 0 las que no quieras.</p>

    <form method="POST" action="{{ route('orders.store') }}" id="orderForm">
      @csrf
      <div class="row g-3">
        @foreach($parts as $i => $part)
        <div class="col-md-6">
          <div class="card border h-100">
            <div class="card-body">
              <input type="hidden" name="items[{{ $i }}][part_id]" value="{{ $part['id'] }}">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <h6 class="fw-bold mb-0">{{ $part['name'] }}</h6>
                  <small class="text-muted"><code>{{ $part['sku'] }}</code>
                    @if($part['brand']) · {{ $part['brand'] }} @endif
                  </small>
                </div>
                <span class="h6 text-success fw-bold mb-0">${{ number_format($part['price'], 2) }}</span>
              </div>
              <hr class="my-2">
              <div class="d-flex align-items-center gap-2">
                <label class="form-label mb-0 small fw-semibold">Cantidad:</label>
                <input type="number" name="items[{{ $i }}][quantity]"
                       class="form-control form-control-sm qty-input"
                       style="width: 90px;"
                       min="0" max="{{ $part['stock_quantity'] }}"
                       value="0"
                       data-price="{{ $part['price'] }}"
                       onchange="calcTotal()">
                <small class="text-muted">/ {{ $part['stock_quantity'] }} disp.</small>
              </div>
            </div>
          </div>
        </div>
        @endforeach
      </div>

      <div class="d-flex justify-content-between align-items-center mt-4 pt-3 border-top">
        <div>
          <span class="text-muted">Total estimado:</span>
          <span class="h4 fw-bold text-success ms-2" id="totalDisplay">$0.00</span>
        </div>
        <button type="submit" class="btn btn-warning fw-bold px-4">
          <i class="bi bi-check-lg me-1"></i>Realizar Pedido
        </button>
      </div>
    </form>
  </div>
</div>
@endsection

@section('scripts')
<script>
function calcTotal() {
  let total = 0;
  document.querySelectorAll('.qty-input').forEach(input => {
    const qty   = parseInt(input.value) || 0;
    const price = parseFloat(input.dataset.price) || 0;
    total += qty * price;
  });
  document.getElementById('totalDisplay').textContent = '$' + total.toFixed(2);
}
</script>
@endsection
