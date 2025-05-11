from flask import Flask, request, jsonify, render_template_string
import Levenshtein

app = Flask(__name__)

# 模拟的药物数据存储
medications = {
    'aspirin': {
        'name': 'Aspirin',
        'description': 'Used to reduce pain, fever, or inflammation.',
        'uses': 'Pain relief, anti-inflammatory'
    },
    'acetaminophen': {
        'name': 'Acetaminophen',
        'description': 'Common pain reliever and fever reducer.',
        'uses': 'Fever, headache'
    },
    # 可以添加更多药物数据
}

def find_closest_matches(query, max_distance=2):
    matches = []
    for med_key, med_info in medications.items():
        distance = Levenshtein.distance(query, med_key)
        if distance <= max_distance:
            matches.append((distance, med_info))
    matches.sort(key=lambda x: (x[0], x[#citation-1](citation-1)['name']))
    return [match[#citation-1](citation-1) for match in matches]

@app.route('/')
def index():
    return render_template_string(index_html)

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    results = find_closest_matches(query)
    return render_template_string(search_html, query=query, results=results)

@app.route('/view/<string:med_name>')
def view_medication(med_name):
    med_info = medications.get(med_name.lower())
    if not med_info:
        return render_template_string(not_found_html), 404
    return render_template_string(view_html, medication=med_info)

# 新增API接口
@app.route('/api/search', methods=['POST'])
def api_search():
    data = request.json
    query = data.get('query', '').lower()
    results = find_closest_matches(query)
    return jsonify(results)

@app.route('/api/view', methods=['POST'])
def api_view():
    data = request.json
    med_name = data.get('name', '').lower()
    med_info = medications.get(med_name)
    if med_info:
        return jsonify(med_info)
    else:
        return jsonify({'error': 'Medication not found'}), 404

index_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Medical Search</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container">
        <h1 class="mt-5 text-center">Medical Search</h1>
        <form action="/search" method="get" class="form-inline justify-content-center mt-3">
            <input type="text" name="q" class="form-control mr-2" placeholder="Enter drug name" required>
            <button type="submit" class="btn btn-primary">Search</button>
        </form>
    </div>
</body>
</html>
'''

search_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Search Results for "{{ query }}"</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container">
        <h1 class="mt-5 text-center">Search Results for "{{ query }}"</h1>
        <ul class="list-group mt-3">
            {% if results %}
                {% for med in results %}
                    <li class="list-group-item">
                        <a href="/view/{{ med.name.lower() }}">{{ med.name }}</a>: {{ med.description }}
                    </li>
                {% endfor %}
            {% else %}
                <li class="list-group-item">No results found.</li>
            {% endif %}
        </ul>
        <a href="/" class="btn btn-secondary mt-3">Back to search</a>
    </div>
</body>
</html>
'''

view_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ medication.name }}</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container">
        <h1 class="mt-5 text-center">{{ medication.name }}</h1>
        <p><strong>Description:</strong> {{ medication.description }}</p>
        <p><strong>Uses:</strong> {{ medication.uses }}</p>
        <a href="/" class="btn btn-secondary">Back to search</a>
    </div>
</body>
</html>
'''

not_found_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Not Found</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container">
        <h1 class="mt-5 text-center">404 - Medication Not Found</h1>
        <p class="text-center">The medication you are looking for does not exist.</p>
        <a href="/" class="btn btn-secondary">Back to search</a>
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True)
