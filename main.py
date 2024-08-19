from telegram import Update

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from datetime import datetime

import aiohttp # type: ignore

import re

from urllib.parse import quote



# Inisialisasi

print("Bot Jalan...")

token = "7122138934:AAFxfRizWE5rcwntaPFbHbNJmxhIGVuk5EA"

apiUrl = "http://10.24.24.7:7557"

ssidKe = "4"





# log pesan

async def log_pesan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"{waktu} 📥 dari {update.message.from_user.username}: {update.message.text}")



# start

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    await update.message.reply_text(f'Terima kasih {update.effective_user.first_name}, Telah menggunakan bot ini')



# list

async def listDevice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    async with aiohttp.ClientSession() as session:

        async with session.get(f'{apiUrl}/devices') as response:

            if response.status == 200:

                data = await response.json()

                devices = []

                for index, device in enumerate(data):

                    device_id = device.get('_id', 'Unknown ID')

                    device_info = device.get('_deviceId', {})

                    

                    manufacturer_full = device_info.get('_Manufacturer', 'Unknown Manufacturer')

                    manufacturer = manufacturer_full.split()[0] if manufacturer_full != 'Unknown Manufacturer' else manufacturer_full

                    serial_number = device_info.get('_ProductClass', 'Unknown')

                    

                    devices.append(f"{index+1}. {manufacturer} {serial_number}")



                devices_text = "\n".join(devices)

                await update.message.reply_text(

                    f'Perangkat Yang Terhubung:\n\n{devices_text}', 

                    parse_mode='Markdown'

                )

            else:

                await update.message.reply_text(f'Gagal mengambil data dari API. Status: {response.status}')

                

# Ubah ssid dan pw

async def handle_Wifi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    text = update.message.text.strip()

    

    # Ganti SSID

    match_ssid = re.match(r'^US\.(\S+)\.(.*)$', text)  

    if match_ssid:

        device_id = quote(match_ssid.group(1))

        wifi_name = match_ssid.group(2)

        

        async with aiohttp.ClientSession() as session:

            payload = {

                "name": "setParameterValues",

                "parameterValues": [

                         [f"InternetGatewayDevice.LANDevice.1.WLANConfiguration.{ssidKe}.SSID", wifi_name, "xsd:string"]

#                     [f'Device.WiFi.SSID.{ssidKe}.SSID', wifi_name, "xsd:string"]  # parameter mikrotik

                ]

            }

            url = f'{apiUrl}/devices/{device_id}/tasks?connection_request'

            async with session.post(url, json=payload) as response:

              print(response)

                if response.status == 200 or response.status == 202:

                    await update.message.reply_text(f'Nama WiFi berhasil diubah menjadi: *{wifi_name}*', parse_mode='Markdown')

                elif response.status == 404:

                    await update.message.reply_text(f'ID perangkat tidak ditemukan.')

                else:

                    print(response)

                    await update.message.reply_text(f'Gagal mengirim perubahan SSID WiFi.')

        return



    # Ganti Password

    match_pw = re.match(r'^UP\.(\S+)\.(.*)$', text)

    if match_pw:

        device_id = quote(match_pw.group(1))

        password = match_pw.group(2)

        

        if len(password) < 8:

            await update.message.reply_text(f'❌ Password minimal 8 karakter')

            return

        

        async with aiohttp.ClientSession() as session:

            payload = {

                "name": "setParameterValues",

                "parameterValues": [

                                    [f"InternetGatewayDevice.LANDevice.1.WLANConfiguration.{ssidKe}.PreSharedKey.1.PreSharedKey", password, "xsd:string"] 

#                     ["Device.WiFi.AccessPoint.1.Security.KeyPassphrase", password, "xsd:string"] # mikrotik

                ]

            }

            url = f'{apiUrl}/devices/{device_id}/tasks?connection_request'

            async with session.post(url, json=payload) as response:

                if response.status == 200 or response.status == 202:

                    await update.message.reply_text(f'Password WiFi berhasil diubah menjadi: *{password}*', parse_mode='Markdown')

                elif response.status == 404:

                    await update.message.reply_text(f'ID perangkat tidak ditemukan.')

                else:

                    print(response)

                    await update.message.reply_text(f'Gagal mengirim perubahan password WiFi.')

        return



    # Ganti SSID dan Password

    match_sspw = re.match(r'^USP\.(\S+)\.(.*)\.(.*)$', text) 

    if match_sspw:

        device_id = quote(match_sspw.group(1))

        wifi_name = match_sspw.group(2)

        password = match_sspw.group(3)

        

        if len(password) < 8:

            await update.message.reply_text(f'❌ Password minimal 8 karakter')

            return

        

        async with aiohttp.ClientSession() as session:

            payload = {

                "name": "setParameterValues",

                "parameterValues": [

                    [f"InternetGatewayDevice.LANDevice.1.WLANConfiguration.{ssidKe}.SSID", wifi_name, "xsd:string"],

                  [f"InternetGatewayDevice.LANDevice.1.WLANConfiguration.{ssidKe}.PreSharedKey.1.PreSharedKey", password, "xsd:string"] 

#                       ["Device.WiFi.SSID.1.SSID", wifi_name, "xsd:string"], # parameter mikrotik

#                       ["Device.WiFi.AccessPoint.1.Security.KeyPassphrase", password, "xsd:string"] # mikrotik

                ]

            }

            url = f'{apiUrl}/devices/{device_id}/tasks?connection_request'

            async with session.post(url, json=payload) as response:

                if response.status == 200 or response.status == 202:

                    await update.message.reply_text(f'SSID dan Password berhasil diubah dengan SSID: *{wifi_name}* dan Password: *{password}*', parse_mode='markdown')

                elif response.status == 404:

                    await update.message.reply_text(f'*ID Perangkat Tidak ditemukan*')

                else:

                    await update.message.reply_text(f'Gagal mengirim perubahan SSID dan password WiFi, coba lagi lain kali')

        return



    # respon P tidak dikenal

    await update.message.reply_text('Perintah tidak dikenal.\nKetik /help untuk bantuan')



