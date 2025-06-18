import connexion

from database import init_db

app = connexion.App(__name__, specification_dir=".")
app.add_api("api_spec.yaml")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
