<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class CartController extends Controller
{
    private string $apiUrl;

    public function __construct()
    {
        $this->apiUrl = env('API_URL', 'http://api:8000/api/v1');
    }

    public function index()
    {
        $cart  = session('cart', []);
        $total = collect($cart)->sum(fn($i) => $i['price'] * $i['quantity']);
        return view('cart.index', compact('cart', 'total'));
    }

    public function add(Request $request)
    {
        $request->validate([
            'part_id'  => 'required|string',
            'quantity' => 'required|integer|min:1',
        ]);

        $partId   = $request->part_id;
        $quantity = (int) $request->quantity;
        $cart     = session('cart', []);

        if (isset($cart[$partId])) {
            $cart[$partId]['quantity'] = min(
                $cart[$partId]['quantity'] + $quantity,
                $cart[$partId]['stock']
            );
        } else {
            $cart[$partId] = [
                'part_id'  => $partId,
                'name'     => $request->name,
                'sku'      => $request->sku,
                'price'    => (float) $request->price,
                'stock'    => (int) $request->stock,
                'quantity' => $quantity,
            ];
        }

        session(['cart' => $cart]);
        return back()->with('success', "«{$request->name}» agregado al carrito.");
    }

    public function update(Request $request)
    {
        $request->validate([
            'part_id'  => 'required|string',
            'quantity' => 'required|integer|min:1',
        ]);

        $cart = session('cart', []);
        if (isset($cart[$request->part_id])) {
            $cart[$request->part_id]['quantity'] = min(
                (int) $request->quantity,
                $cart[$request->part_id]['stock']
            );
            session(['cart' => $cart]);
        }

        return back();
    }

    public function remove(Request $request)
    {
        $cart = session('cart', []);
        unset($cart[$request->part_id]);
        session(['cart' => $cart]);
        return back()->with('success', 'Producto eliminado del carrito.');
    }

    public function checkout()
    {
        $cart = session('cart', []);

        if (empty($cart)) {
            return redirect()->route('cart.index')->with('error', 'El carrito está vacío.');
        }

        $items = collect($cart)
            ->map(fn($i) => ['part_id' => $i['part_id'], 'quantity' => $i['quantity']])
            ->values()
            ->toArray();

        $resp = Http::withToken(session('api_token', ''))
            ->post("{$this->apiUrl}/orders", ['items' => $items]);

        if ($resp->failed()) {
            $detail = $resp->json('detail') ?? 'Error al crear el pedido.';
            return back()->with('error', is_array($detail) ? json_encode($detail) : $detail);
        }

        session()->forget('cart');
        $order = $resp->json();
        return redirect()->route('orders.show', $order['id'])
            ->with('success', '¡Pedido realizado con éxito!');
    }
}
