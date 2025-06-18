#!/usr/bin/env python3
"""
Script para probar la configuración de Telegram
"""

import requests
import json

def test_telegram_bot():
    """Prueba la configuración del bot de Telegram"""
    
    # Configuración
    bot_token = "8001862470:AAFOgN4EToHubIRjGgtMBW1HEvVf1ijS7n8"
    chat_id = "1121116968"
    
    print(f"🤖 Probando bot con token: {bot_token[:10]}...")
    print(f"📱 Chat ID: {chat_id}")
    
    # 1. Probar getMe - información del bot
    print("\n1️⃣ Probando getMe...")
    try:
        response = requests.get(f"https://api.telegram.org/bot{bot_token}/getMe")
        data = response.json()
        
        if data.get('ok'):
            bot_info = data['result']
            print(f"✅ Bot activo: {bot_info['first_name']} (@{bot_info.get('username', 'N/A')})")
        else:
            print(f"❌ Error en getMe: {data}")
            return False
    except Exception as e:
        print(f"❌ Error conectando con Telegram: {e}")
        return False
    
    # 2. Obtener updates para verificar chat_id
    print("\n2️⃣ Obteniendo updates...")
    try:
        response = requests.get(f"https://api.telegram.org/bot{bot_token}/getUpdates")
        data = response.json()
        
        if data.get('ok'):
            updates = data['result']
            if updates:
                print(f"📨 Encontrados {len(updates)} updates:")
                for update in updates[-3:]:  # Mostrar últimos 3
                    if 'message' in update:
                        msg = update['message']
                        chat = msg['chat']
                        print(f"   Chat ID: {chat['id']} | Tipo: {chat['type']} | Usuario: {chat.get('first_name', 'N/A')}")
            else:
                print("📭 No hay updates. Envía un mensaje al bot primero.")
        else:
            print(f"❌ Error obteniendo updates: {data}")
    except Exception as e:
        print(f"❌ Error obteniendo updates: {e}")
    
    # 3. Probar envío de mensaje
    print(f"\n3️⃣ Probando envío de mensaje al chat {chat_id}...")
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': '🧪 Prueba de configuración - Henko Bot\n\n✅ El bot está funcionando correctamente!'
        }
        
        response = requests.post(url, data=payload)
        data = response.json()
        
        if data.get('ok'):
            print("✅ Mensaje enviado exitosamente!")
            print(f"📱 ID del mensaje: {data['result']['message_id']}")
            return True
        else:
            print(f"❌ Error enviando mensaje: {data}")
            error_desc = data.get('description', '')
            
            if 'chat not found' in error_desc:
                print("\n💡 Posibles soluciones:")
                print("   1. Verifica que el chat_id sea correcto")
                print("   2. Asegúrate de haber enviado un mensaje al bot primero")
                print("   3. El bot debe poder iniciar conversaciones contigo")
                print("   4. Verifica que no hayas bloqueado el bot")
            
            return False
    except Exception as e:
        print(f"❌ Error enviando mensaje: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Test de Configuración de Telegram - Henko Bot")
    print("=" * 60)
    
    success = test_telegram_bot()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ¡Configuración exitosa! El bot está listo para usar.")
    else:
        print("⚠️  Hay problemas con la configuración. Revisa los errores arriba.")
        print("\n📋 Pasos para solucionar:")
        print("1. Abre Telegram y busca tu bot")
        print("2. Envía /start al bot")
        print("3. Vuelve a ejecutar este test")
