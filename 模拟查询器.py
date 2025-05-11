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
    # 在此添加更多药物数据
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

@app.route('/search', methods=['POST'])
def api_search():
    query = request.json.get('query', '').lower()
    results = find_closest_matches(query)
    return jsonify(results)

index_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Medical Search</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <style>
        #results {
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 10px;
            background-color: #f8f9fa;
        }
    </style>
    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
</head>
<body>
    <div class="container">
        <h1 class="mt-5 text-center">Medical Search</h1>
        <div class="form-group mt-3">
            <input type="text" id="searchBox" class="form-control" placeholder="Enter drug name">
        </div>
        <div id="results" class="list-group mt-3"></div>
    </div>
    <script>
        $('#searchBox').on('input', function() {
            const query = $(this).val().trim();
            if (query.length > 0) {
                $.ajax({
                    url: '/search',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ query: query }),
                    success: function(data) {
                        let resultsDiv = $('#results');
                        resultsDiv.empty();
                        if (data.length > 0) {
                            data.forEach(med => {
                                resultsDiv.append(`<a href="#" class="list-group-item list-group-item-action">
                                    <strong>${med.name}</strong>: ${med.description} - <em>${med.uses}</em>
                                </a>`);
                            });
                        } else {
                            resultsDiv.append('<div class="alert alert-warning">No results found.</div>');
                        }
                    }
                });
            } else {
                $('#results').empty();
            }
        });
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True)
