import pandas as pd
from sklearn.cluster import KMeans
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import folium

# Function to convert postcodes to coordinates
# Function to convert postcodes to coordinates with retry
def get_coordinates(postcode, geolocator, retries=3):
    for attempt in range(retries):
        try:
            location = geolocator.geocode(postcode + ", UK", timeout=10)
            if location:
                return (location.latitude, location.longitude)
        except GeocoderTimedOut:
            print(f"Timeout occurred for postcode {postcode}. Retrying... ({attempt + 1}/{retries})")
    return None


# Main function for grouping postcodes
def group_postcodes(file_path, num_groups):
    # Read the postcodes from the file
    df = pd.read_csv(file_path)
    if 'Postcode' not in df.columns:
        raise ValueError("The input file must contain a column named 'Postcode'.")

    postcodes = df['Postcode'].dropna().tolist()

    # Convert postcodes to coordinates
    geolocator = Nominatim(user_agent="postcode_grouping_tool", timeout=10)
    coordinates = []

    print("Converting postcodes to coordinates...")
    for postcode in postcodes:
        coords = get_coordinates(postcode, geolocator)
        if coords:
            coordinates.append(coords)
        else:
            print(f"Could not find coordinates for postcode: {postcode}")

    if len(coordinates) < num_groups:
        raise ValueError("The number of valid coordinates is less than the number of groups.")

    # Apply KMeans clustering
    print("Grouping postcodes...")
    kmeans = KMeans(n_clusters=num_groups, random_state=42)
    clusters = kmeans.fit_predict(coordinates)

    # Create a new dataframe with the clusters
    result_df = pd.DataFrame({
        'Postcode': [postcode for postcode, coord in zip(postcodes, coordinates) if coord is not None],
        'Latitude': [coord[0] for coord in coordinates],
        'Longitude': [coord[1] for coord in coordinates],
        'Group': clusters
    })

    return result_df

# Function to create a map with grouped postcodes
def create_map(grouped_postcodes):
    print("Creating map...")
    # Initialize the map centered around the UK
    m = folium.Map(location=[54.0, -2.0], zoom_start=6)

    # Add points to the map with color-coded groups
    colors = ["red", "blue", "green", "purple", "orange", "darkred", "lightred", "beige", "darkblue", "darkgreen"]
    for _, row in grouped_postcodes.iterrows():
        folium.CircleMarker(
            location=(row['Latitude'], row['Longitude']),
            radius=5,
            color=colors[row['Group'] % len(colors)],
            fill=True,
            fill_color=colors[row['Group'] % len(colors)],
            fill_opacity=0.7,
            popup=f"Postcode: {row['Postcode']}\nGroup: {row['Group']}"
        ).add_to(m)

    return m

# Example usage
if __name__ == "__main__":
    input_file = "postcodes.csv"  # Replace with your file path
    number_of_groups = 4  # Replace with the desired number of groups

    try:
        grouped_postcodes = group_postcodes(input_file, number_of_groups)
        output_file = "grouped_postcodes.csv"
        grouped_postcodes.to_csv(output_file, index=False)
        print(f"Grouped postcodes saved to {output_file}")

        # Create and save the map
        postcode_map = create_map(grouped_postcodes)
        map_file = "grouped_postcodes_map.html"
        postcode_map.save(map_file)
        print(f"Map saved to {map_file}")

    except Exception as e:
        print(f"Error: {e}")
