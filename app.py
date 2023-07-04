from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import zipfile
import io
import tempfile
import subprocess
import os

from werkzeug.datastructures import FileStorage
from enum import Enum
from sqlalchemy import JSON
import trimesh
import gmsh
import threading
import sqlite3

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vorplanml.db'


db = SQLAlchemy(app)
    
    
class Material(Enum):
    MAT1 = 'Stahl - C45'
    MAT2 = 'Stahl - 42CrMo4'
    MAT3 = 'Aluminium - AlMgSi1'
    MAT4 = 'Gusseisen - GG25'
    MAT5 = 'Kupfer - CuZn37'
    MAT6 = 'Messing - Ms58'
    MAT7 = 'Bronze - CuSn8'
    MAT8 = 'Titan - Ti6Al4V'
    MAT9 = 'Nickellegierungen - Inconel 625'
    MAT10 = 'Kunststoffe - PA6'
    MAT11 = 'Nichteisenmetalle - Zink'
    MAT12 = 'Chromstahl - X12CrNi17-7'
    MAT13 = 'Werkzeugstahl - HSS'
    MAT14 = 'Stahlguss - GS-C25'
    MAT15 = 'Aluminiumlegierungen - AlSi1MgMn'
    MAT16 = 'Kugellagerstahl - 100Cr6'
    MAT17 = 'Rostfreier Stahl - X6Cr17'
    MAT18 = 'Titanlegierungen - TiAl6V4'
    MAT19 = 'Hochtemperaturlegierungen - Inconel 718'
    MAT20 = 'Zinklegierungen - ZL0410'
    MAT21 = 'Kohlenstoffstahl - C55'
    MAT22 = 'Aluminiumbronze - CuAl10Ni'
    MAT23 = 'Nickel-Chrom-Legierungen - Nichrome'
    MAT24 = 'Superlegierungen - Inconel 625'
    MAT25 = 'Verbundwerkstoffe - GFK'
    


class Part(db.Model):
    __tablename__ = 'part'

    id = db.Column(db.Integer, primary_key=True)
    originalFilename = db.Column(db.String(100), nullable=False)
    stepStorageFilePath = db.Column(db.String(100), nullable=False)
    stlStorageFilePath = db.Column(db.String(100), nullable=False)
    objStorageFilePath = db.Column(db.String(100), nullable=False)
    voxelStorageFilePath = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.String(500), nullable=True)
    customer = db.Column(db.String(100), nullable=True)
    drawingNumber = db.Column(db.String(500), nullable=True)
    orderNumber = db.Column(db.String(500), nullable=True)
    drawingStorageFilePath = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    material = db.Column(db.String(100), nullable=True)
    isSawing = db.Column(db.Boolean, nullable=True)
    isMeasuring = db.Column(db.Boolean, nullable=True)
    isLaserEngraving = db.Column(db.Boolean, nullable=True)
    isHardening = db.Column(db.Boolean, nullable=True)
    isStartholeDrilling = db.Column(db.Boolean, nullable=True)
    isSinkEroding = db.Column(db.Boolean, nullable=True)
    isHoning = db.Column(db.Boolean, nullable=True)
    isPolishing = db.Column(db.Boolean, nullable=True)

# Initialize the database
with app.app_context():
    db.create_all()

    
