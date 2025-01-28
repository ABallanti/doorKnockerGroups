from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os
import folium
from clustering_engine import group_postcodes, create_map

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# File storage directories
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER

# Route for serving the placeholder map
@app.route('/placeholder_map', methods=['GET'])
def placeholder_map():
    """
    Serve an empty placeholder map on page load.
    """
    placeholder_map_path = os.path.join(OUTPUT_FOLDER, "placeholder_map.html")
    if not os.path.exists(placeholder_map_path):
        # Generate an empty map if it doesn't exist
        m = folium.Map(location=[54.0, -2.0], zoom_start=6)  # Centered on the UK
        m.save(placeholder_map_path)
    return send_file(placeholder_map_path)

# Route for uploading a file and processing it
@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Upload a CSV file, process it, and generate grouped CSV and map.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    num_groups = int(request.form.get('num_groups', 5))

    # Save the uploaded file
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    try:
        # Process the file
        result_df = group_postcodes(file_path, num_groups)

        # Save outputs
        output_csv = os.path.join(app.config["OUTPUT_FOLDER"], "grouped_postcodes.csv")
        result_df.to_csv(output_csv, index=False)

        output_map = os.path.join(app.config["OUTPUT_FOLDER"], "grouped_postcodes_map.html")
        create_map(result_df).save(output_map)

        return jsonify({
            "message": "Processing successful",
            "csv_url": "/download/grouped_postcodes.csv",
            "map_url": "/download/grouped_postcodes_map.html"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route for downloading output files
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """
    Serve files from the outputs directory.
    """
    return send_from_directory(app.config["OUTPUT_FOLDER"], filename)

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
