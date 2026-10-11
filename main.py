import os, asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandObject, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

# === НАСТРОЙКИ ===
API_TOKEN = '8881661079:AAEO6Ru_B_fQgKZncK57lot5BKYVmhSov50'
ADMIN_ID = 8873439307  # СЮДА_ВСТАВЬ_СВОЙ_ID_ИЗ_USERINFOBOT

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
users_db = {}

WEB_APP_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Stars Drop</title>
    <script src="https://telegram.org"></script>
    <style>
        :root { --bg-color: #000000; --card-bg: #111111; --card-selected: #162216; --accent-color: #00e676; --accent-glow: rgba(0, 230, 118, 0.2); --text-color: #ffffff; --text-muted: #888888; --border-color: #222222; --border-selected: #00e676; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: var(--bg-color); color: var(--text-color); margin: 0; padding: 0; display: flex; flex-direction: column; height: 100vh; overflow: hidden; user-select: none; }
        .header { padding: 15px; text-align: center; border-bottom: 1px solid var(--border-color); font-weight: bold; font-size: 18px; letter-spacing: 1px; }
        .content { flex: 1; overflow-y: auto; padding: 15px; padding-bottom: 90px; }
        .tab-content { display: none; } .tab-content.active { display: block; }
        .wheel-area { height: 80px; display: flex; justify-content: center; align-items: center; position: relative; margin-bottom: 10px; }
        .wheel-center { width: 120px; height: 120px; border: 2px solid var(--border-color); border-radius: 50%; position: absolute; top: -70px; display: flex; align-items: flex-end; justify-content: center; padding-bottom: 15px; font-size: 16px; color: var(--text-muted); }
        .chance-header { text-align: center; font-size: 18px; font-weight: bold; color: var(--text-muted); margin-bottom: 20px; letter-spacing: 1px; }
        .chance-header span { color: var(--accent-color); }
        .section-title { font-size: 13px; font-weight: bold; color: var(--text-muted); margin: 15px 0 10px 5px; text-transform: uppercase; letter-spacing: 0.5px; }
        .section-title::before { content: '› '; color: var(--accent-color); }
        .gifts-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 15px; }
        .gift-item { background-color: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 12px 5px; text-align: center; cursor: pointer; transition: all 0.2s ease; }
        .gift-item.selected { background-color: var(--card-selected); border-color: var(--border-selected); box-shadow: inset 0 0 10px var(--accent-glow); }
        .gift-emoji { font-size: 24px; margin-bottom: 8px; }
        .gift-price { font-size: 12px; font-weight: bold; color: var(--text-color); display: flex; align-items: center; justify-content: center; gap: 2px; }
        .gift-price span { color: var(--accent-color); }
        .card { background-color: var(--card-bg); border: 1px solid var(--border-color); border-radius: 14px; padding: 20px; margin-bottom: 15px; text-align: center; }
        .ref-box { background: #050505; padding: 12px; border-radius: 8px; border: 1px solid var(--border-color); word-break: break-all; margin: 15px 0; font-family: monospace; color: var(--text-muted); }
        .balance-title { font-size: 14px; color: var(--text-muted); margin-bottom: 5px; }
        .balance-value { font-size: 38px; font-weight: bold; color: #ffffff; margin-bottom: 20px; }
        .balance-value span { color: var(--accent-color); }
        .btn-action { background-color: #111; color: var(--accent-color); border: 1px solid var(--accent-color); border-radius: 10px; padding: 12px; font-size: 15px; font-weight: bold; width: 100%; margin-bottom: 10px; cursor: pointer; }
        .btn-action.primary { background-color: var(--accent-color); color: #000; }
        .nav-bar { position: fixed; bottom: 0; left: 0; right: 0; height: 70px; background-color: var(--card-bg); border-top: 1px solid var(--border-color); display: flex; justify-content: space-around; align-items: center; z-index: 100; }
        .nav-item { display: flex; flex-direction: column; align-items: center; color: var(--text-muted); background: none; border: none; font-size: 11px; gap: 5px; cursor: pointer; width: 33.3%; height: 100%; justify-content: center; }
        .nav-item.active { color: var(--accent-color); }
    </style>
</head>
<body>
    <div class="header">STARS DROP</div>
    <div class="content">
        <div id="tab-upgrader" class="tab-content active">
            <div class="wheel-area"><div class="wheel-center">0</div></div>
            <div class="chance-header">ШАНС: <span id="chance-val">—</span></div>
            <div class="section-title">Выбери предмет</div><div class="gifts-grid" id="grid-source"></div>
            <div class="section-title">Хочешь получить</div><div class="gifts-grid" id="grid-target"></div>
            <button class="btn-main" onclick="processUpgrade()">ПРОКАЧАТЬ</button>
        </div>
        <div id="tab-referrals" class="tab-content">
            <div class="card">
                <h3>Реферальная система</h3>
                <p style="color: var(--text-muted); font-size: 14px;">Приглашайте друзей и получайте <b style="color: var(--accent-color)">10% от их дохода</b> на баланс.</p>
                <div class="ref-box" id="ref-url">Генерация...</div>
                <button class="btn-action primary" onclick="copyRef()">Копировать ссылку</button>
            </div>
        </div>
        <div id="tab-profile" class="tab-content">
            <div class="card">
                <div class="balance-title">Ваш баланс</div>
                <div class="balance-value"><span id="user-balance">0</span> <span>★</span></div>
                <p id="user-name" style="color: var(--text-muted); margin: 0; font-size: 14px;">@username</p>
            </div>
            <button class="btn-action primary" onclick="depositStars()">Пополнить Stars</button>
            <button class="btn-action" onclick="sendWithdraw()">Вывод подарка</button>
        </div>
    </div>
    <div class="nav-bar">
        <button class="nav-item active" onclick="switchTab('upgrader', this)"><span>Апгрейдер</span></button>
        <button class="nav-item" onclick="switchTab('referrals', this)"><span>Рефералы</span></button>
        <button class="nav-item" onclick="switchTab('profile', this)"><span>Профиль</span></button>
    </div>
    <script>
        const tg = window.Telegram.WebApp; tg.expand();
        const giftData = [
            { id: 1, emoji: '🧸', price: 15 }, { id: 2, emoji: '🌹', price: 25 },
            { id: 3, emoji: '🎂', price: 50 }, { id: 4, emoji: '🚀', price: 100 },
            { id: 5, emoji: '❤️', price: 200 }, { id: 6, emoji: '💎', price: 500 },
            { id: 7, emoji: '👑', price: 1500 }, { id: 8, emoji: '💍', price: 5000 }
        ];
        let selectedSource = null, selectedTarget = null;
        if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
            const u = tg.initDataUnsafe.user;
            document.getElementById('user-name').innerText = `@${u.username || 'user'}`;
            document.getElementById('ref-url').innerText = `https://t.me` + tg.initDataUnsafe.receiver.username + `?start=r_` + u.id;
        }
        function renderGrids() {
            const sg = document.getElementById('grid-source'), tgGrid = document.getElementById('grid-target');
            giftData.forEach(item => {
                let s = document.createElement('div'); s.className = 'gift-item'; s.innerHTML = `<div class="gift-emoji">${item.emoji}</div><div class="gift-price">${item.price}<span>★</span></div>`;
                s.onclick = () => { document.querySelectorAll('#grid-source .gift-item').forEach(el=>el.classList.remove('selected')); s.classList.add('selected'); selectedSource = item; calculateChance(); };
                sg.appendChild(s);
                let t = document.createElement('div'); t.className = 'gift-item'; t.innerHTML = `<div class="gift-emoji">${item.emoji}</div><div class="gift-price">${item.price}<span>★</span></div>`;
                t.onclick = () => { document.querySelectorAll('#grid-target .gift-item').forEach(el=>el.classList.remove('selected')); t.classList.add('selected'); selectedTarget = item; calculateChance(); };
                tgGrid.appendChild(t);
            });
        }
        function calculateChance() {
            const cl = document.getElementById('chance-val');
            if (selectedSource && selectedTarget) {
                if (selectedSource.price >= selectedTarget.price) cl.innerText = "100%";
                else cl.innerText = Math.min(Math.round((selectedSource.price / selectedTarget.price) * 100), 95) + "%";
            } else cl.innerText = "—";
        }
        function switchTab(id, btn) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.getElementById(`tab-${id}`).classList.add('active');
        }
        function copyRef() { navigator.clipboard.writeText(document.getElementById('ref-url').innerText).then(() => tg.showAlert("Ссылка скопирована!")); }
        function depositStars() { tg.showAlert("Запрос отправлен."); }
        function sendWithdraw() {
            tg.showPopup({ title: 'Вывод подарка', message: 'Введите получателя:', buttons: [{id: 'ok', type: 'default', text: 'Вывести'}, {id: 'c', type: 'cancel', text: 'Отмена'}] }, (btnId) => {
                if(btnId === 'ok') {
                    fetch('/api/withdraw', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ user_id: tg.initDataUnsafe.user.id }) });
                    tg.showAlert("Заявка отправлена!");
                }