def createFile(file, comment, material,
               customer,
               drawingNumber,
               orderNumber,
               drawingFile,
               isSawing,
               isMeasuring,
               isLaserEngraving,
               isHardening,
               isStartholeDrilling,
               isSinkEroding,
               isHoning,
               isPolishing):

    # Save file to the upload folder
    originalFilename = file.filename
    
    if drawingFile:
        originalDrawingEnding = os.path.splitext(drawingFile.filename)[1] 
    else:
        originalDrawingEnding= None

    filename = str(uuid.uuid4())
    

    
    stepStorageFilePath=os.path.join(app.config['UPLOAD_FOLDER'], filename+ '.stp')
    stlStorageFilePath=os.path.join(app.config['UPLOAD_FOLDER'], filename+ '.stl')
    objStorageFilePath=os.path.join(app.config['UPLOAD_FOLDER'], filename+ '.obj')
    voxelStorageFilePath=os.path.join(app.config['UPLOAD_FOLDER'], filename+ '.npy')
    
    if drawingFile:
        drawingStorageFilePath=os.path.join(app.config['UPLOAD_FOLDER'], filename+ originalDrawingEnding)
        drawingFile.save(drawingStorageFilePath)
    else:
        drawingStorageFilePath=None
    file.save(stepStorageFilePath)

    ## dirty, but Trimesh cannot run in flask in a thread
    
    with app.app_context():
        subprocess.run(
        ['python3', 'create_mesh.py', stepStorageFilePath, stlStorageFilePath, objStorageFilePath, voxelStorageFilePath],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    

        # Store text input in SQLite database
        part = Part(originalFilename=originalFilename, 
                    stepStorageFilePath = stepStorageFilePath,
                    stlStorageFilePath = stlStorageFilePath, 
                    objStorageFilePath = objStorageFilePath,
                    voxelStorageFilePath = voxelStorageFilePath,
                    comment=comment,
                    customer = customer,
                    drawingNumber = drawingNumber,
                    orderNumber = orderNumber,
                    drawingStorageFilePath = drawingStorageFilePath,
                    material=material,
                    isSawing=isSawing,
                    isMeasuring=isMeasuring,
                    isLaserEngraving=isLaserEngraving,
                    isHardening=isHardening,
                    isStartholeDrilling=isStartholeDrilling,
                    isSinkEroding=isSinkEroding,
                    isHoning=isHoning,
                    isPolishing=isPolishing)
        db.session.add(part)
        db.session.commit()


@app.route('/parts/stl/<int:part_id>', methods=['GET'])
def get_stl(part_id):
    part = Part.query.get_or_404(part_id)
    stl_path = part.stlStorageFilePath
    return send_file(stl_path, as_attachment=True)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        return redirect(url_for('index'))
    

    data=[]
    
    return render_template('index.html', data=data)


@app.route('/upload', methods=['GET'])
def upload():
    return render_template('upload.html', material=Material)

@app.route('/upload', methods=['POST'])
def upload_page():
    # Get data from the form
    file = request.files['file']
    comment = request.form['comment']

    drawingFile = request.files['drawingFile']


    material = request.form.get('material')
    if material == '':
        material=None
        
    isSawing = request.form.get('isSawing')
    isSawing = bool(isSawing) if isSawing else None

    isMeasuring = request.form.get('isMeasuring')
    isMeasuring = bool(isMeasuring) if isMeasuring else None
    
    isLaserEngraving = request.form.get('isLaserEngraving')
    isLaserEngraving = bool(isLaserEngraving) if isLaserEngraving else None
    
    isHardening = request.form.get('isHardening')
    isHardening = bool(isHardening) if isHardening else None
    
    isStartholeDrilling = request.form.get('isStartholeDrilling')
    isStartholeDrilling = bool(isStartholeDrilling) if isStartholeDrilling else None
    
    isSinkEroding = request.form.get('isSinkEroding')
    isSinkEroding = bool(isSinkEroding) if isSinkEroding else None

    isHoning = request.form.get('isHoning')
    isHoning = bool(isHoning) if isHoning else None

    isPolishing = request.form.get('isPolishing')
    isPolishing = bool(isPolishing) if isPolishing else None

    customer = request.form.get('customer')
    if customer == '':
        customer=None
        
    drawingNumber = request.form.get('drawingNumber')
    if drawingNumber == '':
        drawingNumber=None
        
    orderNumber = request.form.get('orderNumber')
    if orderNumber == '':
        orderNumber=None

        

    createFile(file, comment, material,
                customer,
                drawingNumber,
                orderNumber,
                drawingFile,
                isSawing,
                isMeasuring,
                isLaserEngraving,
                isHardening,
                isStartholeDrilling,
                isSinkEroding,
                isHoning,
                isPolishing)
    

        
    return redirect(url_for('parts'))



@app.route('/uploadMultiple', methods=['GET'])
def upload_multiple_page():
    return render_template('uploadMultiple.html')


@app.route('/uploadMultiple', methods=['POST'])
def upload_multiple():
    # Get data from the form
    file = request.files['file']

    if file.filename.endswith('.zip'):
        with zipfile.ZipFile(file, 'r') as zip_ref:
            for member in zip_ref.infolist():
                if member.filename.endswith(('.stp', '.STEP')) and not member.filename.startswith('__MACOSX/'):
                    # Extract the part file from the zip
                    tmp_folder_name = str(uuid.uuid4())
                    tmp_folder_path = os.path.join('tmp', tmp_folder_name)

                    ## TODO: delete tmp folder
                    zip_ref.extract(member, path=tmp_folder_path)
                    extracted_file_path = os.path.join(tmp_folder_path, member.filename)
                
                    with open(extracted_file_path, 'rb') as f:
                        # Create a BytesIO object from the byte stream
                        file = io.BytesIO(f.read())
                        name = os.path.basename(extracted_file_path)
                        file_storage = FileStorage(stream=file, filename=name)

                    # Create a Part object using the byte stream
                    createFile(file_storage, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
        
        return redirect(url_for('parts'))
    else:
        return 'Invalid file format. Please upload a ZIP file.'

    

@app.route('/parts/delete/<int:part_id>', methods=['GET', 'POST'])
def delete_part(part_id):
    part = Part.query.get(part_id)
    if part:
        db.session.delete(part)
        db.session.commit()
        
        try:
            os.remove( part.stepStorageFilePath)
            os.remove( part.stlStorageFilePath)
            os.remove( part.objStorageFilePath)
            os.remove( part.voxelStorageFilePath)
        except:
            pass

        return redirect(url_for('parts'))
    else:
        return 'Part not found!'
    
@app.route('/parts', methods=['GET'])
def parts():
    parts = Part.query.all()
    return render_template('parts.html', parts=parts)

@app.route('/parts/<int:part_id>', methods=['GET'])
def view_part(part_id):
    part = Part.query.get_or_404(part_id)
    
    
    ### here comes the ml model
    #vorgangsfolge = getVorgangsfolge(filenameVoxel)
    ### here comes the ml model
    vorgangsfolge=["a","vorgangsfolge"]
    
    return render_template('part.html', part=part, vorgangsfolge=vorgangsfolge)

@app.route('/parts/edit/<int:part_id>', methods=['POST'])
def update_part(part_id):
    part = Part.query.get_or_404(part_id)
    
    
    
    isSawing = request.form.get('isSawing')
    isSawing = bool(isSawing) if isSawing else None
    part.isSawing = isSawing

    isMeasuring = request.form.get('isMeasuring')
    isMeasuring = bool(isMeasuring) if isMeasuring else None
    part.isMeasuring=isMeasuring
    
    isLaserEngraving = request.form.get('isLaserEngraving')
    isLaserEngraving = bool(isLaserEngraving) if isLaserEngraving else None
    part.isLaserEngraving = isLaserEngraving
    
    isHardening = request.form.get('isHardening')
    isHardening = bool(isHardening) if isHardening else None
    part.isHardening=isHardening
    
    isStartholeDrilling = request.form.get('isStartholeDrilling')
    isStartholeDrilling = bool(isStartholeDrilling) if isStartholeDrilling else None
    part.isStartholeDrilling= isStartholeDrilling
    
    isSinkEroding = request.form.get('isSinkEroding')
    isSinkEroding = bool(isSinkEroding) if isSinkEroding else None
    part.isSinkEroding=isSinkEroding
    
    isHoning = request.form.get('isHoning')
    isHoning = bool(isHoning) if isHoning else None
    part.isHoning=isHoning

    isPolishing = request.form.get('isPolishing')
    isPolishing = bool(isPolishing) if isPolishing else None
    part.isPolishing=isPolishing



    material = request.form.get('material')
    if material == '':
        material=None


    drawingNumber = request.form.get('drawingNumber')
    if drawingNumber == '':
        drawingNumber=None

    customer = request.form.get('customer')
    if customer == '':
        customer=None
        
    orderNumber = request.form.get('orderNumber')
    if orderNumber == '':
        orderNumber=None
        
    comment = request.form.get('comment')
    if comment == '':
        comment=None
        

    part.comment = comment
    part.customer = customer
    part.material = material
    part.drawingNumber = drawingNumber
    part.orderNumber = orderNumber



    db.session.commit()
    return redirect(url_for('parts'))

@app.route('/parts/edit/<int:part_id>', methods=['GET'])
def edit_part(part_id):
    part = Part.query.get_or_404(part_id)


    return render_template('edit_part.html', part=part, 
                           material=Material,
                           isSawing=part.isSawing)

def createVoxel(filename): 
    ### function goes here
    return filename

def getVorgangsfolge(filenameVoxel):
    return ["Materialentnahme", "CAM programmieren", "Weichfräsen", "Härten", "Drahterodieren", "Werkbank", "Montage"]
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5002)
