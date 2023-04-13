from flask import Flask, request, send_file, render_template
from io import BytesIO
import pandas as pd
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/subtract', methods=['POST'])
def subtract_csvs():
    uploaded_csv = request.files.get('file')
    if not uploaded_csv: # Check if csv is uploaded
        return {'error': 'File is required'}, 400
    if not uploaded_csv.read(): # Check if csv is empty
        return {'error': 'File is empty'}, 400
    
    uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_csv.filename)
    
    with open(uploaded_file_path, "wb") as f:
        f.write(uploaded_csv.read())
    uploaded_csv.seek(0)    
    uploaded_df = pd.read_csv(uploaded_csv, header=None, index_col=False)
    uploaded_df.columns = ['col' + str(col) for col in range(uploaded_df.shape[1])] # Assign generated column names
    uploaded_df.drop_duplicates(inplace=True)
    print(f'Before drop_duplicates():\n{uploaded_df}\n')
    uploaded_diff = pd.read_csv('hosted-file.csv', header=None, index_col=False)
    uploaded_diff.columns = ['col' + str(col) for col in range(uploaded_diff.shape[1])] # Assign generated column names
    uploaded_df = uploaded_df.merge(uploaded_diff, on=list(uploaded_diff.columns), how='left', indicator=True)
    uploaded_df = uploaded_df[uploaded_df['_merge'] == 'left_only'].drop('_merge', axis=1)
    print(f'After drop_duplicates():\n{uploaded_df}\n')
    print(f'Uploaded file shape: {uploaded_df.shape}')
    
    result_csv = BytesIO()
    uploaded_df.to_csv(result_csv, index=False, header=False)
    result_csv.seek(0)
    
    return send_file(result_csv, mimetype='text/csv', as_attachment=True, download_name='result.csv')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')