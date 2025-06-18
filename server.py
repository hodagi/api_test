import os
import connexion

app = connexion.App(__name__, specification_dir='.')
app.add_api('api_spec.yaml')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
