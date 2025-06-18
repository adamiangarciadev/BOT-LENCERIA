#!/usr/bin/env python3
"""
Script de inicio rápido para Henko Bot
Proporciona una interfaz simple para usar el bot
"""

import os
import sys
import json
import subprocess
from datetime import datetime

def mostrar_banner():
    """Muestra el banner de inicio"""
    print("🛍️" + "="*60 + "🛍️")
    print("           HENKO BOT - AUTOMATIZACIÓN TELEGRAM & INSTAGRAM")
    print("🛍️" + "="*60 + "🛍️")
    print()

def verificar_configuracion():
    """Verifica si la configuración está completa"""
    if not os.path.exists('config.json'):
        return False, "Archivo config.json no encontrado"
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        if config.get('telegram_token', '').startswith('TU_BOT_TOKEN'):
            return False, "Token de Telegram no configurado"
        
        if config.get('chat_id', '').startswith('TU_CHAT_ID'):
            return False, "Chat ID no configurado"
        
        return True, "Configuración completa"
        
    except Exception as e:
        return False, f"Error leyendo configuración: {e}"

def mostrar_menu():
    """Muestra el menú principal"""
    print("📋 MENÚ PRINCIPAL")
    print("-" * 40)
    print("1️⃣  Ejecutar UNA VEZ (prueba)")
    print("2️⃣  Iniciar modo AUTOMÁTICO (24/7)")
    print("3️⃣  Probar configuración de Telegram")
    print("4️⃣  Configurar bot (setup inicial)")
    print("5️⃣  Ver último producto enviado")
    print("6️⃣  Ver estadísticas")
    print("7️⃣  Ayuda y documentación")
    print("0️⃣  Salir")
    print("-" * 40)

def ejecutar_test():
    """Ejecuta el bot en modo test"""
    print("🧪 Ejecutando prueba del bot...")
    print("⏱️  Esto puede tomar unos segundos...\n")
    
    try:
        resultado = subprocess.run([sys.executable, "henko_bot.py", "--test"], 
                                 capture_output=True, text=True, timeout=60)
        
        if resultado.returncode == 0:
            print("✅ ¡Prueba exitosa!")
            print("\n📱 El bot debería haber enviado un mensaje a Telegram.")
            print("📋 Revisa tu chat para confirmar.")
        else:
            print("❌ Error en la prueba:")
            print(resultado.stderr)
            
        return resultado.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏱️ La prueba tomó demasiado tiempo. Verifica tu conexión.")
        return False
    except Exception as e:
        print(f"❌ Error ejecutando prueba: {e}")
        return False

def iniciar_automatico():
    """Inicia el bot en modo automático"""
    print("🤖 Iniciando bot en modo automático...")
    print("⏰ El bot enviará productos según el horario configurado.")
    print("🛑 Presiona Ctrl+C para detener\n")
    
    try:
        subprocess.run([sys.executable, "henko_bot.py"])
    except KeyboardInterrupt:
        print("\n🛑 Bot detenido por el usuario.")
    except Exception as e:
        print(f"❌ Error ejecutando bot: {e}")

def probar_telegram():
    """Prueba la configuración de Telegram"""
    print("📡 Probando configuración de Telegram...\n")
    
    try:
        subprocess.run([sys.executable, "test_telegram.py"])
    except Exception as e:
        print(f"❌ Error probando Telegram: {e}")

def ejecutar_setup():
    """Ejecuta la configuración inicial"""
    print("⚙️ Iniciando configuración inicial...\n")
    
    try:
        subprocess.run([sys.executable, "setup.py"])
    except Exception as e:
        print(f"❌ Error en configuración: {e}")

