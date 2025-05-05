from flask import Flask, render_template_string, request, jsonify
import uuid
import json
from datetime import datetime
app = Flask(__name__)
# ------------------------ 数据库初始化 ------------------------
try:
    with open('notes.json', 'r') as file:
        notes = json.load(file)
except FileNotFoundError:
    notes = {}
def save_notes():
    with open('notes.json', 'w') as file:
        json.dump(notes, file)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.json
        note_id = str(uuid.uuid4())
        notes[note_id] = {
            'content': data['content'],
            'iv': data['iv'],
            'salt': data['salt'],
            'timestamp': datetime.now().isoformat()  # 记录当前时间
        }
        save_notes()
        return jsonify({'note_id': note_id})
    
    # 首页 HTML 模板
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>加密记事本</title>
        <style>
            body {
                background-color: #e6f7e6;
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .container {
                padding: 20px;
                background-color: #ffffff;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                width: 50%;
            }
            textarea {
                width: 100%;
                padding: 10px;
                border-radius: 4px;
                border: 1px solid #ccc;
                box-sizing: border-box;
                margin-bottom: 10px;
            }
            input[type="password"], button {
                display: block;
                width: calc(100% - 20px);
                padding: 10px;
                margin-bottom: 10px;
                border-radius: 4px;
                border: 1px solid #ccc;
            }
            button {
                background-color: #4CAF50;
                color: white;
                cursor: pointer;
                border: none;
            }
            button:hover {
                background-color: #45a049;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 style="text-align: center;">在线加密记事本</h1>
            <textarea id="content" rows="10" placeholder="在此输入文本..."></textarea>
            <input type="password" id="password" placeholder="输入密码进行加密（可选）">
            <button type="button" onclick="handleSubmit()">保存</button>
        </div>

        <script>
            async function encryptData(content, password) {
                const enc = new TextEncoder();
                const keyMaterial = await window.crypto.subtle.importKey(
                    "raw",
                    enc.encode(password),
                    { name: "PBKDF2" },
                    false,
                    ["deriveKey"]
                );

                const salt = window.crypto.getRandomValues(new Uint8Array(16));
                const key = await window.crypto.subtle.deriveKey(
                    {
                        name: "PBKDF2",
                        salt: salt,
                        iterations: 100000,
                        hash: "SHA-256"
                    },
                    keyMaterial,
                    { name: "AES-GCM", length: 256 },
                    false,
                    ["encrypt"]
                );

                const iv = window.crypto.getRandomValues(new Uint8Array(12));
                const encrypted = await window.crypto.subtle.encrypt(
                    { name: "AES-GCM", iv: iv },
                    key,
                    enc.encode(content)
                );

                return {
                    cipherText: new Uint8Array(encrypted),
                    iv: iv,
                    salt: salt
                };
            }

            async function handleSubmit() {
                const content = document.getElementById('content').value;
                const password = document.getElementById('password').value;

                let encryptedData;
                try {
                    if (password) {
                        encryptedData = await encryptData(content, password);
                    } else {
                        encryptedData = { cipherText: new TextEncoder().encode(content) };
                    }

                    const response = await fetch('/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            iv: encryptedData.iv ? Array.from(encryptedData.iv) : null,
                            salt: encryptedData.salt ? Array.from(encryptedData.salt) : null,
                            content: Array.from(encryptedData.cipherText)
                        })
                    });

                    if (response.ok) {
                        const data = await response.json();
                        window.location.href = `/note/${data.note_id}`;
                    }
                } catch (error) {
                    console.error("加密错误: ", error);
                }
            }
        </script>
    </body>
    </html>
    """)
@app.route('/note/<note_id>', methods=['GET'])
def view_note(note_id):
    note = notes.get(note_id)
    if not note:
        return "Note not found", 404

    # 查看 HTML 模板
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>查看记事本</title>
        <style>
            body {
                background-color: #e6f7e6;
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .container {
                padding: 20px;
                background-color: #ffffff;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                width: 50%;
            }
            textarea {
                width: 100%;
                padding: 10px;
                border-radius: 4px;
                border: 1px solid #ccc;
                box-sizing: border-box;
                margin-bottom: 10px;
            }
            button {
                width: 100%;
                padding: 10px;
                background-color: #4CAF50;
                color: white;
                cursor: pointer;
                border: none;
                border-radius: 4px;
                margin-bottom: 10px;
            }
            button:hover {
                background-color: #45a049;
            }
            .modal {
                display: none;
                position: fixed;
                z-index: 1;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.4);
                justify-content: center;
                align-items: center;
            }
            .modal-content {
                background-color: #fefefe;
                padding: 20px;
                border: 1px solid #888;
                width: 300px;
                border-radius: 4px;
            }
            .note-info {
                margin-bottom: 10px;
                font-size: 14px;
                color: #555;
            }
        </style>
    </head>
    <body>

        <div class="container">
            <div class="note-info">创建时间：{{ note.timestamp }}</div>
            <textarea id="content" rows="10" readonly placeholder="待解密内容..."></textarea>
            <button type="button" id="decryptButton">解密</button>
        </div>

        <div id="passwordModal" class="modal">
            <div class="modal-content">
                <span>请输入密码解密</span>
                <input type="password" id="modalPassword" style="width: 100%; padding: 8px; margin-top: 10px;">
                <button type="button" onclick="handleDecrypt()">解密</button>
            </div>
        </div>

        <script>
            async function decryptData(cipherData, password, iv, salt) {
                const enc = new TextEncoder();
                const keyMaterial = await window.crypto.subtle.importKey(
                    "raw",
                    enc.encode(password),
                    { name: "PBKDF2" },
                    false,
                    ["deriveKey"]
                );

                const key = await window.crypto.subtle.deriveKey(
                    {
                        name: "PBKDF2",
                        salt: new Uint8Array(salt),
                        iterations: 100000,
                        hash: "SHA-256"
                    },
                    keyMaterial,
                    { name: "AES-GCM", length: 256 },
                    false,
                    ["decrypt"]
                );

                const decrypted = await window.crypto.subtle.decrypt(
                    { name: "AES-GCM", iv: new Uint8Array(iv) },
                    key,
                    new Uint8Array(cipherData)
                );

                const dec = new TextDecoder();
                return dec.decode(decrypted);
            }

            document.getElementById('decryptButton').onclick = function() {
                if ({{ note.iv is none or note.salt is none }}) {
                    const dec = new TextDecoder();
                    document.getElementById('content').value = dec.decode(new Uint8Array({{ note.content }}));
                } else {
                    document.getElementById('passwordModal').style.display = 'flex';
                }
            };

            async function handleDecrypt() {
                const password = document.getElementById('modalPassword').value;
                const noteContent = new Uint8Array({{ note.content }});
                const iv = {{ note.iv }};
                const salt = {{ note.salt }};

                try {
                    let decryptedContent = await decryptData(noteContent, password, iv, salt);
                    document.getElementById('content').value = decryptedContent;
                    document.getElementById('passwordModal').style.display = 'none';
                } catch (error) {
                    console.error("解密错误: ", error);
                    alert("解密失败，请确认密码输入正确。");
                }
            }
        </script>
    </body>
    </html>
    """, note=note)

if __name__ == '__main__':
    app.run(debug=False)
