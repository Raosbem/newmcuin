<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\PartsController;
use App\Http\Controllers\OrdersController;
use App\Http\Controllers\CartController;

// ── Públicas ──────────────────────────────────────────────────────────────────
Route::get('/', fn() => redirect()->route('parts.index'));

Route::get('/login',    [AuthController::class, 'showLogin'])->name('login');
Route::post('/login',   [AuthController::class, 'login']);
Route::get('/register', [AuthController::class, 'showRegister'])->name('register');
Route::post('/register',[AuthController::class, 'register']);
Route::post('/logout',  [AuthController::class, 'logout'])->name('logout');

// ── Catálogo (requiere auth) ───────────────────────────────────────────────────
Route::middleware('api.auth')->group(function () {
    Route::get('/catalog',       [PartsController::class, 'index'])->name('parts.index');
    Route::get('/catalog/{id}',  [PartsController::class, 'show'])->name('parts.show');

    Route::get('/cart',           [CartController::class, 'index'])->name('cart.index');
    Route::post('/cart/add',      [CartController::class, 'add'])->name('cart.add');
    Route::post('/cart/update',   [CartController::class, 'update'])->name('cart.update');
    Route::post('/cart/remove',   [CartController::class, 'remove'])->name('cart.remove');
    Route::post('/cart/checkout', [CartController::class, 'checkout'])->name('cart.checkout');

    Route::get('/orders',             [OrdersController::class, 'index'])->name('orders.index');
    Route::get('/orders/{id}',        [OrdersController::class, 'show'])->name('orders.show');
    Route::post('/orders/{id}/cancel',[OrdersController::class, 'cancel'])->name('orders.cancel');
    Route::get('/orders/{id}/pdf',    [OrdersController::class, 'pdf'])->name('orders.pdf');
});
