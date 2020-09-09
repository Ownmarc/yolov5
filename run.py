from app import api, API, app

API.add_resource(api.UPLOAD, "/upload")
API.add_resource(api.BURNTBASE, "/burntbase")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=False)
