# Email Validator Tool

Una herramienta profesional de línea de comandos para validar correos electrónicos mediante múltiples capas de verificación, incluyendo sintaxis, DNS/MX, dominios desechables, cuentas de rol, lista de rebotes, y opcionalmente, detección de catch-all y verificación SMTP.

## Stack Tecnológico

- **Python 3.8+**: Lenguaje base
- **email-validator**: Validación de sintaxis RFC
- **dnspython**: Verificación de registros MX
- **disposable-email-domains**: Detección de dominios desechables
- **email-role-detector**: Detección de cuentas de rol
- **aiosmtplib**: Verificación SMTP asíncrona
- **Typer**: Interfaz de línea de comandos
- **Pydantic**: Validación de datos y configuración
- **Loguru**: Sistema de logging
- **SQLite**: Base de datos local para lista de rebotes
- **pytest**: Framework de testing
- **Black/isort/flake8**: Formateo y linting

## Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/email-validator-tool.git
   cd email-validator-tool
   ```

2. Crear y activar entorno virtual:
   ```bash
   python -m venv venv
   # En Windows:
   .\venv\Scripts\activate
   # En Unix/MacOS:
   source venv/bin/activate
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Configuración

1. Copiar el archivo de ejemplo:
   ```bash
   cp .env.example .env
   ```

2. Ajustar las variables en `.env`:
   ```
   CSV_INPUT_PATH=emails.csv
   CSV_OUTPUT_PATH=results.csv
   MAX_CONCURRENT_CONNECTIONS=10
   PER_DOMAIN_DELAY_SECONDS=5.0
   SMTP_TIMEOUT=10
   ENABLE_CATCH_ALL=False
   ENABLE_SMTP=False
   ```

## Uso

Validar una lista de correos:
```bash
python -m email_validator_tool.cli input.csv output.csv
```

Habilitar verificación catch-all (fase 2):
```bash
python -m email_validator_tool.cli input.csv output.csv --enable-catch-all
```

Habilitar verificación SMTP (fase 3):
```bash
python -m email_validator_tool.cli input.csv output.csv --enable-smtp
```

## Capas de Validación

1. **Sintaxis (RFC)**
   - Verifica que el correo cumple con la especificación RFC
   - Usa email-validator para validación robusta

2. **DNS/MX**
   - Comprueba que el dominio existe
   - Verifica que tiene registros MX válidos
   - Usa dnspython para resolución DNS

3. **Dominios Desechables**
   - Detecta dominios de correo temporal
   - Usa disposable-email-domains dataset

4. **Cuentas de Rol**
   - Identifica cuentas genéricas (admin, info, etc.)
   - Usa email-role-detector y patrones personalizados

5. **Lista de Rebotes**
   - Verifica contra base de datos local de rebotes
   - Almacena historial en SQLite

6. **Catch-all** (Opcional)
   - Detecta dominios que aceptan cualquier correo
   - Requiere verificación SMTP

7. **SMTP** (Opcional)
   - Verifica existencia real del buzón
   - Requiere conexión directa al servidor

## Gestión de Riesgos

⚠️ **Advertencia**: Las verificaciones SMTP y catch-all son consideradas de alto riesgo:

- Pueden resultar en el bloqueo de tu IP por los servidores de correo
- Deben usarse con precaución y configuración adecuada
- Recomendaciones:
  - Usar delays entre verificaciones (PER_DOMAIN_DELAY_SECONDS)
  - Limitar conexiones concurrentes (MAX_CONCURRENT_CONNECTIONS)
  - Configurar timeouts apropiados (SMTP_TIMEOUT)
  - Considerar usar un VPS dedicado
  - Implementar rotación de IPs si es necesario

## Contribución

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.
