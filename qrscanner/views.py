import os
from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from pyzxing import BarCodeReader
from datetime import datetime

reader = BarCodeReader()
UPLOAD_FOLDER = 'media/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return filename.split('.')[-1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def index(request):
    return render(request, 'index.html')

def scan_qr_code(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        if not allowed_file(file.name):
            return JsonResponse({'error': 'Invalid file type'}, status=400)
        
        fs = FileSystemStorage(location=UPLOAD_FOLDER)
        file_path = fs.save('scanned_qr.png', file)
        full_path = os.path.join(UPLOAD_FOLDER, file_path)

        result = reader.decode(full_path)
        if not result or 'parsed' not in result[0]:
            return JsonResponse({'error': 'No QR code found'}, status=400)

        qr_data = result[0]['parsed']
        try:
            url_params = dict(param.split('=') for param in qr_data.split('?')[1].split('&'))
        except IndexError:
            return JsonResponse({'error': 'QR code is malformed'}, status=400)

        teacher = url_params.get('teacher', 'Unknown')
        classroom = url_params.get('classroom', 'Unknown')
        timestamp = url_params.get('timestamp', '0')

        try:
            scan_time = datetime.utcfromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            scan_time = 'Invalid timestamp'

        return render(request, 'scan_result.html', {
            'teacher': teacher,
            'classroom': classroom,
            'timestamp': scan_time
        })
    return JsonResponse({'error': 'No file provided'}, status=400)
