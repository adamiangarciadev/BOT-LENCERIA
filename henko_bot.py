#!/usr/bin/env python3
"""
Henko Lencería - Bot Automatizado para Telegram e Instagram
Aplicación que extrae productos de la tienda y envía notificaciones diarias.
"""

import requests
import random
import schedule
import time
import logging
import json
from datetime import datetime
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import os
from dataclasses import dataclass
import re

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('henko_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class Producto:
    """Clase para representar un producto de la tienda"""
    id: str
    nombre: str
    marca: str
    precio_original: str
    precio_oferta: str
    stock: str
    link: str
    imagen_url: str
    colores: List[str]
    talles: List[str]
    categoria: str

class HenkoScraper:
    """Scraper para extraer productos de Henko Lencería"""
    
    def __init__(self):
        self.base_url = "https://henkolenceria.mitiendanube.com"
        self.productos_url = f"{self.base_url}/productos/?mpage=200"  # Página fija
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def obtener_total_paginas(self) -> int:
        """Obtiene el número total de páginas de productos"""
        try:
            response = self.session.get(self.productos_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar indicadores de paginación
            pagination_info = soup.find_all(['span', 'div'], class_=re.compile(r'pagination|page'))
            
            # Por ahora asumimos 10 páginas basado en los 577 productos observados
            # Esto se puede optimizar detectando la paginación real
            total_productos = 577
            productos_por_pagina = 60  # Estimación basada en observación
            total_paginas = (total_productos + productos_por_pagina - 1) // productos_por_pagina
            
            logger.info(f"Total estimado de páginas: {total_paginas}")
            return total_paginas
            
        except Exception as e:
            logger.error(f"Error obteniendo total de páginas: {e}")
            return 10  # Valor por defecto
    
    def extraer_productos_pagina(self, pagina: int = 1) -> List[Producto]:
        """Extrae productos de una página específica - TODOS los productos, no solo una marca"""
        productos = []
        
        try:
            url = f"{self.productos_url}?mpage={pagina}" if pagina > 1 else self.productos_url
            logger.info(f"Scrapeando página {pagina}: {url}")
            
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar TODOS los enlaces de productos sin filtrar por marca
            enlaces_productos = soup.find_all('a', href=re.compile(r'/productos/[^/]+'))
            
            logger.info(f"Encontrados {len(enlaces_productos)} enlaces de productos potenciales")
            
            productos_validos = []
            for enlace in enlaces_productos:
                try:
                    texto_enlace = enlace.get_text(strip=True)
                    href = enlace.get('href', '')
                    
                    # Filtrar enlaces que no son productos reales
                    if (not href or 
                        '/productos/' not in href or
                        'categoria' in href.lower() or
                        'buscar' in href.lower() or
                        len(texto_enlace.strip()) < 3):
                        continue
                    
                    # Verificar que el texto tiene contenido real de producto
                    if texto_enlace and len(texto_enlace.strip()) > 0:
                        # Intentar extraer producto sin importar la marca
                        producto = self._extraer_producto_desde_enlace(enlace, soup)
                        if producto and self._es_producto_valido(producto):
                            productos_validos.append(producto)
                            logger.debug(f"Producto extraído: {producto.nombre}")
                            
                except Exception as e:
                    logger.warning(f"Error extrayendo producto desde enlace: {e}")
                    continue
            
            # Eliminar duplicados por ID o link
            productos_unicos = {}
            for producto in productos_validos:
                # Usar el link como clave única si no hay ID válido
                clave = producto.id if producto.id.isdigit() else producto.link
                if clave not in productos_unicos:
                    productos_unicos[clave] = producto
            
            productos = list(productos_unicos.values())
            logger.info(f"Extraídos {len(productos)} productos únicos de la página {pagina}")
            
            # Mostrar variedad de marcas encontradas para verificar
            marcas_encontradas = set(p.marca for p in productos if p.marca)
            if marcas_encontradas:
                logger.info(f"Marcas encontradas: {', '.join(list(marcas_encontradas)[:5])}")
            
        except Exception as e:
            logger.error(f"Error scrapeando página {pagina}: {e}")
        
        return productos
    
    def _es_producto_valido(self, producto: Producto) -> bool:
        """Verifica si un producto es válido para enviar"""
        if not producto:
            return False
        
        # Filtros básicos de validación
        nombre_lower = producto.nombre.lower()
        
        # Excluir elementos que no son productos
        exclusiones = [
            'categoria', 'buscar', 'filtro', 'ordenar', 'página',
            'menu', 'navegacion', 'footer', 'header'
        ]
        
        if any(exc in nombre_lower for exc in exclusiones):
            return False
        
        # Debe tener nombre mínimo
        if len(producto.nombre.strip()) < 3:
            return False
        
        # Debe tener link válido
        if not producto.link or 'productos/' not in producto.link:
            return False
        
        return True
    
    def _extraer_producto_desde_enlace(self, enlace, soup_pagina) -> Optional[Producto]:
        """Extrae información del producto desde un enlace - CUALQUIER marca"""
        try:
            href = enlace.get('href', '')
            if not href:
                return None
            
            # Construir link completo
            if href.startswith('/'):
                link_completo = f"{self.base_url}{href}"
            elif href.startswith('http'):
                link_completo = href
            else:
                link_completo = f"{self.base_url}/productos/{href}"
            
            texto_enlace = enlace.get_text(strip=True)
            
            # Limpiar texto del enlace (remover caracteres extra que pueden venir del scraping)
            texto_limpio = re.sub(r'[^\w\s|$.,\-áéíóúñ]+', ' ', texto_enlace)
            texto_limpio = re.sub(r'\s+', ' ', texto_limpio).strip()
            
            # Extraer ID y marca de diferentes formatos posibles
            producto_id = "0"
            marca = "Producto"
            
            if '|' in texto_limpio:
                # Formato "ID | Marca" (como Marcela Koury)
                partes = texto_limpio.split('|', 1)
                id_candidato = partes[0].strip()
                if id_candidato.isdigit():
                    producto_id = id_candidato
                    marca = partes[1].split('$')[0].strip()  # Tomar solo hasta el precio
                    texto_enlace = f"{producto_id} | {marca}"
                else:
                    # Si no hay ID numérico, usar el nombre completo
                    producto_id = "0" 
                    marca = texto_limpio.split('$')[0].strip()
                    texto_enlace = marca
            else:
                # Intentar extraer ID del href o usar el nombre como está
                match = re.search(r'(\d+)', href)
                if match:
                    producto_id = match.group(1)
                else:
                    # Generar ID único basado en el texto
                    producto_id = str(hash(texto_limpio.lower()) % 10000)
                
                marca = texto_limpio.split('$')[0].strip()
                texto_enlace = marca if marca else "Producto sin nombre"
            
            # Si la marca está vacía, intentar extraer del href
            if not marca or marca == "Producto":
                # Intentar extraer marca del URL
                url_parts = href.split('/')
                for part in url_parts:
                    if part and part != 'productos' and not part.isdigit():
                        marca = part.replace('-', ' ').title()
                        break
                
                if not marca or marca == "Producto":
                    marca = "Henko Lencería"
            
            # Buscar información adicional en el contexto del enlace
            contenedor = enlace.find_parent(['div', 'article', 'section', 'li'])
            
            # Extraer precios - buscar en varios niveles
            precio_original = "Consultar"
            precio_oferta = "Consultar"
            
            # Buscar precios en el contenedor
            if contenedor:
                # Buscar elementos que contengan signo de peso
                elementos_precio = contenedor.find_all(string=re.compile(r'\$[\d,.]+'))
                if elementos_precio:
                    precios_encontrados = [p.strip() for p in elementos_precio if '$' in p and len(p.strip()) > 1]
                    if len(precios_encontrados) >= 2:
                        precio_original = precios_encontrados[0]
                        precio_oferta = precios_encontrados[1]
                    elif len(precios_encontrados) == 1:
                        precio_oferta = precios_encontrados[0]
                        precio_original = precio_oferta
            
            # Extraer imagen
            imagen_url = ""
            img = enlace.find('img') or (contenedor.find('img') if contenedor else None)
            if img:
                src = img.get('src', '') or img.get('data-src', '') or img.get('data-original', '')
                if src and 'data:image/gif' not in src:  # Ignorar placeholders
                    if src.startswith('http'):
                        imagen_url = src
                    elif src.startswith('/'):
                        imagen_url = f"{self.base_url}{src}"
            
            # Extraer información de stock
            stock = "Disponible"
            if contenedor:
                # Buscar textos que indiquen stock
                stock_texts = contenedor.find_all(string=re.compile(r'(stock|quedan|último|agotado)', re.I))
                if stock_texts:
                    stock = stock_texts[0].strip()
                elif "sin stock" in contenedor.get_text().lower():
                    stock = "Sin stock"
            
            # Determinar categoría basada en el texto o contexto
            categoria = "Lencería"
            texto_completo = (texto_enlace + " " + (contenedor.get_text() if contenedor else "")).lower()
            
            if any(cat in texto_completo for cat in ['soutien', 'corpiño', 'bra']):
                categoria = "Soutien"
            elif any(cat in texto_completo for cat in ['body', 'bodysuit']):
                categoria = "Body"
            elif any(cat in texto_completo for cat in ['conjunto', 'set']):
                categoria = "Conjunto"
            elif any(cat in texto_completo for cat in ['bombacha', 'calzón']):
                categoria = "Bombacha"
            elif any(cat in texto_completo for cat in ['media', 'calcetín']):
                categoria = "Medias"
            elif any(cat in texto_completo for cat in ['camisón', 'pijama']):
                categoria = "Pijamas"
            
            return Producto(
                id=producto_id,
                nombre=texto_enlace,
                marca=marca,
                precio_original=precio_original,
                precio_oferta=precio_oferta,
                stock=stock,
                link=link_completo,
                imagen_url=imagen_url,
                colores=[],
                talles=[],
                categoria=categoria
            )
            
        except Exception as e:
            logger.warning(f"Error extrayendo producto desde enlace: {e}")
            return None
    
    def _extraer_producto_desde_tarjeta(self, tarjeta) -> Optional[Producto]:
        """Extrae información del producto desde una tarjeta"""
        try:
            # Buscar enlace principal
            enlace = tarjeta.find('a', href=re.compile(r'/productos/'))
            if not enlace:
                return None
            
            return self._extraer_producto_desde_enlace(enlace, tarjeta)
            
        except Exception as e:
            logger.warning(f"Error extrayendo producto desde tarjeta: {e}")
            return None
    
    def obtener_productos_aleatorios(self, cantidad: int = 5) -> List[Producto]:
        """Obtiene una muestra aleatoria de productos de diferentes páginas"""
        total_paginas = self.obtener_total_paginas()
        productos_totales = []
        
        # Seleccionar páginas aleatorias para obtener variedad
        paginas_a_scrapear = random.sample(range(1, min(total_paginas + 1, 6)), min(5, total_paginas))
        
        for pagina in paginas_a_scrapear:
            productos_pagina = self.extraer_productos_pagina(pagina)
            productos_totales.extend(productos_pagina)
            time.sleep(1)  # Evitar sobrecarga del servidor
        
        # Seleccionar productos aleatorios
        if len(productos_totales) >= cantidad:
            return random.sample(productos_totales, cantidad)
        else:
            return productos_totales

class TelegramBot:
    """Cliente para enviar mensajes a Telegram"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
    
    def enviar_mensaje(self, texto: str) -> bool:
        """Envía un mensaje de texto a Telegram"""
        try:
            # Telegram tiene límite de 4096 caracteres
            if len(texto) > 4000:
                texto = texto[:4000] + "..."
            
            url = f"{self.api_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': texto,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code != 200:
                logger.error(f"Error Telegram {response.status_code}: {response.text}")
                # Intentar sin Markdown si falla
                data['parse_mode'] = 'HTML'
                response = requests.post(url, data=data)
                
                if response.status_code != 200:
                    # Último intento sin formato
                    del data['parse_mode']
                    response = requests.post(url, data=data)
            
            response.raise_for_status()
            logger.info("Mensaje enviado exitosamente a Telegram")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando mensaje a Telegram: {e}")
            return False
    
    def enviar_foto_con_texto(self, imagen_url: str, caption: str) -> bool:
        """Envía una foto con descripción a Telegram"""
        try:
            url = f"{self.api_url}/sendPhoto"
            data = {
                'chat_id': self.chat_id,
                'photo': imagen_url,
                'caption': caption,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            logger.info("Foto enviada exitosamente a Telegram")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando foto a Telegram: {e}")
            # Fallback: enviar solo el texto
            return self.enviar_mensaje(caption)

class CopyGenerator:
    """Generador de copy viral para Instagram"""
    
    def __init__(self):
        self.emojis_trending = ["🔥", "✨", "💖", "🤩", "😍", "💕", "🌟", "💎", "🦋", "🌸", "💫", "👑", "🔥🔥", "💋"]
        
        # Hashtags trending actualizados para 2025
        self.hashtags_trending = [
            "#viral", "#fyp", "#trending", "#explore", "#viralreels", 
            "#instagramreels", "#reelsviral", "#explorar", "#tendencia",
            "#2025trends", "#musthave", "#hottrend", "#instafamous"
        ]
        
        self.hashtags_lenceria = [
            "#lencería", "#lingerie", "#underwear", "#ropainteriorfemenina",
            "#sensual", "#elegante", "#sexylingerie", "#intimates",
            "#bodypositive", "#confidence", "#empowerment", "#selflove"
        ]
        
        self.hashtags_marca = [
            "#henko", "#henkolenceria", "#argentina", "#madeinargentina", 
            "#calidad", "#comodidad", "#style", "#marcaargentina"
        ]
        
        self.hashtags_shopping = [
            "#tiendaonline", "#shopping", "#compraonline", "#moda",
            "#fashion", "#style", "#outfit", "#ootd", "#shoponline",
            "#enviosatodoelpais", "#cuotas", "#descuentos"
        ]
    
    def generar_copy_instagram(self, producto: Producto) -> str:
        """Genera copy viral y atractivo para Instagram"""
        
        # Hooks llamativos para captar atención
        hooks_virales = [
            "🚨 ESTO ES LO QUE NECESITABAS Y NO LO SABÍAS",
            "🔥 ATENCIÓN: Esto se está agotando rápido",
            "😍 OBSESIONADA con esta pieza nueva",
            "✨ POV: Encontraste LA pieza perfecta",
            "🤩 TODOS van a preguntar dónde lo compraste",
            "💖 PLOT TWIST: Te vas a enamorar",
            "🌟 BREAKING NEWS: Llegó tu nueva obsesión",
            "👑 QUEEN BEHAVIOR: Usar esto y sentirte INCREÍBLE"
        ]
        
        # Calls to action virales
        ctas_virales = [
            "💬 COMENTA tu emoji favorito",
            "❤️ DOBLE TAP si también te obsesionaste",
            "📲 COMPARTE con tu bestie que necesita esto",
            "🛒 GUARDÁ este post para comprarlo después",
            "👀 SEGUINOS para más must-haves como este",
            "🔄 COMPARTE en tu story si te gustó"
        ]
        
        hook = random.choice(hooks_virales)
        cta = random.choice(ctas_virales)
        
        # Descripción del producto con énfasis
        nombre_destacado = f"✨ {producto.nombre.upper()} ✨"
        
        # Crear urgencia si hay stock limitado
        mensaje_stock = ""
        if "stock" in producto.stock.lower() or "queda" in producto.stock.lower():
            mensaje_stock = f"\n⚡ {producto.stock} - ¡NO TE QUEDES SIN EL TUYO!"
        else:
            mensaje_stock = "\n✅ DISPONIBLE AHORA"
        
        # Beneficios destacados
        beneficios = [
            "💕 Comodidad TODO EL DÍA",
            "🔥 Elegancia que se siente",
            "✨ Calidad PREMIUM",
            "👑 Te hace sentir REINA",
            "💖 Perfecto para cualquier ocasión"
        ]
        beneficio_random = random.choice(beneficios)
        
        # Crear mix de hashtags estratégicos (reducido para evitar límites)
        hashtags_seleccionados = (
            random.sample(self.hashtags_trending, 3) +
            random.sample(self.hashtags_lenceria, 2) +
            random.sample(self.hashtags_marca, 2) +
            random.sample(self.hashtags_shopping, 2)
        )
        
        # Agregar hashtags específicos del producto y marca
        if "soutien" in producto.nombre.lower():
            hashtags_seleccionados.extend(["#soutien", "#bra"])
        elif "body" in producto.nombre.lower():
            hashtags_seleccionados.extend(["#body", "#bodysuit"])
        elif "conjunto" in producto.nombre.lower():
            hashtags_seleccionados.extend(["#conjunto", "#set"])
        elif "bombacha" in producto.nombre.lower():
            hashtags_seleccionados.extend(["#bombacha"])
        
        # Agregar hashtag de la marca específica si es diferente a las genéricas
        if producto.marca and len(producto.marca) > 3:
            marca_hash = producto.marca.lower().replace(' ', '').replace('-', '')
            if marca_hash not in ['henko', 'henkolenceria', 'producto']:
                hashtags_seleccionados.append(f"#{marca_hash}")
        
        # Tomar los primeros 15 hashtags para mantener el mensaje conciso
        random.shuffle(hashtags_seleccionados)
        hashtags_finales = hashtags_seleccionados[:15]
        hashtags_texto = " ".join(hashtags_finales)
        
        # Construir copy viral más conciso
        copy = f"""{hook}

{nombre_destacado}

{beneficio_random}
{mensaje_stock}

💰 {producto.precio_oferta}
🚚 Envíos a todo el país

{cta}

{hashtags_texto}

#henkolenceria #tiendaonline"""
        
        return copy

class HenkoBot:
    """Aplicación principal que coordina todas las funciones"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config = self.cargar_configuracion(config_file)
        self.scraper = HenkoScraper()
        
        # Inicializar bot de Telegram si está configurado
        if self.config.get('telegram_token') and self.config.get('chat_id'):
            self.telegram_bot = TelegramBot(
                self.config['telegram_token'],
                self.config['chat_id']
            )
        else:
            self.telegram_bot = None
            logger.warning("Bot de Telegram no configurado")
        
        self.copy_generator = CopyGenerator()
    
    def cargar_configuracion(self, config_file: str) -> Dict:
        """Carga la configuración desde archivo JSON"""
        config_default = {
            "telegram_token": "TU_BOT_TOKEN_AQUI",
            "chat_id": "TU_CHAT_ID_AQUI",
            "horario_envio": "09:00",
            "productos_por_dia": 1,
            "log_level": "INFO"
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge con config por defecto
                    config_default.update(config)
            else:
                # Crear archivo de configuración por defecto
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config_default, f, indent=2, ensure_ascii=False)
                logger.info(f"Archivo de configuración creado: {config_file}")
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
        
        return config_default
    
    def procesar_producto_diario(self):
        """Función principal que se ejecuta diariamente"""
        try:
            logger.info("Iniciando proceso diario de selección de producto...")
            
            # Obtener productos aleatorios
            productos = self.scraper.obtener_productos_aleatorios(5)
            
            if not productos:
                logger.error("No se pudieron obtener productos")
                return
            
            # Filtrar productos válidos (más flexible para todas las marcas)
            productos_validos = [
                p for p in productos 
                if (p.id and len(p.nombre) > 3 and 
                    "categoria" not in p.nombre.lower() and
                    "buscar" not in p.nombre.lower() and
                    "filtro" not in p.nombre.lower() and
                    p.link and "/productos/" in p.link)
            ]
            
            if not productos_validos:
                logger.error("No se encontraron productos válidos")
                return
            
            # Seleccionar un producto al azar
            producto_seleccionado = random.choice(productos_validos)
            logger.info(f"Producto seleccionado: {producto_seleccionado.nombre}")
            
            # Generar copy para Instagram
            copy_instagram = self.copy_generator.generar_copy_instagram(producto_seleccionado)
            
            # Preparar mensaje para Telegram
            mensaje_telegram = f"""🛍️ **PRODUCTO DEL DÍA - HENKO LENCERÍA**

{copy_instagram}

🔗 **Link directo**: {producto_seleccionado.link}

---
*Copy listo para Instagram ⬆️*
*¡Solo copiá y pegá!* 📋"""
            
            # Enviar por Telegram
            if self.telegram_bot:
                if producto_seleccionado.imagen_url:
                    exito = self.telegram_bot.enviar_foto_con_texto(
                        producto_seleccionado.imagen_url,
                        mensaje_telegram
                    )
                else:
                    exito = self.telegram_bot.enviar_mensaje(mensaje_telegram)
                
                if exito:
                    logger.info("Producto del día enviado exitosamente")
                else:
                    logger.error("Error enviando producto del día")
            else:
                logger.warning("Telegram bot no configurado - mostrando mensaje:")
                print(mensaje_telegram)
            
            # Guardar registro del producto enviado
            self.guardar_registro_producto(producto_seleccionado, copy_instagram)
            
        except Exception as e:
            logger.error(f"Error en proceso diario: {e}")
    
    def guardar_registro_producto(self, producto: Producto, copy: str):
        """Guarda un registro del producto enviado"""
        try:
            registro = {
                "fecha": datetime.now().isoformat(),
                "producto": {
                    "id": producto.id,
                    "nombre": producto.nombre,
                    "link": producto.link,
                    "precio": producto.precio_oferta
                },
                "copy_generado": copy
            }
            
            # Cargar registros existentes
            registros_file = "productos_enviados.json"
            registros = []
            
            if os.path.exists(registros_file):
                with open(registros_file, 'r', encoding='utf-8') as f:
                    registros = json.load(f)
            
            registros.append(registro)
            
            # Mantener solo los últimos 100 registros
            if len(registros) > 100:
                registros = registros[-100:]
            
            # Guardar registros actualizados
            with open(registros_file, 'w', encoding='utf-8') as f:
                json.dump(registros, f, indent=2, ensure_ascii=False)
            
            logger.info("Registro de producto guardado")
            
        except Exception as e:
            logger.error(f"Error guardando registro: {e}")
    
    def configurar_horario(self):
        """Configura el horario de ejecución automática"""
        horario = self.config.get('horario_envio', '09:00')
        schedule.every().day.at(horario).do(self.procesar_producto_diario)
        logger.info(f"Horario configurado: todos los días a las {horario}")
    
    def ejecutar_inmediatamente(self):
        """Ejecuta el proceso inmediatamente (para testing)"""
        logger.info("Ejecutando proceso inmediatamente...")
        self.procesar_producto_diario()
    
    def iniciar_bot(self):
        """Inicia el bot en modo automático"""
        logger.info("Iniciando Henko Bot...")
        self.configurar_horario()
        
        logger.info("Bot configurado. Esperando horario programado...")
        logger.info("Presiona Ctrl+C para detener el bot")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Revisar cada minuto
        except KeyboardInterrupt:
            logger.info("Bot detenido por el usuario")

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Henko Lencería Bot para Telegram e Instagram')
    parser.add_argument('--test', action='store_true', help='Ejecutar una vez inmediatamente para testing')
    parser.add_argument('--config', default='config.json', help='Archivo de configuración')
    
    args = parser.parse_args()
    
    # Crear instancia del bot
    bot = HenkoBot(args.config)
    
    if args.test:
        bot.ejecutar_inmediatamente()
    else:
        bot.iniciar_bot()

if __name__ == "__main__":
    main()
