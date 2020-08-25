from app import api, API, app

API.add_resource(api.UPLOAD, "/upload")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)