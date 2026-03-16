#!/usr/bin/env python3
"""
Telegram Bot untuk Spam WhatsApp (Pairing Code Only)
Author: ZinXploit
"""

import os
import subprocess
import threading
from datetime import datetime
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# ===== KONFIGURASI =====
TOKEN = "ISI_TOKEN_BOT_TELEGRAM_LO"  # Ganti dengan token bot lo
ALLOWED_USERS = [123456789]  # ID Telegram yang diizinkan

# ===== VARIABLE GLOBAL =====
spam_process = None
spam_info = {}

# ===== FUNGSI CEK AKSES =====
def is_allowed(user_id):
    return user_id in ALLOWED_USERS

# ===== HANDLER COMMAND =====
def start(update: Update, context: CallbackContext):
    if not is_allowed(update.effective_user.id):
        update.message.reply_text("❌ Lo siapa? Ga diizinin, kontol!")
        return
    
    welcome_msg = """
╔═══════════════════════════════════╗
║    WA SPAM BOT - Simple Edition   ║
║         Created by ZinXploit       ║
╚═══════════════════════════════════╝

Perintah:
• /spam 628xxx jumlah - Spam pairing code
• /stop - Hentikan spam
• /status - Cek status

⚠️ Resiko: IP lo bisa diblokir WhatsApp!
    """
    update.message.reply_text(welcome_msg)

def spam(update: Update, context: CallbackContext):
    global spam_process, spam_info
    
    user_id = update.effective_user.id
    if not is_allowed(user_id):
        update.message.reply_text("❌ Ga diizinin, bego!")
        return
    
    # Cek apakah sudah ada spam berjalan
    if spam_process and spam_process.poll() is None:
        update.message.reply_text("⚠️ Masih ada spam berjalan. Stop dulu pake /stop")
        return
    
    try:
        target = context.args[0]
        jumlah = int(context.args[1]) if len(context.args) > 1 else 50
        
        # Validasi nomor
        if not target.startswith('62') or len(target) < 10:
            update.message.reply_text("❌ Format nomor salah! Harus 628xxx")
            return
        
        if jumlah > 200:
            update.message.reply_text("⚠️ Maksimal 200 spam biar IP lo ga cepet diblokir!")
            return
        
        update.message.reply_text(f"🔥 Memulai spam {jumlah}x ke {target}...")
        
        # Jalankan Node.js script di background
        cmd = f"node spammer.js {target} {jumlah}"
        spam_process = subprocess.Popen(
            cmd, 
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        spam_info = {
            'target': target,
            'jumlah': jumlah,
            'start_time': datetime.now(),
            'user_id': user_id,
            'chat_id': update.effective_chat.id
        }
        
        # Buat thread buat monitor proses
        monitor_thread = threading.Thread(target=monitor_spam, args=(update.effective_chat.id, context))
        monitor_thread.daemon = True
        monitor_thread.start()
        
    except IndexError:
        update.message.reply_text("Usage: /spam 628xxx [jumlah]")
    except Exception as e:
        update.message.reply_text(f"❌ Error: {str(e)}")

def stop(update: Update, context: CallbackContext):
    global spam_process, spam_info
    
    if not is_allowed(update.effective_user.id):
        update.message.reply_text("❌ Ga diizinin, bego!")
        return
    
    if spam_process and spam_process.poll() is None:
        spam_process.terminate()
        spam_process = None
        spam_info = {}
        update.message.reply_text("🛑 Spam dihentikan!")
    else:
        update.message.reply_text("📭 Tidak ada spam aktif.")

def status(update: Update, context: CallbackContext):
    global spam_info, spam_process
    
    if not is_allowed(update.effective_user.id):
        update.message.reply_text("❌ Ga diizinin, bego!")
        return
    
    if spam_process and spam_process.poll() is None:
        elapsed = (datetime.now() - spam_info['start_time']).seconds
        status_msg = f"""
📊 STATUS SPAM:
🎯 Target: {spam_info['target']}
📨 Jumlah: {spam_info['jumlah']}
⏱️  Waktu: {elapsed} detik
🔄 Status: BERJALAN
        """
        update.message.reply_text(status_msg)
    else:
        update.message.reply_text("📭 Tidak ada spam aktif.")

def monitor_spam(chat_id, context):
    """Monitor proses spam dan kirim notifikasi selesai"""
    global spam_process, spam_info
    
    spam_process.wait()  # Tunggu sampai selesai
    
    # Baca output
    stdout, stderr = spam_process.communicate()
    
    if spam_process.returncode == 0:
        context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ Spam ke {spam_info['target']} selesai!"
        )
    else:
        context.bot.send_message(
            chat_id=chat_id,
            text=f"❌ Spam gagal: {stderr[:200]}"
        )
    
    spam_process = None
    spam_info = {}

def main():
    if TOKEN == "ISI_TOKEN_BOT_TELEGRAM_LO":
        print("❌ Token bot belum diisi, kontol!")
        return
    
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # Register handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("spam", spam))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(CommandHandler("status", status))
    
    # Start bot
    print("🤖 Bot started! Press Ctrl+C to stop.")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
