import flask
import elasticsearch as elastic
import os
from pathlib import Path



'''	initialize the Flask and Elasticsearch modules
'''

es = elastic.Elasticsearch('127.0.0.1', port=9200)
app = flask.Flask(__name__)

app.config['WORKING_FOLDER'] = os.getcwd() + '/static/documents'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = "fulltext search"

Path(app.config['WORKING_FOLDER']).mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'docx', 'doc'])


path = os.path.join(app.config['WORKING_FOLDER'])


# Home page
@app.route('/', methods=['GET'])
def index():
    return flask.render_template('fulltext_search.html')


# Search Endpont
@app.route('/elasticsearch/results', methods=['GET', 'POST'])
def search_results():
    query_phrase = flask.request.form['search']
    res = es.search(
        index='testing_index',
        body={
            "query": {"match": {"content": query_phrase}},
            "highlight": {"pre_tags": ["<b><u>"], "post_tags": ["</u></b>"], "fields": {"content": {}}}
        }
    )

    res['ST'] = query_phrase
    for hit in res['hits']['hits']:
        hit['good_summary'] = '….'.join(hit['highlight']['content'])

    return flask.render_template('search_results.html', res=res)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/elasticsearch/upload')
def upload_file():

    list_of_files = {}
    for filename in os.listdir(path):
        list_of_files[filename] = "/static/documents/" + filename

    return flask.render_template('upload.html', len=len(list_of_files), files=list_of_files)


@app.route('/elasticsearch/files/upload', methods=['POST'])
def upload_files():
    if flask.request.method == 'POST':
        # check if the post request has the file part
        if 'files[]' not in flask.request.files:
            flask.flash('No file available for upload')
            return flask.redirect('/elasticsearch/upload')

        files = flask.request.files.getlist('files[]')

        for file in files:
            if file and allowed_file(file.filename):
                file.save(os.path.join(app.config['WORKING_FOLDER'], file.filename))

        flask.flash('File(s) successfully uploaded')
        return flask.redirect('/elasticsearch/upload')


@app.route('/elasticsearch/files/<filename>', methods=['GET', 'POST'])
def delete_file(filename):

    file_to_remove = app.config['WORKING_FOLDER'] + "/" + filename;
    os.remove(file_to_remove)

    flask.flash('File ' + filename + ' successfully removed')
    return flask.redirect('/elasticsearch/upload')


if __name__ == '__main__':
    app.run('127.0.0.1', debug=True)
