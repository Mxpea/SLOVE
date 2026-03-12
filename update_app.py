import sys

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

new_endpoint = """
@app.route('/api/visualize', methods=['POST'])
def api_visualize():
    data = request.json or {}
    history = data.get('history', [])
    vis_data = recommender.get_visualization_data(history)
    return jsonify(vis_data)
"""

if "def api_visualize" not in code:
    code += new_endpoint

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)
