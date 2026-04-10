from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from ..models import SubcontractList

@csrf_exempt
def subcontract_lists_by_contract(request):
    contract_id = request.GET.get('contract_id')
    if not contract_id:
        return HttpResponse('')
    
    subcontract_lists = SubcontractList.objects.filter(contract_id=contract_id)
    options = []
    for sl in subcontract_lists:
        options.append(f'<option value="{sl.pk}" data-category="{sl.category}" data-params="{sl.construction_params}" data-unit="{sl.unit}" data-quantity="{sl.quantity}">{sl.name}</option>')
    
    return HttpResponse('\n'.join(options))
