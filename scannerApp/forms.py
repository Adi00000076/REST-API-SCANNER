from django import forms

class ScanForm(forms.Form):
    color_mode = forms.ChoiceField(
        choices=[('Color', 'Color'), ('Grayscale', 'Grayscale')],
        label='Color Mode',
        initial='Color'
    )
    zoom_level = forms.IntegerField(
        label='Zoom Level (%)',
        min_value=10,
        max_value=400,
        initial=100
    )
    num_pages = forms.IntegerField(
        label='Number of Pages',
        min_value=1,
        max_value=10,
        initial=1
    )

    def clean(self):
        cleaned_data = super().clean()
        zoom_level = cleaned_data.get('zoom_level')
        num_pages = cleaned_data.get('num_pages')

        # Add any additional validation if necessary
        if zoom_level and (zoom_level < 10 or zoom_level > 400):
            self.add_error('zoom_level', 'Zoom level must be between 10 and 400.')

        if num_pages and (num_pages < 1 or num_pages > 10):
            self.add_error('num_pages', 'Number of pages must be between 1 and 10.')

        return cleaned_data
