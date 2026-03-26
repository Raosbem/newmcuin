# ── Stage 1: crear proyecto Laravel con composer ──────────────────────────────
FROM composer:2.7 AS builder

WORKDIR /app
RUN composer create-project laravel/laravel . --prefer-dist --no-interaction --quiet

# Copiar archivos personalizados encima del scaffold de Laravel
COPY routes/        ./routes/
COPY app/           ./app/
COPY resources/views/ ./resources/views/

# ── Stage 2: runtime PHP + Apache ─────────────────────────────────────────────
FROM php:8.3-apache

# Extensiones necesarias
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends libzip-dev zip unzip libpng-dev libonig-dev && \
    docker-php-ext-install pdo pdo_mysql mbstring zip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Habilitar mod_rewrite
RUN a2enmod rewrite

# Configurar DocumentRoot a /public
ENV APACHE_DOCUMENT_ROOT=/var/www/html/public
RUN sed -ri -e 's!/var/www/html!${APACHE_DOCUMENT_ROOT}!g' \
      /etc/apache2/sites-available/*.conf && \
    sed -ri -e 's!/var/www/!${APACHE_DOCUMENT_ROOT}!g' \
      /etc/apache2/apache2.conf /etc/apache2/conf-available/*.conf

# AllowOverride para .htaccess de Laravel
RUN echo '<Directory ${APACHE_DOCUMENT_ROOT}>\n    AllowOverride All\n    Require all granted\n</Directory>' \
    >> /etc/apache2/apache2.conf

# Copiar proyecto desde el builder
COPY --from=builder /app /var/www/html

# Permisos de escritura
RUN chown -R www-data:www-data /var/www/html/storage \
                                /var/www/html/bootstrap/cache && \
    chmod -R 775 /var/www/html/storage \
                  /var/www/html/bootstrap/cache

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80
ENTRYPOINT ["/entrypoint.sh"]
