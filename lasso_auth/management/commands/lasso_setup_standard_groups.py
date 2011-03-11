from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
import lasso_auth.models
import django.contrib.auth.models

def permissions_to_query(*perm):
    res = None
    for p in perm:
        cp = Q(content_type__app_label=p[0], content_type__name=p[1], codename=p[2])
        if res is None:
            res = cp
        else:
            res = res | cp
    return res

def create_group(name, *permissions):
        group_l = lasso_auth.models.Group.objects.filter(name=name).all()

        if len(group_l) == 0:
            group = lasso_auth.models.Group(name=name)
            group.save()
        else:
            group = group_l[0]

        group.permissions.clear()
        for permission in django.contrib.auth.models.Permission.objects.filter(permissions_to_query(*permissions)).all():
            group.permissions.add(permission)
        group.save()

def create_user(username, password, is_superuser, *groups):
        user_l = lasso_auth.models.User.objects.filter(username=username).all()

        if len(user_l) == 0:
            user = lasso_auth.models.User(username=username)
            user.save()
        else:
            user = user_l[0]

        user.groups.clear()
        for group in lasso_auth.models.Group.objects.filter(name__in=groups):
            user.groups.add(group)

        user.set_password(password)
        user.is_staff = True
        user.is_superuser = is_superuser

        user.save()

