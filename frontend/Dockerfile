# ─────────────────────────────────────────────────────────────
# Stage 1 — build the static bundle
# ─────────────────────────────────────────────────────────────
FROM node:22-alpine AS build

WORKDIR /app

# Install dependencies from the lockfile first for layer caching.
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY . .

# Build-time configuration. Empty base URL => same-origin "/api/...", which the
# nginx stage proxies to the backend. No secret is ever passed here: everything
# in a VITE_* variable ends up readable in the browser bundle.
ARG VITE_API_BASE_URL=""
ARG VITE_API_TIMEOUT_MS=45000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL \
    VITE_API_TIMEOUT_MS=$VITE_API_TIMEOUT_MS

RUN npm run build

# ─────────────────────────────────────────────────────────────
# Stage 2 — serve
# ─────────────────────────────────────────────────────────────
FROM nginx:1.27-alpine AS runtime

# Where /api/ is proxied. Overridden per environment.
ENV API_UPSTREAM=http://api:8000

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template

# Run unprivileged on a non-restricted port.
RUN sed -i 's/user  nginx;/# user directive removed: container runs as nginx/' /etc/nginx/nginx.conf \
    && sed -i 's,/var/run/nginx.pid,/tmp/nginx.pid,' /etc/nginx/nginx.conf \
    && chown -R nginx:nginx /usr/share/nginx/html /var/cache/nginx /etc/nginx/conf.d

USER nginx
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -qO- http://127.0.0.1:8080/healthz >/dev/null 2>&1 || exit 1

CMD ["nginx", "-g", "daemon off;"]
