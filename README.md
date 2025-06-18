# Henko Bot 🤖🛍️

**Henko Bot** es una solución automatizada para negocios de indumentaria, diseñada especialmente para **Henko Lencería**. Este bot permite extraer productos automáticamente desde la tienda online y enviar contenido promocional atractivo (copy + imagen) a Telegram e Instagram.

## Características principales

- 🔍 Scraping inteligente de productos desde [Tienda Nube](https://henkolenceria.mitiendanube.com/)
- 🛒 Detección de nombre, marca, precio, imagen, stock y categoría
- ✨ Generación automática de copys virales para Instagram
- 📩 Envío de productos automáticamente a un grupo o canal de Telegram
- 🕐 Configuración de horario diario para envíos automáticos
- 📊 Registro y estadísticas de productos enviados

## Archivos importantes

| Archivo | Descripción |
|--------|-------------|
| `henko_bot.py` | Lógica principal del bot. Scraping, generación de copy, y envío a Telegram |
| `setup.py` | Script de configuración inicial: dependencias, token, horarios |
| `start.py` | Interfaz de uso rápido con menú interactivo |
| `test_telegram.py` | Prueba conexión con bot de Telegram y envío de mensaje |
| `config.json` | Archivo de configuración generado automáticamente (token, horario, etc.) |

## Requisitos

- Python 3.8+
- Paquetes: `requests`, `beautifulsoup4`, `schedule`, etc.

Instalación de dependencias:
```bash
pip install -r requirements.txt
```

## Uso rápido

```bash
# Configuración inicial (token, horario, etc.)
python setup.py

# Ejecutar una vez para test
python henko_bot.py --test

# Ejecutar bot 24/7
python henko_bot.py
```

## Créditos

Desarrollado por **Alberto Damian Garcia** — [LinkedIn](https://www.linkedin.com/in/alberto-damian-garcia-603a20220/)  
Hecho con ❤️ en Buenos Aires, Argentina.

---

> 📦 Este proyecto forma parte de la automatización de contenidos de **Henko Lencería**.