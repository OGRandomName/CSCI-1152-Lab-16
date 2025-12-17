import csv
from plotly.subplots import make_subplots
from plotly.graph_objs import Scattergeo, Layout
from plotly import offline

def load_fire_data(filename, limit=1000):
    """Load fire data from a CSV, auto-detecting the brightness field."""
    lats, lons, brights, hover_texts = [], [], [], []
    with open(filename) as f:
        reader = csv.reader(f)
        header_row = next(reader)

        # Required fields
        lat_index = header_row.index("latitude")
        lon_index = header_row.index("longitude")
        date_index = header_row.index("acq_date")

        # Auto-detect brightness field
        if "brightness" in header_row:
            bright_index = header_row.index("brightness")
            bright_label = "brightness"
        elif "bright_ti4" in header_row:
            bright_index = header_row.index("bright_ti4")
            bright_label = "bright_ti4"
        elif "bright_ti5" in header_row:
            bright_index = header_row.index("bright_ti5")
            bright_label = "bright_ti5"
        else:
            raise ValueError(f"No brightness field found in {filename}")

        count = 0
        for row in reader:
            try:
                lat = float(row[lat_index])
                lon = float(row[lon_index])
                bright = float(row[bright_index])
                date = row[date_index]
            except ValueError:
                # Skip invalid rows
                continue
            else:
                lats.append(lat)
                lons.append(lon)
                brights.append(bright)
                hover_texts.append(date)

            count += 1
            if count >= limit:
                break

    return lats, lons, brights, hover_texts, bright_label

# Load both datasets (limit to first 1000 for readability)
lats_1, lons_1, brights_1, texts_1, label_1 = load_fire_data('world_fires_1_day.csv', limit=1000)
lats_7, lons_7, brights_7, texts_7, label_7 = load_fire_data('world_fires_7_day.csv', limit=1000)

# Create subplot layout with 1 row, 2 columns
fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=("1 Day Fires", "7 Day Fires"),
    specs=[[{'type': 'scattergeo'}, {'type': 'scattergeo'}]]
)

# Add 1-day fires (hide its colorbar)
fig.add_trace(
    Scattergeo(
        lon=lons_1,
        lat=lats_1,
        text=texts_1,
        marker=dict(
            size=[b/50 for b in brights_1],
            color=brights_1,
            colorscale='Bluered',
            showscale=False  # hide left colorbar
        )
    ),
    row=1, col=1
)

# Add 7-day fires
fig.add_trace(
    Scattergeo(
        lon=lons_7,
        lat=lats_7,
        text=texts_7,
        marker=dict(
            size=[b/50 for b in brights_7],
            color=brights_7,
            colorscale='Viridis',
            colorbar=dict(
                title='Brightness',   # <-- force title to "Brightness"
                x=1.02,
                y=0.5,
                thickness=15,
                len=0.8
            )
        )
    ),
    row=1, col=2
)

# Global layout
fig.update_layout(
    title_text="Global Fire Data Comparison: 1 Day vs 7 Day",
    showlegend=False
)

offline.plot(fig, filename='global_fires_side_by_side.html')
