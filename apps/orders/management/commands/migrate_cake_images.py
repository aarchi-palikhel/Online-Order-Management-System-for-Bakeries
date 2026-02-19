"""
Management command to migrate existing cake design images from CakeCustomization to CakeDesignReference
"""
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from orders.models import Order, OrderItem, CakeDesignReference, CakeCustomization
from cart.models import CartItem


class Command(BaseCommand):
    help = 'Migrate existing cake design reference images from CakeCustomization to CakeDesignReference'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without actually migrating',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        self.stdout.write('Starting migration of cake design images...\n')
        
        # Find all OrderItems that are cakes
        cake_order_items = OrderItem.objects.filter(
            product__is_cake=True
        ).select_related('order', 'product')
        
        total_items = cake_order_items.count()
        self.stdout.write(f'Found {total_items} cake order items\n')
        
        migrated_count = 0
        skipped_count = 0
        error_count = 0
        
        for order_item in cake_order_items:
            try:
                # Check if design reference already exists
                existing_ref = CakeDesignReference.objects.filter(
                    order=order_item.order,
                    order_item=order_item
                ).first()
                
                if existing_ref:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  ⚠ OrderItem #{order_item.id}: Design reference already exists (ID: {existing_ref.id})'
                        )
                    )
                    skipped_count += 1
                    continue
                
                # Try to find the CakeCustomization that was used for this order
                # Look for cart items that might have been used
                customization = None
                
                # Method 1: Check if there's a CakeCustomization with matching details
                customizations = CakeCustomization.objects.filter(
                    user=order_item.order.user,
                    product=order_item.product,
                    reference_image__isnull=False
                ).order_by('-created_at')
                
                # Try to match by delivery date or other details
                for cust in customizations:
                    if cust.delivery_date == order_item.delivery_date:
                        customization = cust
                        break
                
                # If no exact match, take the most recent one with an image
                if not customization and customizations.exists():
                    customization = customizations.first()
                
                if not customization or not customization.reference_image:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  ⚠ OrderItem #{order_item.id}: No customization with image found'
                        )
                    )
                    skipped_count += 1
                    continue
                
                # Found a customization with image - migrate it
                if dry_run:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ Would migrate: OrderItem #{order_item.id} '
                            f'(Order: {order_item.order.order_number}, '
                            f'Image: {customization.reference_image.name})'
                        )
                    )
                    migrated_count += 1
                else:
                    # Actually create the CakeDesignReference
                    image_file = customization.reference_image
                    
                    design_ref = CakeDesignReference(
                        order=order_item.order,
                        order_item=order_item,
                        title=customization.reference_title or f"Design for {order_item.product.name}",
                        description=customization.reference_description or f"Custom cake order",
                    )
                    
                    # Copy the image file
                    design_ref.image.save(
                        image_file.name,
                        ContentFile(image_file.read()),
                        save=False
                    )
                    design_ref.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ Migrated: OrderItem #{order_item.id} '
                            f'(Order: {order_item.order.order_number}, '
                            f'Image: {image_file.name}) → CakeDesignReference #{design_ref.id}'
                        )
                    )
                    migrated_count += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'  ✗ Error with OrderItem #{order_item.id}: {str(e)}'
                    )
                )
                error_count += 1
                import traceback
                traceback.print_exc()
        
        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'\nMigration Summary:'))
        self.stdout.write(f'  Total cake order items: {total_items}')
        self.stdout.write(self.style.SUCCESS(f'  Migrated: {migrated_count}'))
        self.stdout.write(self.style.WARNING(f'  Skipped: {skipped_count}'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'  Errors: {error_count}'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN - No changes were made'))
            self.stdout.write('Run without --dry-run to actually migrate the images')
        else:
            self.stdout.write(self.style.SUCCESS('\n✓ Migration complete!'))
