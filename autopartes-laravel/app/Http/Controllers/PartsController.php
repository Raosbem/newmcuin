<?php

namespace App\Http\Controllers;

use Illuminate\Support\Facades\Http;

class PartsController extends Controller
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

    public function index()
    {
        $resp  = Http::withToken($this->token())
            ->get("{$this->apiUrl}/parts", ['limit' => 100]);
        $parts = $resp->successful() ? $resp->json() : [];
        return view('parts.index', compact('parts'));
    }

    public function show(string $id)
    {
        $resp = Http::withToken($this->token())
            ->get("{$this->apiUrl}/parts/{$id}");
        if ($resp->failed()) {
            return redirect()->route('parts.index')->with('error', 'Autoparte no encontrada.');
        }
        $part = $resp->json();
        return view('parts.show', compact('part'));
    }
}
