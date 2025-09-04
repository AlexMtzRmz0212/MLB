from flask import Flask, jsonify, request
from pybaseball import championships

app = Flask(__name__)

@app.route('/championships')
def get_championships():
    team = request.args.get('team')
    data = championships()
    
    if team:
        team_data = data[data['Team'] == team]
        if not team_data.empty:
            return jsonify({
                "team": team,
                "championships": int(team_data["#"].values[0])
            })
        else:
            return jsonify({"error": "Team not found"}), 404
    else:
        teams = data['Team'].tolist()
        return jsonify(teams)

if __name__ == '__main__':
    app.run(debug=True)
