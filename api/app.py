# import os
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from werkzeug.utils import secure_filename

# from pdf_parser import parse_pdf_headings
# from summarizer import summarize_content

# UPLOAD_FOLDER = 'uploads'
# ALLOWED_EXTENSIONS = {'pdf'}

# app = Flask(__name__)
# CORS(app, resources={r"/upload": {"origins": "*"}}) 
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# @app.route('/upload', methods=['POST'])
# def upload_files():
#     if 'pdfs' not in request.files:
#         return jsonify({"error": "No files part"}), 400

#     files = request.files.getlist('pdfs')
#     if len(files) > 10:
#         return jsonify({"error": "You can upload up to 10 PDFs only."}), 400

#     persona = request.form.get('persona')
#     job = request.form.get('job')

#     if not persona or not job:
#         return jsonify({"error": "Persona and job are required."}), 400

#     all_parsed_data = []
#     saved_filepaths = []

#     try:
#         for file in files:
#             if file and allowed_file(file.filename):
#                 filename = secure_filename(file.filename)
#                 filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#                 file.save(filepath)
#                 saved_filepaths.append(filepath)

#                 headings_json = parse_pdf_headings(filepath)
#                 all_parsed_data.append({
#                     "filename": filename,
#                     "headings": headings_json
#                 })
#             else:
#                 return jsonify({"error": f"File {file.filename} is not allowed."}), 400

#         # Pass all parsed data to summarizer
#         summary = summarize_content(all_parsed_data, job, persona)

#         return jsonify({
#             "summary": summary,
#             "parsed_data": all_parsed_data
#         })

#     finally:
#         # Clean up all saved files
#         for path in saved_filepaths:
#             if os.path.exists(path):
#                 try:
#                     os.remove(path)
#                 except Exception as e:
#                     print(f"Error deleting {path}: {e}")


# if __name__ == '__main__':
#     app.run(debug=True)


import os
import shutil
import uuid
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

from api.line_parser import process_folder             # STEP 1
from api.heuristic_labeller import process_unlabelled_csv        # STEP 2
from api.main import run_pipeline                  # STEP 3

ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
CORS(app, resources={r"/upload": {"origins": "*"}})

BASE_UPLOAD_FOLDER = './uploads'
os.makedirs(BASE_UPLOAD_FOLDER, exist_ok=True)

# Serve React frontend
@app.route("/")
@app.route("/index.html")
def serve_react():
    return app.send_static_file("index.html")

# Catch-all for client-side routes (SPA)
@app.route("/<path:path>")
def serve_react_catchall(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return app.send_static_file(path)
    else:
        return app.send_static_file("index.html")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['POST'])
def upload_files():
    if 'pdfs' not in request.files:
        return jsonify({"error": "No files part"}), 400

    files = request.files.getlist('pdfs')
    if len(files) > 10:
        return jsonify({"error": "You can upload up to 10 PDFs only."}), 400

    persona = request.form.get('persona')
    job = request.form.get('job')
    if not persona or not job:
        return jsonify({"error": "Persona and job are required."}), 400

    # Create a temporary directory
    session_id = str(uuid.uuid4())
    temp_dir = os.path.join(BASE_UPLOAD_FOLDER, session_id)
    os.makedirs(temp_dir, exist_ok=True)

    try:
        # Step 1: Save PDFs
        for file in files:
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(temp_dir, filename))
            else:
                return jsonify({"error": f"File {file.filename} is not allowed."}), 400

        # Step 2: Extract headings → unlabelled CSV
        unlabelled_csv = os.path.join(temp_dir, "unlabelled_data.csv")
        process_folder(temp_dir, unlabelled_csv)

        # Step 3: Classify headings → labelled CSV
        labelled_csv = os.path.join(temp_dir, "labelled_output.csv")
        process_unlabelled_csv(unlabelled_csv, labelled_csv)

        # Step 4: Summarize → JSON dict
        output_json = os.path.join(temp_dir, "summary.json")
        start_time = time.time()
        run_pipeline(csv_path=labelled_csv, persona=persona, job=job, output_json_path=output_json)
        elapsed_time = time.time() - start_time

        # Step 5: Return summary
        with open(output_json, 'r', encoding='utf-8') as f:
            summary = f.read()

        return jsonify({
            "summary": summary,
            "execution_time_seconds": round(elapsed_time, 2)
        })

    except Exception as e:
        return jsonify({"error": f"Processing error: {str(e)}"}), 500

    finally:
        # ✅ Cleanup temporary files
        try:
            shutil.rmtree(temp_dir)
        except Exception as cleanup_error:
            print(f"[Cleanup Error] Failed to delete {temp_dir}: {cleanup_error}")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
