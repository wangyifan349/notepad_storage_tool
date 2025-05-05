from flask import Flask, render_template, request, jsonify
import uuid
import json
app = Flask(__name__)
# ------------------------ 数据库初始化 ------------------------
def load_notes():
    try:
        with open('notes.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_notes():
    with open('notes.json', 'w') as file:
        json.dump(notes, file)

notes = load_notes()
# ------------------------ 路由定义 ------------------------
# 首页路由，显示笔记创建页面
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.json
        note_id = str(uuid.uuid4())
        notes[note_id] = {
            'content': data['content'],
            'iv': data['iv'],
            'salt': data['salt']
        }
        save_notes()
        return jsonify({'note_id': note_id})
    return render_template('index.html')

# 视图路由，显示笔记查看页面
@app.route('/note/<note_id>', methods=['GET'])
def view_note(note_id):
    note = notes.get(note_id)
    if not note:
        return "Note not found", 404
    return render_template('view.html', note=note)

if __name__ == '__main__':
    app.run(debug=False)
