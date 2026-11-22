from django.shortcuts import render

# Create your views here.
import json

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import Plant, SensorReading, DiseaseDetection
from .forms import DiseaseDetectionForm


# HOME PAGE API

def dashboard_api(request):

    plants = Plant.objects.all()

    data = []

    for plant in plants:

        latest = plant.readings.order_by(
            '-recorded_at'
        ).first()

        plant_data = {
            'id': plant.id,
            'plant_name': plant.plant_name,
            'plant_type': plant.plant_type,
            'location': plant.location,
            'moisture_threshold': plant.moisture_threshold,
            'moisture_percent': None,
            'temperature': None,
            'humidity': None,
            'status': 'No sensor data',
            'last_updated': None,
        }

        if latest:

            plant_data.update({
                'moisture_percent': latest.moisture_percent,
                'temperature': latest.temperature,
                'humidity': latest.humidity,
                'status': (
                    'Low Moisture'
                    if latest.moisture_percent < plant.moisture_threshold
                    else 'Normal'
                ),
                'last_updated': latest.recorded_at.isoformat(),
            })

        data.append(plant_data)

    return JsonResponse({
        'success': True,
        'plants': data
    })


# ESP32 SENSOR DATA API

@csrf_exempt
@require_POST
def receive_sensor_data(request):

    api_key = request.headers.get('X-DEVICE-KEY')

    if api_key != settings.DEVICE_API_KEY:
        return JsonResponse({
            'success': False,
            'message': 'Unauthorized device'
        }, status=401)

    try:

        data = json.loads(request.body)

        plant_id = data.get('plant_id')
        moisture_value = data.get('moisture_value')
        moisture_percent = data.get('moisture_percent')
        temperature = data.get('temperature')
        humidity = data.get('humidity')

        if plant_id is None or moisture_value is None or moisture_percent is None:
            return JsonResponse({
                'success': False,
                'message': 'Required sensor data is missing'
            }, status=400)

        moisture_value = float(moisture_value)
        moisture_percent = float(moisture_percent)

        if not 0 <= moisture_percent <= 100:
            return JsonResponse({
                'success': False,
                'message': 'Invalid moisture percentage'
            }, status=400)

        if temperature is not None:
            temperature = float(temperature)

        if humidity is not None:
            humidity = float(humidity)

            if not 0 <= humidity <= 100:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid humidity value'
                }, status=400)

        plant = get_object_or_404(Plant, id=plant_id)

        reading = SensorReading.objects.create(
            plant=plant,
            moisture_value=moisture_value,
            moisture_percent=moisture_percent,
            temperature=temperature,
            humidity=humidity
        )

        return JsonResponse({
            'success': True,
            'message': 'Sensor data saved successfully',
            'reading_id': reading.id,
            'low_moisture_alert': (
                moisture_percent < plant.moisture_threshold
            )
        })

    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({
            'success': False,
            'message': 'Invalid sensor data'
        }, status=400)


# SENSOR HISTORY API

def sensor_history(request, plant_id):

    plant = get_object_or_404(Plant, id=plant_id)

    readings = SensorReading.objects.filter(
        plant=plant
    ).order_by('-recorded_at')[:50]

    data = []

    for reading in readings:

        data.append({
            'moisture_value': reading.moisture_value,
            'moisture_percent': reading.moisture_percent,
            'temperature': reading.temperature,
            'humidity': reading.humidity,
            'recorded_at': reading.recorded_at.isoformat()
        })

    return JsonResponse({
        'success': True,
        'plant': plant.plant_name,
        'readings': data
    })


# TOMATO LEAF IMAGE UPLOAD

@require_POST
def upload_leaf_image(request):

    form = DiseaseDetectionForm(request.POST, request.FILES)

    if form.is_valid():

        detection = form.save(commit=False)
        detection.save()

        return JsonResponse({
            'success': True,
            'message': 'Image uploaded successfully. AI analysis is pending.',
            'detection_id': detection.id,
            'status': detection.status
        }, status=201)

    return JsonResponse({
        'success': False,
        'errors': form.errors.get_json_data()
    }, status=400)


# DISEASE DETECTION HISTORY

def disease_history(request, plant_id):

    plant = get_object_or_404(Plant, id=plant_id)

    detections = DiseaseDetection.objects.filter(
        plant=plant
    ).order_by('-detected_at')

    data = []

    for detection in detections:

        data.append({
            'id': detection.id,
            'image': detection.image.url,
            'predicted_class': detection.predicted_class,
            'confidence_score': detection.confidence_score,
            'status': detection.status,
            'detected_at': detection.detected_at.isoformat()
        })

    return JsonResponse({
        'success': True,
        'plant': plant.plant_name,
        'detections': data
    })