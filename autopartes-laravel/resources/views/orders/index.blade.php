@extends('layouts.app')
@section('title', 'Mis Pedidos')

@section('content')
<div class="d-flex justify-content-between align-items-center mb-4">
  <h3 class="fw-bold mb-0">
    <i class="bi bi-bag-check-fill me-2 text-warning"></i>Mis Pedidos
  </h3>
  <a href="{{ route('cart.index') }}" class="btn btn-warning">
    <i class="bi bi-cart3 me-1"></i>Ir al carrito
  </a>
</div>

@php
  $colors = ['received'=>'warning','processing'=>'info','shipped'=>'primary',
             'delivered'=>'success','cancelled'=>'danger'];
  $labels = ['received'=>'Recibido','processing'=>'En proceso','shipped'=>'Enviado',
             'delivered'=>'Entregado','cancelled'=>'Cancelado'];
@endphp

@if(count($orders) === 0)
  <div class="alert alert-info">Aún no tienes pedidos. <a href="{{ route('parts.index') }}">Explora el catálogo</a>.</div>
@else
<div class="card border-0 shadow-sm">
  <div class="card-body p-0">
    <table class="table table-hover align-middle mb-0">
      <thead class="table-dark">
        <tr>
          <th>ID</th><th>Estado</th><th>Total</th><th>Fecha</th><th class="text-center">Acciones</th>
        </tr>
      </thead>
      <tbody>
        @foreach($orders as $o)
        <tr>
          <td><code>{{ strtoupper(substr($o['id'], 0, 8)) }}</code></td>
          <td>
            <span class="badge bg-{{ $colors[$o['status']] ?? 'secondary' }}">{{ $labels[$o['status']] ?? $o['status'] }}</span>
          </td>
          <td class="fw-semibold">${{ number_format($o['total_amount'], 2) }}</td>
          <td><small>{{ substr($o['created_at'] ?? '', 0, 10) }}</small></td>
          <td class="text-center">
            <a href="{{ route('orders.show', $o['id']) }}" class="btn btn-sm btn-outline-primary">
              <i class="bi bi-eye"></i> Ver
            </a>
          </td>
        </tr>
        @endforeach
      </tbody>
    </table>
  </div>
</div>
@endif
@endsection
