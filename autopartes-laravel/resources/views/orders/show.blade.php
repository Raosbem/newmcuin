@extends('layouts.app')
@section('title', 'Pedido ' . strtoupper(substr($order['id'], 0, 8)))

@section('content')
@php
  $colors = ['pending'=>'warning','confirmed'=>'info','shipped'=>'primary',
             'delivered'=>'success','cancelled'=>'danger'];
@endphp

<div class="d-flex align-items-center mb-4">
  <a href="{{ route('orders.index') }}" class="btn btn-outline-secondary me-3">
    <i class="bi bi-arrow-left"></i>
  </a>
  <h3 class="fw-bold mb-0">
    <i class="bi bi-bag-fill me-2 text-warning"></i>
    Pedido <code>{{ strtoupper(substr($order['id'], 0, 8)) }}</code>
  </h3>
</div>

<div class="row g-3">
  <!-- Resumen -->
  <div class="col-md-4">
    <div class="card border-0 shadow-sm">
      <div class="card-header bg-white fw-semibold">Información del Pedido</div>
      <div class="card-body">
        <dl class="mb-0">
          <dt class="small text-muted">Estado</dt>
          <dd>
            <span class="badge bg-{{ $colors[$order['status']] ?? 'secondary' }} mb-2">
              {{ $order['status'] }}
            </span>
          </dd>
          <dt class="small text-muted">Total</dt>
          <dd class="h5 fw-bold text-success">${{ number_format($order['total_amount'], 2) }}</dd>
          <dt class="small text-muted">Fecha</dt>
          <dd>{{ substr($order['created_at'] ?? '', 0, 10) }}</dd>
        </dl>
      </div>
    </div>

    <!-- Acciones -->
    <div class="card border-0 shadow-sm mt-3">
      <div class="card-body d-grid gap-2">
        <!-- Descargar PDF -->
        <a href="{{ route('orders.pdf', $order['id']) }}" class="btn btn-outline-danger">
          <i class="bi bi-file-earmark-pdf me-1"></i>Descargar PDF
        </a>

        <!-- Cancelar -->
        @if(!in_array($order['status'], ['cancelled', 'shipped', 'delivered']))
        <form method="POST" action="{{ route('orders.cancel', $order['id']) }}"
              onsubmit="return confirm('¿Cancelar este pedido?')">
          @csrf
          <button type="submit" class="btn btn-outline-warning w-100">
            <i class="bi bi-x-circle me-1"></i>Cancelar Pedido
          </button>
        </form>
        @endif
      </div>
    </div>
  </div>

  <!-- Items -->
  <div class="col-md-8">
    <div class="card border-0 shadow-sm">
      <div class="card-header bg-white fw-semibold">Artículos</div>
      <div class="card-body p-0">
        <table class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th>Autoparte</th><th>Precio unit.</th><th>Cantidad</th><th>Subtotal</th>
            </tr>
          </thead>
          <tbody>
            @foreach($order['items'] as $item)
            <tr>
              <td><small><code>{{ strtoupper(substr($item['part_id'], 0, 8)) }}…</code></small></td>
              <td>${{ number_format($item['unit_price'], 2) }}</td>
              <td>{{ $item['quantity'] }}</td>
              <td class="fw-semibold">${{ number_format($item['subtotal'], 2) }}</td>
            </tr>
            @endforeach
          </tbody>
          <tfoot class="table-light">
            <tr>
              <td colspan="3" class="text-end fw-bold">TOTAL</td>
              <td class="fw-bold text-success">${{ number_format($order['total_amount'], 2) }}</td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  </div>
</div>
@endsection
