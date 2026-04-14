<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
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

    public function index(Request $request)
    {
        $params = ['limit' => 100];
        if ($request->filled('search'))      $params['search']      = $request->query('search');
        if ($request->filled('brand_id'))    $params['brand_id']    = $request->query('brand_id');
        if ($request->filled('category_id')) $params['category_id'] = $request->query('category_id');

        $partsResp      = Http::withToken($this->token())->get("{$this->apiUrl}/parts/", $params);
        $brandsResp     = Http::withToken($this->token())->get("{$this->apiUrl}/brands/");
        $categoriesResp = Http::withToken($this->token())->get("{$this->apiUrl}/categories/");

        $parts      = $partsResp->successful()      ? ($partsResp->json()      ?? []) : [];
        $brands     = $brandsResp->successful()     ? ($brandsResp->json()     ?? []) : [];
        $categories = $categoriesResp->successful() ? ($categoriesResp->json() ?? []) : [];

        return view('parts.index', compact('parts', 'brands', 'categories'));
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
