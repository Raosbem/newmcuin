<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class OrdersController extends Controller
{
    private string $apiUrl;

    public function __construct()
    {
        $this->apiUrl = env('API_URL', 'http://api:8000/api/v1');
    }

    private function token(): string
    {
        return session('api_token', '');
    }

    // ── Historial de mis pedidos ───────────────────────────────────────────────

    public function index()
    {
        $resp   = Http::withToken($this->token())
            ->get("{$this->apiUrl}/orders", ['limit' => 50]);
        $orders = $resp->successful() ? $resp->json() : [];
        return view('orders.index', compact('orders'));
    }

    // ── Detalle de un pedido ───────────────────────────────────────────────────

    public function show(string $id)
    {
        $resp = Http::withToken($this->token())
            ->get("{$this->apiUrl}/orders/{$id}");
        if ($resp->failed()) {
            return redirect()->route('orders.index')->with('error', 'Pedido no encontrado.');
        }
        $order = $resp->json();
        return view('orders.show', compact('order'));
    }

    // ── Formulario de nuevo pedido ─────────────────────────────────────────────

    public function create()
    {
        $resp  = Http::withToken($this->token())
            ->get("{$this->apiUrl}/parts", ['limit' => 100]);
        $parts = $resp->successful() ? $resp->json() : [];
        return view('orders.create', compact('parts'));
    }

    // ── Crear pedido ───────────────────────────────────────────────────────────

    public function store(Request $request)
    {
        $request->validate([
            'items'             => 'required|array|min:1',
            'items.*.part_id'   => 'required|string',
            'items.*.quantity'  => 'required|integer|min:1',
        ]);

        // Filtrar items con quantity > 0
        $items = collect($request->items)
            ->filter(fn($i) => isset($i['quantity']) && (int)$i['quantity'] > 0)
            ->map(fn($i) => [
                'part_id'  => $i['part_id'],
                'quantity' => (int)$i['quantity'],
            ])
            ->values()
            ->toArray();

        if (empty($items)) {
            return back()->with('error', 'Debes seleccionar al menos una autoparte.');
        }

        $resp = Http::withToken($this->token())
            ->post("{$this->apiUrl}/orders", ['items' => $items]);

        if ($resp->failed()) {
            $detail = $resp->json('detail') ?? 'Error al crear el pedido.';
            return back()->with('error', $detail);
        }

        $order = $resp->json();
        return redirect()->route('orders.show', $order['id'])
            ->with('success', 'Pedido creado exitosamente.');
    }

    // ── Cancelar pedido ────────────────────────────────────────────────────────

    public function cancel(string $id)
    {
        $resp = Http::withToken($this->token())
            ->patch("{$this->apiUrl}/orders/{$id}/cancel");

        if ($resp->failed()) {
            $detail = $resp->json('detail') ?? 'No se pudo cancelar el pedido.';
            return redirect()->route('orders.show', $id)->with('error', $detail);
        }

        return redirect()->route('orders.show', $id)
            ->with('success', 'Pedido cancelado.');
    }

    // ── Descargar PDF del pedido ───────────────────────────────────────────────

    public function pdf(string $id)
    {
        $resp = Http::withToken($this->token())
            ->get("{$this->apiUrl}/orders/{$id}/pdf");

        if ($resp->failed()) {
            return redirect()->route('orders.show', $id)
                ->with('error', 'No se pudo descargar el PDF.');
        }

        $shortId = strtoupper(substr($id, 0, 8));
        return response($resp->body(), 200, [
            'Content-Type'        => 'application/pdf',
            'Content-Disposition' => "attachment; filename=pedido_{$shortId}.pdf",
        ]);
    }
}
