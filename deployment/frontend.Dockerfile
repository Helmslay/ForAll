# Build the frontend from the repository root:
# docker build -f app/Dockerfile -t sentinel-explorer-web:preview .
FROM node:24.22.3-bookworm-slim AS build

WORKDIR /workspace
COPY app/package.json app/package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY app/ ./app/
WORKDIR /workspace/app
RUN npm run build

FROM nginx:1.30.8-trixie AS runtime

COPY deployment/nginx/nginx.conf /etc/nginx/nginx.conf
COPY deployment/nginx/container.conf /etc/nginx/conf.d/default.conf
COPY --from=build /workspace/app/dist/ /usr/share/nginx/html/

# The static bundle is immutable at runtime; Nginx runs without root privileges.
RUN chown -R root:root /usr/share/nginx/html \
    && find /usr/share/nginx/html -type d -exec chmod 0555 {} + \
    && find /usr/share/nginx/html -type f -exec chmod 0444 {} +

USER 101:101
EXPOSE 8080
ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]
