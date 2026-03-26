<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class AuthController extends Controller
{
    private string $apiUrl;

    public function __construct()
    {
        $this->apiUrl = env('API_URL', 'http://api:8000/api/v1');
    }

    // ── Login ──────────────────────────────────────────────────────────────────

    public function showLogin()
    {
        return view('auth.login');
    }

    public function login(Request $request)
    {
        $request->validate([
            'email'    => 'required|email',
            'password' => 'required',
        ]);

        $resp = Http::post("{$this->apiUrl}/auth/login", [
            'email'    => $request->email,
            'password' => $request->password,
        ]);

        if ($resp->failed()) {
            return back()->withErrors(['email' => 'Credenciales inválidas.']);
        }

        $token = $resp->json('access_token');

        // Obtener datos del usuario
        $meResp = Http::withToken($token)->get("{$this->apiUrl}/auth/me");
        if ($meResp->failed()) {
            return back()->withErrors(['email' => 'Error al obtener datos del usuario.']);
        }

        $user = $meResp->json();
        if ($user['role'] !== 'customer') {
            return back()->withErrors(['email' => 'Este portal es solo para clientes externos.']);
        }

        session([
            'api_token' => $token,
            'user'      => $user,
        ]);

        return redirect()->route('parts.index')->with('success', "Bienvenido, {$user['full_name']}!");
    }

    // ── Register ───────────────────────────────────────────────────────────────

    public function showRegister()
    {
        return view('auth.register');
    }

    public function register(Request $request)
    {
        $request->validate([
            'full_name' => 'required|string|max:100',
            'email'     => 'required|email',
            'password'  => 'required|min:6|confirmed',
        ]);

        $resp = Http::post("{$this->apiUrl}/users/register", [
            'full_name' => $request->full_name,
            'email'     => $request->email,
            'password'  => $request->password,
        ]);

        if ($resp->failed()) {
            $detail = $resp->json('detail') ?? 'Error al registrarse.';
            return back()->withErrors(['email' => $detail]);
        }

        return redirect()->route('login')
            ->with('success', 'Cuenta creada. Ahora puedes iniciar sesión.');
    }

    // ── Logout ─────────────────────────────────────────────────────────────────

    public function logout()
    {
        session()->flush();
        return redirect()->route('login')->with('success', 'Sesión cerrada.');
    }
}