def ver_ultimo_producto():
    """Muestra información del último producto enviado"""
    try:
        if not os.path.exists('productos_enviados.json'):
            print("📭 No hay productos enviados aún.")
            return
        
        with open('productos_enviados.json', 'r', encoding='utf-8') as f:
            registros = json.load(f)
        
        if not registros:
            print("📭 No hay productos enviados aún.")
            return
        
        ultimo = registros[-1]
        print("📱 ÚLTIMO PRODUCTO ENVIADO")
        print("-" * 40)
        print(f"📅 Fecha: {ultimo['fecha']}")
        print(f"🏷️ Producto: {ultimo['producto']['nombre']}")
        print(f"💰 Precio: {ultimo['producto']['precio']}")
        print(f"🔗 Link: {ultimo['producto']['link']}")
        print("\n📝 Copy generado:")
        print("-" * 40)
        print(ultimo['copy_generado'])
        
    except Exception as e:
        print(f"❌ Error leyendo registros: {e}")

def ver_estadisticas():
    """Muestra estadísticas de uso"""
    try:
        stats = {
            'total_enviados': 0,
            'ultimo_envio': 'Nunca',
            'productos_unicos': 0
        }
        
        if os.path.exists('productos_enviados.json'):
            with open('productos_enviados.json', 'r', encoding='utf-8') as f:
                registros = json.load(f)
            
            stats['total_enviados'] = len(registros)
            if registros:
                stats['ultimo_envio'] = registros[-1]['fecha']
                productos_ids = set(r['producto']['id'] for r in registros)
                stats['productos_unicos'] = len(productos_ids)
        
        # Verificar configuración
        config_ok, config_msg = verificar_configuracion()
        
        print("📊 ESTADÍSTICAS DEL BOT")
        print("-" * 40)
        print(f"✅ Configuración: {'OK' if config_ok else 'PENDIENTE'}")
        print(f"📤 Productos enviados: {stats['total_enviados']}")
        print(f"🔢 Productos únicos: {stats['productos_unicos']}")
        print(f"⏰ Último envío: {stats['ultimo_envio']}")
        
        if os.path.exists('henko_bot.log'):
            size = os.path.getsize('henko_bot.log')
            print(f"📝 Tamaño del log: {size} bytes")
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")

def mostrar_ayuda():
    """Muestra información de ayuda"""
    print("📖 AYUDA Y DOCUMENTACIÓN")
    print("-" * 40)
    print("🔧 Comandos principales:")
    print("   python henko_bot.py --test     (prueba única)")
    print("   python henko_bot.py            (modo automático)")
    print("   python test_telegram.py       (probar Telegram)")
    print("   python setup.py               (configuración inicial)")
    print()
    print("📁 Archivos importantes:")
    print("   config.json                   (configuración)")
    print("   productos_enviados.json       (historial)")
    print("   henko_bot.log                 (logs del sistema)")
    print()
    print("🆘 Solución de problemas:")
    print("   1. Verificar configuración con opción 3")
    print("   2. Revisar logs en henko_bot.log")
    print("   3. Ejecutar setup.py si hay errores")
    print()
    print("📚 Documentación completa: README.md")

def main():
    """Función principal del menú"""
    mostrar_banner()
    
    # Verificar configuración inicial
    config_ok, config_msg = verificar_configuracion()
    
    if not config_ok:
        print(f"⚠️  {config_msg}")
        print("🔧 Ejecuta la configuración inicial (opción 4) primero.\n")
    else:
        print(f"✅ {config_msg}\n")
    
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\n👉 Selecciona una opción (0-7): ").strip()
            print()
            
            if opcion == "0":
                print("👋 ¡Hasta luego!")
                break
            elif opcion == "1":
                ejecutar_test()
            elif opcion == "2":
                iniciar_automatico()
            elif opcion == "3":
                probar_telegram()
            elif opcion == "4":
                ejecutar_setup()
            elif opcion == "5":
                ver_ultimo_producto()
            elif opcion == "6":
                ver_estadisticas()
            elif opcion == "7":
                mostrar_ayuda()
            else:
                print("❌ Opción no válida. Selecciona un número del 0 al 7.")
            
            if opcion != "0":
                input("\nPresiona Enter para continuar...")
        except KeyboardInterrupt:
            print("\n🛑 Salida forzada por el usuario.")
            break   