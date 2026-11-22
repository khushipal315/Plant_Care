from django.db import models

# Create your models here.
class Plant(models.Model):

    plant_name = models.CharField(max_length=100)

    plant_type = models.CharField(
        max_length=100,
        default="Tomato"
    )

    location = models.CharField(
        max_length=200,
        blank=True
    )

    moisture_threshold = models.FloatField(default=30)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.plant_name


class SensorReading(models.Model):

    plant = models.ForeignKey(
        Plant,
        on_delete=models.CASCADE,
        related_name='readings'
    )

    moisture_value = models.FloatField()

    moisture_percent = models.FloatField()

    temperature = models.FloatField(
        null=True,
        blank=True
    )

    humidity = models.FloatField(
        null=True,
        blank=True
    )

    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.plant.plant_name} - {self.moisture_percent}%"


class DiseaseDetection(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    plant = models.ForeignKey(
        Plant,
        on_delete=models.CASCADE,
        related_name='detections'
    )

    image = models.ImageField(upload_to='tomato_leaves/')

    predicted_class = models.CharField(
        max_length=100,
        blank=True
    )

    confidence_score = models.FloatField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    detected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.plant.plant_name} - {self.status}"
