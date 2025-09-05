# 🗺️ MLB Teams Interactive Map

An interactive **Major League Baseball (MLB) map** that visualizes all 30 MLB teams with smart marker separation, division path connections, and team logos — all in a single interactive HTML page.

---

## 📂 Project Structure
```
.
├── Current Season
├── Map/
│   ├── Old Maps
│   ├── DivAndLeaguesMap.py
│   └── MLB.csv
├── Old Tests
├── Teams Info
├── Visualizations
├── World Series
├── index.html
└── README.md
```
---

## ✨ Features

- **Team Markers**: Displays each MLB team with their official logo  
- **Automatic Marker Separation**: Prevents overlapping markers using a configurable separation algorithm  
- **Division Path Visuals**: Draws connecting lines between teams in the same division  
- **League Colors**:  
  - 🟥 **American League** → Red paths  
  - 🟦 **National League** → Blue paths  
- **Original Positions**: Small black dots mark unadjusted geographic locations  
- **Interactive Popups**: Click on a logo to see team info  

---

## 🛠️ Custom Separations

Some teams are very close geographically. These pairs have **custom separation rules** applied:

| Team Pair                         | Direction (°) | Strength |
|----------------------------------|--------------|----------|
| Milwaukee Brewers ↔ Chicago Cubs | 150°         | 20x      |
| Chicago White Sox ↔ Chicago Cubs | 250°         | 10x      |
| NY Yankees ↔ NY Mets             | 330°         | 20x      |
| LA Dodgers ↔ LA Angels           | 90°          | 20x      |
| LA Dodgers ↔ SD Padres           | 90°          | 20x      |
| SF Giants ↔ Oakland Athletics    | 100°         | 15x      |
| Baltimore Orioles ↔ Washington Nationals | 300° | 15x |

---

## ⚙️ Configuration

You can tweak the marker separation algorithm inside `DivAndLeaguesMap.py`:

| Parameter         | Description                              | Default |
|------------------|----------------------------------------|---------|
| `MIN_DISTANCE_KM` | Minimum allowed distance between markers | 140 km |
| `ITERATIONS`      | Number of passes for separation         | 2 |
| `DIV_FACTOR`      | Force divisor (lower = more separation) | 60 |

---

## 📊 Data Requirements

The `MLB.csv` file must have these columns:

| Column      | Description |
|-------------|-------------|
| **Team**    | Full team name |
| **League**  | "American" or "National" |
| **Division**| Division name |
| **Latitude**| Team’s geographic latitude |
| **Longitude**| Team’s geographic longitude |
| **LogoURL** | Direct link to official team logo |

---

## 🚀 Installation & Usage

1. **Install Dependencies**
   ```bash
   pip install pandas folium numpy
2. **Check Data File**  
   Ensure `MLB.csv` is in `./Map/`.
3. **Run the Script**
   ```bash
   python ./Map/DivAndLeaguesMap.py
4. **Open the Map**
    The generated `index.html` will appear in the project root (./index.html).  
    Open it in any browser.
---

## 🖌️ Customization

- Modify `custom_directions` in `DivAndLeaguesMap.py` to adjust team pair separation  
- Change `division_orders` to customize division path order  
- Adjust `league_colors` dictionary for different color schemes  
- Tune map center/zoom in `folium.Map()` initialization  

---

## 📦 Dependencies

- **Python 3.x**  
- **pandas**  
- **folium**  
- **numpy**  

---

## 📸 Output Preview

- **Interactive Map** with clickable logos  
- **Colored Division Paths** (Red = AL, Blue = NL)  
- **Separated Markers** for overlapping cities  
- **Original Position Dots** for reference  
- **Legend Box** for interpretation  

---

## 🏗️ Future Improvements

- Change color tones according to divisions
- Add filters by league/division  
- Toggle for original positions  
- Dynamic legend inside the map  

---

## 👤 Author

Maintained by **Alex**.  
Contributions and suggestions welcome!