class Command(BaseCommand):
    args = ''
    help = 'Logs all used storage for the day'

    def handle(self, *args, **options):
        create_group("Admin",
                     ('lasso_auth', 'group', 'add_group'),
                     ('lasso_auth', 'group', 'change_group'),
                     ('lasso_auth', 'group', 'delete_group'),
                     ('lasso_auth', 'user', 'add_user'),
                     ('lasso_auth', 'user', 'change_user'),
                     ('lasso_auth', 'user', 'delete_user'),
                     ('lasso_customer', 'contact', 'add_contact'),
                     ('lasso_customer', 'contact', 'change_access'),
                     ('lasso_customer', 'contact', 'change_access_contact'),
                     ('lasso_customer', 'contact', 'change_contact'),
                     ('lasso_customer', 'contact', 'delete_contact'),
                     ('lasso_customer', 'Customer', 'add_customer'),
                     ('lasso_customer', 'Customer', 'change_customer'),
                     ('lasso_customer', 'Customer', 'delete_customer'),
                     ('lasso_customer', 'Destination', 'add_destination'),
                     ('lasso_customer', 'Destination', 'change_destination'),
                     ('lasso_customer', 'Destination', 'delete_destination'),
                     ('lasso_customer', 'Organization', 'add_organization'),
                     ('lasso_customer', 'Organization', 'change_organization'),
                     ('lasso_customer', 'Organization', 'delete_organization'),
                     ('lasso_customer', 'Original seller', 'add_originalseller'),
                     ('lasso_customer', 'Original seller', 'change_originalseller'),
                     ('lasso_customer', 'Original seller', 'delete_originalseller'),
                     ('lasso_customer', 'Transporter', 'add_transporter'),
                     ('lasso_customer', 'Transporter', 'change_transporter'),
                     ('lasso_customer', 'Transporter', 'delete_transporter'),
                     ('lasso_customer', 'Unit work price', 'add_unitworkprices'),
                     ('lasso_customer', 'Unit work price', 'change_unitworkprices'),
                     ('lasso_customer', 'Unit work price', 'delete_unitworkprices'),
                     ('lasso_customer', 'Unit work type', 'add_unitworktype'),
                     ('lasso_customer', 'Unit work type', 'change_unitworktype'),
                     ('lasso_customer', 'Unit work type', 'delete_unitworktype'),
                     ('lasso_customer', 'warehandling price', 'add_warehandlingprice'),
                     ('lasso_customer', 'warehandling price', 'change_warehandlingprice'),
                     ('lasso_customer', 'warehandling price', 'delete_warehandlingprice'),
                     ('lasso_global', 'insurance', 'add_insurance'),
                     ('lasso_global', 'insurance', 'change_insurance'),
                     ('lasso_global', 'insurance', 'delete_insurance'),
                     ('lasso_global', 'origin', 'add_origin'),
                     ('lasso_global', 'origin', 'change_origin'),
                     ('lasso_global', 'origin', 'delete_origin'),
                     ('lasso_global', 'Transport condition', 'add_transportcondition'),
                     ('lasso_global', 'Transport condition', 'change_transportcondition'),
                     ('lasso_global', 'Transport condition', 'delete_transportcondition'),
                     ('lasso_global', 'Vehicle type', 'add_vehicletype'),
                     ('lasso_global', 'Vehicle type', 'change_vehicletype'),
                     ('lasso_global', 'Vehicle type', 'delete_vehicletype'),
                     ('lasso_labelprinting', 'Address', 'add_address'),
                     ('lasso_labelprinting', 'Address', 'change_address'),
                     ('lasso_labelprinting', 'Address', 'delete_address'),
                     ('lasso_warehandling', 'Entry', 'add_entry'),
                     ('lasso_warehandling', 'Entry', 'change_entry'),
                     ('lasso_warehandling', 'Entry', 'delete_entry'),
                     ('lasso_warehandling', 'Entry', 'view_entry'),
                     ('lasso_warehandling', 'Entry', 'view_own_entry'),
                     ('lasso_warehandling', 'Entry row', 'add_entryrow'),
                     ('lasso_warehandling', 'Entry row', 'change_entryrow'),
                     ('lasso_warehandling', 'Entry row', 'delete_entryrow'),
                     ('lasso_warehandling', 'storage log', 'add_storagelog'),
                     ('lasso_warehandling', 'storage log', 'change_storagelog'),
                     ('lasso_warehandling', 'storage log', 'delete_storagelog'),
                     ('lasso_warehandling', 'storage log', 'view_own_storagelog'),
                     ('lasso_warehandling', 'storage log', 'view_storagelog'),
                     ('lasso_warehandling', 'unit work', 'add_unitwork'),
                     ('lasso_warehandling', 'unit work', 'change_unitwork'),
                     ('lasso_warehandling', 'unit work', 'delete_unitwork'),
                     ('lasso_warehandling', 'unit work', 'view_own_unitwork'),
                     ('lasso_warehandling', 'unit work', 'view_unitwork'),
                     ('lasso_warehandling', 'Withdrawal', 'add_withdrawal'),
                     ('lasso_warehandling', 'Withdrawal', 'change_withdrawal'),
                     ('lasso_warehandling', 'Withdrawal', 'delete_withdrawal'),
                     ('lasso_warehandling', 'Withdrawal', 'view_own_withdrawal'),
                     ('lasso_warehandling', 'Withdrawal', 'view_withdrawal'),
                     ('lasso_warehandling', 'Withdrawal row', 'add_withdrawalrow'),
                     ('lasso_warehandling', 'Withdrawal row', 'change_withdrawalrow'),
                     ('lasso_warehandling', 'Withdrawal row', 'delete_withdrawalrow'),
                     ('lasso_warehouse', 'empty pallet space', 'add_emptypalletspace'),
                     ('lasso_warehouse', 'empty pallet space', 'change_emptypalletspace'),
                     ('lasso_warehouse', 'empty pallet space', 'delete_emptypalletspace'),
                     ('lasso_warehouse', 'filled pallet space', 'add_filledpalletspace'),
                     ('lasso_warehouse', 'filled pallet space', 'change_filledpalletspace'),
                     ('lasso_warehouse', 'filled pallet space', 'delete_filledpalletspace'),
                     ('lasso_warehouse', 'Pallet space', 'add_emptypalletspace'),
                     ('lasso_warehouse', 'Pallet space', 'add_filledpalletspace'),
                     ('lasso_warehouse', 'Pallet space', 'add_palletspace'),
                     ('lasso_warehouse', 'Pallet space', 'change_emptypalletspace'),
                     ('lasso_warehouse', 'Pallet space', 'change_filledpalletspace'),
                     ('lasso_warehouse', 'Pallet space', 'change_palletspace'),
                     ('lasso_warehouse', 'Pallet space', 'delete_emptypalletspace'),
                     ('lasso_warehouse', 'Pallet space', 'delete_filledpalletspace'),
                     ('lasso_warehouse', 'Pallet space', 'delete_palletspace'),
                     ('lasso_warehouse', 'Row', 'add_row'),
                     ('lasso_warehouse', 'Row', 'change_row'),
                     ('lasso_warehouse', 'Row', 'delete_row'),
                     ('lasso_warehouse', 'Warehouse', 'add_warehouse'),
                     ('lasso_warehouse', 'Warehouse', 'change_warehouse'),
                     ('lasso_warehouse', 'Warehouse', 'delete_warehouse'))

        create_group("Employee",
                     ('lasso_customer', 'contact', 'add_contact'),
                     ('lasso_customer', 'contact', 'change_contact'),
                     ('lasso_customer', 'Customer', 'add_customer'),
                     ('lasso_customer', 'Customer', 'change_customer'),
                     ('lasso_customer', 'Destination', 'add_destination'),
                     ('lasso_customer', 'Destination', 'change_destination'),
                     ('lasso_customer', 'Organization', 'add_organization'),
                     ('lasso_customer', 'Organization', 'change_organization'),
                     ('lasso_customer', 'Original seller', 'add_originalseller'),
                     ('lasso_customer', 'Original seller', 'change_originalseller'),
                     ('lasso_customer', 'Transporter', 'add_transporter'),
                     ('lasso_customer', 'Transporter', 'change_transporter'),
                     ('lasso_customer', 'Unit work price', 'add_unitworkprices'),
                     ('lasso_customer', 'Unit work price', 'change_unitworkprices'),
                     ('lasso_customer', 'Unit work type', 'add_unitworktype'),
                     ('lasso_customer', 'Unit work type', 'change_unitworktype'),
                     ('lasso_global', 'origin', 'add_origin'),
                     ('lasso_global', 'origin', 'change_origin'),
                     ('lasso_labelprinting', 'Address', 'add_address'),
                     ('lasso_labelprinting', 'Address', 'change_address'),
                     ('lasso_warehandling', 'Entry', 'add_entry'),
                     ('lasso_warehandling', 'Entry', 'change_entry'),
                     ('lasso_warehandling', 'Entry', 'view_entry'),
                     ('lasso_warehandling', 'Entry', 'view_own_entry'),
                     ('lasso_warehandling', 'Entry row', 'add_entryrow'),
                     ('lasso_warehandling', 'Entry row', 'change_entryrow'),
                     ('lasso_warehandling', 'storage log', 'add_storagelog'),
                     ('lasso_warehandling', 'storage log', 'change_storagelog'),
                     ('lasso_warehandling', 'storage log', 'view_own_storagelog'),
                     ('lasso_warehandling', 'storage log', 'view_storagelog'),
                     ('lasso_warehandling', 'unit work', 'add_unitwork'),
                     ('lasso_warehandling', 'unit work', 'change_unitwork'),
                     ('lasso_warehandling', 'unit work', 'view_own_unitwork'),
                     ('lasso_warehandling', 'unit work', 'view_unitwork'),
                     ('lasso_warehandling', 'Withdrawal', 'add_withdrawal'),
                     ('lasso_warehandling', 'Withdrawal', 'change_withdrawal'),
                     ('lasso_warehandling', 'Withdrawal', 'view_own_withdrawal'),
                     ('lasso_warehandling', 'Withdrawal', 'view_withdrawal'),
                     ('lasso_warehandling', 'Withdrawal row', 'add_withdrawalrow'),
                     ('lasso_warehandling', 'Withdrawal row', 'change_withdrawalrow'),
                     ('lasso_warehouse', 'Pallet space', 'add_emptypalletspace'),
                     ('lasso_warehouse', 'Pallet space', 'add_filledpalletspace'),
                     ('lasso_warehouse', 'Pallet space', 'add_palletspace'),
                     ('lasso_warehouse', 'Pallet space', 'change_emptypalletspace'),
                     ('lasso_warehouse', 'Pallet space', 'change_filledpalletspace'),
                     ('lasso_warehouse', 'Pallet space', 'change_palletspace'),
                     ('lasso_warehouse', 'Row', 'add_row'),
                     ('lasso_warehouse', 'Row', 'change_row'),
                     ('lasso_warehouse', 'Warehouse', 'add_warehouse'),
                     ('lasso_warehouse', 'Warehouse', 'change_warehouse'))

        create_user('admin', 'password', False, 'Admin')
        create_user('superadmin', 'password', True, 'Admin')
