from django.core.management.base import BaseCommand
from billing.models import Box, BoxPrice

class Command(BaseCommand):
    help = 'Load initial box data with prices'

    def handle(self, *args, **kwargs):
        box_data = [
            {'length': 4, 'width': 4, 'height': 4, 'prices': {'200LB': 0.85, 'ECT32': 0.74}},
            {'length': 5, 'width': 5, 'height': 5, 'prices': {'200LB': 1.07, 'ECT32': 0.97}},
            {'length': 6, 'width': 6, 'height': 2, 'prices': {'200LB': 1.28, 'ECT32': 0.41}},
            {'length': 6, 'width': 4, 'height': 4, 'prices': {'200LB': 0.95, 'ECT32': 0.90}},
            {'length': 6, 'width': 6, 'height': 4, 'prices': {'200LB': 1.04, 'ECT32': 0.92}},
            {'length': 6, 'width': 6, 'height': 6, 'prices': {'200LB': 0.92, 'ECT32': 0.83}},
            {'length': 6, 'width': 6, 'height': 6, 'prices': {'200LB': 2.31, 'ECT32': 0.27}},
            {'length': 7, 'width': 5, 'height': 5, 'prices': {'200LB': 1.07, 'ECT32': 0.96}},
            {'length': 8, 'width': 6, 'height': 4, 'prices': {'200LB': 1.10, 'ECT32': 1.03}},
            {'length': 8, 'width': 8, 'height': 4, 'prices': {'200LB': 1.66, 'ECT32': 1.52}},
            {'length': 10, 'width': 6, 'height': 6, 'prices': {'200LB': 1.35, 'ECT32': 1.23}},
            {'length': 12, 'width': 9, 'height': 4, 'prices': {'200LB': 2.19, 'ECT32': 1.94}},
            {'length': 12, 'width': 9, 'height': 6, 'prices': {'200LB': 2.44, 'ECT32': 2.20}},
            {'length': 12, 'width': 10, 'height': 6, 'prices': {'200LB': 2.48, 'ECT32': 2.29}},
            {'length': 14, 'width': 12, 'height': 6, 'prices': {'200LB': 3.62, 'ECT32': 3.22}},
            {'length': 14, 'width': 12, 'height': 8, 'prices': {'200LB': 3.36, 'ECT32': 3.07}},
            {'length': 14, 'width': 12, 'height': 10, 'prices': {'200LB': 4.33, 'ECT32': 3.85}},
            {'length': 17, 'width': 17, 'height': 14, 'prices': {'200LB': 5.30, 'ECT32': 0.39}},
            {'length': 18, 'width': 12, 'height': 12, 'prices': {'200LB': 4.44, 'ECT32': 4.07}},
            {'length': 18, 'width': 14, 'height': 14, 'prices': {'200LB': 6.50, 'ECT32': 5.84}},
            {'length': 20, 'width': 10, 'height': 10, 'prices': {'200LB': 6.09, 'ECT32': 5.60}},
            {'length': 22, 'width': 12, 'height': 12, 'prices': {'200LB': 7.17, 'ECT32': 5.58}},
            {'length': 26, 'width': 12, 'height': 10, 'prices': {'200LB': 8.30, 'ECT32': 7.65}},
        ]

        for box in box_data:
            new_box = Box.objects.create(
                length=box['length'],
                width=box['width'],
                height=box['height'],
                volume=box['length'] * box['width'] * box['height'],
                prices=box['prices']  # Assign prices here
            )
            for test_type, price in box['prices'].items():
                BoxPrice.objects.create(
                    box=new_box,
                    test_type=test_type,
                    price=price
                )

        self.stdout.write(self.style.SUCCESS('Successfully loaded initial box data'))
