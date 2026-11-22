from django import forms
from .models import DiseaseDetection


class DiseaseDetectionForm(forms.ModelForm):

    class Meta:
        model = DiseaseDetection

        fields = ['plant', 'image']

        widgets = {
            'plant': forms.Select(
                attrs={'class': 'form-control'}
            ),

            'image': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control',
                    'accept': 'image/*'
                }
            ),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')

        if image:
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError(
                    "Image size must be less than 5 MB."
                )

            if image.content_type not in [
                'image/jpeg',
                'image/png',
                'image/webp'
            ]:
                raise forms.ValidationError(
                    "Only JPG, PNG and WEBP images are allowed."
                )

        return image