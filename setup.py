
#!/usr/bin/env python3
"""
Script de configuración inicial para Henko Bot
"""

import json
import os
import subprocess
import sys

def instalar_dependencias():
    """Instala las dependencias necesarias"""
    print("📦 Instalando dependencias...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False

def configurar_telegram():
    """Ayuda al usuario a configurar Telegram"""
    print("\n🤖 Configuración de Telegram Bot")
    print("=" * 50)
    
    print("\n📋 Pasos para configurar tu bot de Telegram:")
    print("1. Abre Telegram y busca @BotFather")
    print("2. Envía el comando /newbot")
    print("3. Sigue las instrucciones para crear tu bot")
    print("4. Copia el token que te proporcione BotFather")
    
    token = input("\n🔑 Pega aquí el token de tu bot: ").strip()
    
    if not token or token == "8001862470:AAFOgN4EToHubIRjGgtMBW1HEvVf1ijS7n8":
        print("⚠️  Token no válido. Puedes configurarlo manualmente en config.json")
        return None, None
    
    print("\n📱 Para obtener tu Chat ID:")
    print(f"1. Envía un mensaje a tu bot desde Telegram")
    print(f"2. Visita: https://api.telegram.org/bot{token}/getUpdates")
    print("3. Busca el campo 'chat' -> 'id' en la respuesta")
    
    chat_id = input("\n🆔 Pega aquí tu Chat ID: ").strip()
    
    if not chat_id or chat_id == "1121116968":
        print("⚠️  Chat ID no válido. Puedes configurarlo manualmente en config.json")
        return token, None
    
    return token, chat_id

def actualizar_configuracion(token, chat_id):
    """Actualiza el archivo de configuración"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if token:
            config['telegram_token'] = token
        if chat_id:
            config['chat_id'] = chat_id
        
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print("✅ Configuración actualizada correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error actualizando configuración: {e}")
        return False

def probar_configuracion():
    """Prueba la configuración ejecutando el bot en modo test"""
    print("\n🧪 Probando configuración...")
    try:
        resultado = subprocess.run([sys.executable, "henko_bot.py", "--test"], 
                                 capture_output=True, text=True, timeout=30)
        
        if resultado.returncode == 0:
            print("✅ Prueba exitosa! El bot está funcionando correctamente")
            print("\n📋 Salida:")
            print(resultado.stdout)
        else:
            print("❌ Error en la prueba:")
            print(resultado.stderr)
            
    except subprocess.TimeoutExpired:
        print("⏱️  La prueba tomó demasiado tiempo. Verifica tu conexión a internet.")
    except Exception as e:
        print(f"❌ Error ejecutando prueba: {e}")

def main():
    print("🚀 Configuración inicial de Henko Bot")
    print("=" * 50)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('henko_bot.py'):
        print("❌ Error: No se encuentra henko_bot.py en el directorio actual")
        print("   Asegúrate de ejecutar este script desde el directorio del proyecto")
        return
    
    # Instalar dependencias
    if not instalar_dependencias():
        return
    
    # Configurar Telegram
    token, chat_id = configurar_telegram()
    
    # Actualizar configuración
    if token or chat_id:
        actualizar_configuracion(token, chat_id)
    
    # Configurar horario
    print("\n⏰ Configuración de horario")
    horario_actual = "09:00"
    
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            horario_actual = config.get('horario_envio', '09:00')
    except:
        pass
    
    print(f"Horario actual: {horario_actual}")
    nuevo_horario = input("🕐 Nuevo horario (HH:MM en formato 24h, Enter para mantener actual): ").strip()
    
    if nuevo_horario and ':' in nuevo_horario:
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            config['horario_envio'] = nuevo_horario
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"✅ Horario actualizado a {nuevo_horario}")
        except Exception as e:
            print(f"❌ Error actualizando horario: {e}")
    
    # Probar configuración si está completa
    if token and chat_id:
        probar = input("\n🧪 ¿Quieres probar la configuración ahora? (s/N): ").strip().lower()
        if probar in ['s', 'si', 'sí', 'y', 'yes']:
            probar_configuracion()
    
    print("\n🎉 Configuración completada!")
    print("\n📖 Comandos útiles:")
    print("  • Ejecutar una vez (test): python henko_bot.py --test")
    print("  • Iniciar bot automático: python henko_bot.py")
    print("  • Ver ayuda: python henko_bot.py --help")
    print("\n📝 Para editar la configuración manualmente: config.json")

if __name__ == "__main__":
    main()