# help

async def help(update, context: ContextTypes.DEFAULT_TYPE) -> None:

    help_text = (

        "Beberapa Perintah yang dapat digunakan:\n"

        "1. /start - Start.\n"

        "2. /list - Menampilkan daftar perangkat yang terhubung.\n"

        "3. US.<device_id>.<wifi_name> - Mengubah SSID WiFi.\n"

        "4. UP.<device_id>.<password> - Mengubah password WiFi.\n"

        "5. USP.<device_id>.<wifi_name>.<password> - Mengubah SSID dan password WiFi"

    )

    await update.message.reply_text(f'{help_text}')

      

# infokan

async def infokan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    username = update.message.from_user.username

    chat_id = update.message.chat_id

    await update.message.reply_text(f'Info Akun Anda:\nUsername: `{username}`\nChatID: `{chat_id}`', parse_mode='Markdown')



# AI

async def ai_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if len(context.args) == 0:

        await update.message.reply_text("Contoh : /ai apa itu python")

        return

    

    message_text = " ".join(context.args)

    api_url = f'https://api-zenn.vercel.app/api/ai/groq?q={message_text}'



    async with aiohttp.ClientSession() as session:

        async with session.get(api_url) as response:

            if response.status == 200:

                data = await response.json()

                await update.message.reply_text(data['data'], parse_mode='Markdown')

            else:

                await update.message.reply_text('Failed to fetch AI response.', parse_mode='Markdown')



#-----

app = ApplicationBuilder().token(token).build()



# log pesan

app.add_handler(MessageHandler(filters.ALL, log_pesan), group=0)

# Perintah bot

app.add_handler(CommandHandler("start", welcome), group=1)

app.add_handler(CommandHandler("list", listDevice), group=1)

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_Wifi), group=1)

app.add_handler(CommandHandler("help", help), group=1)

app.add_handler(CommandHandler("info", infokan), group=1)

app.add_handler(CommandHandler("ai", ai_handler), group=1)



app.run_polling()

