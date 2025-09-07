const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');

const API_URL = 'http://127.0.0.1:5000/rifa';

const client = new Client({
    authStrategy: new LocalAuth()
});

// Estado para aguardar nome do comprador por chat
const aguardandoNome = {};

client.on('qr', qr => {
    qrcode.generate(qr, { small: true });
    console.log('Escaneie o QR code acima com o WhatsApp!');
});

client.on('ready', () => {
    console.log('Bot pronto!');
});

client.on('message', async msg => {
    const chatId = msg.from;
    const texto = msg.body.trim();

    // Se está aguardando o nome do comprador
    if (aguardandoNome[chatId]) {
        const numeroVendido = aguardandoNome[chatId];
        // Aqui você pode salvar o nome e o número em um arquivo ou banco de dados
        // Exemplo: salvar em um arquivo CSV (opcional)
        const fs = require('fs');
        const linha = `${numeroVendido},${texto}\n`;
        fs.appendFileSync('compradores.csv', linha);

        msg.reply(`Nome "${texto}" registrado para o número ${numeroVendido}.`);
        delete aguardandoNome[chatId];
        return;
    }

    const textoLower = texto.toLowerCase();

    if (textoLower === 'help') {
        msg.reply(
            `Você está conversando com um robô de rifas!\n\n` +
            `Comandos disponíveis:\n` +
            `lista - Mostra todos os números e status\n` +
            `vendidos - Mostra números vendidos\n` +
            `disponiveis - Mostra números disponíveis\n` +
            `vender <numero> - Marca o número como vendido\n` +
            `desmarcar <numero> - Marca o número como disponível novamente\n` +
            `valor_total - Mostra quanto já foi arrecadado\n` +
            `help - Mostra esta lista`
        );
    } else if (textoLower === 'lista') {
        const res = await axios.get(API_URL);
        const lista = res.data.map(r => {
            const statusIcon = r.status === 'vendido' ? '❌' : '✅';
            return `${r.numero}: ${statusIcon}`;
        }).join('\n');
        msg.reply(lista);
    } else if (textoLower === 'vendidos') {
        const res = await axios.get(`${API_URL}/vendidos`);
        msg.reply('Vendidos:\n' + res.data.map(n => `${n} ❌`).join(', '));
    } else if (textoLower === 'disponiveis') {
        const res = await axios.get(`${API_URL}/disponiveis`);
        msg.reply('Disponíveis:\n' + res.data.map(n => `${n} ✅`).join(', '));
    } else if (textoLower.startsWith('vender ')) {
        const numero = textoLower.split(' ')[1];
        try {
            const res = await axios.post(`${API_URL}/vender`, { numero });
            msg.reply(res.data.msg || JSON.stringify(res.data));
            // Agora pergunta o nome do comprador
            aguardandoNome[chatId] = numero;
            msg.reply('Para quem você vendeu esse número? Responda com o nome.');
        } catch (err) {
            msg.reply(err.response?.data?.erro || 'Erro ao vender número.');
        }
    } else if (textoLower.startsWith('desmarcar ')) {
        const numero = textoLower.split(' ')[1];
        try {
            const res = await axios.post(`${API_URL}/desvender`, { numero });
            msg.reply(res.data.msg || JSON.stringify(res.data));
        } catch (err) {
            msg.reply(err.response?.data?.erro || 'Erro ao desmarcar número.');
        }
    } else if (textoLower === 'valor_total') {
        const res = await axios.get(`${API_URL}/valor_total`);
        msg.reply(
            `Valor total arrecadado: R$${res.data.valor_total}\n` +
            `Quantidade vendida: ${res.data.quantidade_vendida}\n` +
            `Preço por número: R$${res.data.preco_por_numero}`
        );
    }
});

client.initialize();