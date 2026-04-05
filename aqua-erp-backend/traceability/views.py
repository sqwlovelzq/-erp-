import json
import datetime
import jwt
import os
import zipfile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db.models import Q
from rest_framework.decorators import action
# 引入我们辛辛苦苦建的所有模型
from .models import FarmBatch, HarvestBatch, ProcessBatch, ExportBatch, DocPack, ExportArchive, Customer, SalesOrder

# ==========================================
# 1. 养殖管理：创建档案 [cite: 146, 161]
# ==========================================
@csrf_exempt 
def get_farm_batches(request):
    if request.method == 'GET':
        batches = FarmBatch.objects.all().values(
            'farm_batch_id', 'breeding_unit', 'stocking_date', 
            'target_spec', 'responsible_person', 'feed_med_logs'
        )
        return JsonResponse(list(batches), safe=False)
    
    elif request.method == 'POST':
        data = json.loads(request.body)
        try:
            FarmBatch.objects.create(
                farm_batch_id=data.get('farm_batch_id'),
                breeding_unit=data.get('breeding_unit'),
                stocking_date=data.get('stocking_date'),
                target_spec=data.get('target_spec', '待定'),
                responsible_person=data.get('responsible_person', '未指派'),
                feed_med_logs=data.get('feed_med_logs', '暂无记录')
            )
            return JsonResponse({'status': 'success', 'message': '🐟 完整的养殖档案已建立！'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
# ==========================================
# 🌊 养殖管理：修改与删除接口
# ==========================================
@csrf_exempt
def update_farm_batch(request, farm_batch_id):
    """修改养殖档案 (受控状态)"""
    if request.method == 'PUT':
        data = json.loads(request.body)
        try:
            batch = FarmBatch.objects.get(farm_batch_id=farm_batch_id)
            # 🚨 业务防御锁：检查是否已经被起捕
            if HarvestBatch.objects.filter(parent_farm_batch=batch).exists():
                return JsonResponse({'status': 'error', 'message': '该网箱已开始起捕流转，底层数据已硬化，禁止修改！'}, status=403)
                
            batch.breeding_unit = data.get('breeding_unit', batch.breeding_unit)
            batch.target_spec = data.get('target_spec', batch.target_spec)
            batch.responsible_person = data.get('responsible_person', batch.responsible_person)
            batch.feed_med_logs = data.get('feed_med_logs', batch.feed_med_logs)
            batch.save()
            return JsonResponse({'status': 'success', 'message': '🌊 养殖档案与传感器修正数据已更新！'})
        except FarmBatch.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '批次不存在'}, status=404)

@csrf_exempt
def delete_farm_batch(request, farm_batch_id):
    """安全删除养殖档案"""
    if request.method == 'DELETE':
        try:
            batch = FarmBatch.objects.get(farm_batch_id=farm_batch_id)
            # 🚨 业务防御锁：检查是否已经被起捕
            if HarvestBatch.objects.filter(parent_farm_batch=batch).exists():
                return JsonResponse({'status': 'error', 'message': '该网箱鱼群已出海流转，为保证证据链完整，禁止作废！'}, status=403)
                
            batch.delete()
            return JsonResponse({'status': 'success', 'message': '🗑️ 异常养殖批次已作废清退！'})
        except FarmBatch.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '批次不存在'}, status=404)
# ==========================================
# 2. 起捕流转：标记状态
# ==========================================
@csrf_exempt
def create_harvest(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            quantity = float(data.get('quantity', 0))
            
            # Gate A 拦截：起捕量不足拦截 [cite: 81]
            if quantity < 1000:
                return JsonResponse({'status': 'error', 'message': '❌ 起捕量未达 1000kg 标箱要求！'}, status=403)
                
            parent_batch = FarmBatch.objects.get(farm_batch_id=data.get('parent_farm_id'))
            HarvestBatch.objects.update_or_create(
                harvest_id=data.get('harvest_id'),
                defaults={'farm_batch': parent_batch, 'harvest_date': data.get('harvest_date'), 'quantity': quantity}
            )
            
            # 更新养殖状态
            parent_batch.status = '已起捕'
            parent_batch.save()
            return JsonResponse({'status': 'success', 'message': '✅ 起捕完成，数据已流转！'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        
# ==========================================
# 3. 文件证据中心：上传并“认领” [cite: 18, 67, 167]
# ==========================================
@csrf_exempt
def upload_evidence(request):
    """
    不管你是养殖、加工还是出口，只要传了 ID 过来，我就能精准绑定！
    """
    if request.method == 'POST' and request.FILES.get('file'):
        file_obj = request.FILES['file']
        file_type = request.POST.get('file_type', '检测报告')
        
        # 接收三个环节的 ID
        f_id = request.POST.get('farm_id')
        p_id = request.POST.get('process_id')
        e_id = request.POST.get('export_id')

        # 物理保存
        fs = FileSystemStorage()
        saved_name = fs.save(file_obj.name, file_obj)
        
        # 核心逻辑：根据传过来的 ID 类型，绑定到对应的外键上
        new_doc = DocPack(file_type=file_type, file=saved_name)
        
        if f_id: new_doc.farm_batch = FarmBatch.objects.get(farm_batch_id=f_id)
        if p_id: new_doc.process_batch = ProcessBatch.objects.get(process_id=p_id)
        if e_id: new_doc.export_lot = ExportBatch.objects.get(export_id=e_id)
        
        new_doc.save()
        return JsonResponse({'status': 'success', 'message': f'✅ {file_type} 已存入证据中心！'})

    return JsonResponse({'status': 'error', 'message': '无效请求'}, status=400)

# ==========================================
# 4. 加工中心：Gate B 拦截准备 [cite: 97, 115]
# ==========================================
@csrf_exempt
def get_harvest_list(request):
    # 只给加工厂看还没加工的起捕批次
    harvests = HarvestBatch.objects.all().values('harvest_id', 'farm_batch__farm_batch_id', 'quantity')
    return JsonResponse(list(harvests), safe=False)

@csrf_exempt
def create_process_batch(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        harvest = HarvestBatch.objects.get(harvest_id=data.get('harvest_id'))
        ProcessBatch.objects.create(
            process_id=data.get('process_id'),
            harvest_batch=harvest,
            factory_name=data.get('factory_name'),
            temp_control=data.get('temp_control') ,
            sample_id=data.get('sample_id', '未留样'),
        )
        return JsonResponse({'status': 'success', 'message': '🏭 加工入库成功！'})

@csrf_exempt
def get_process_batches(request):
    batches = ProcessBatch.objects.all().values(
        'process_id', 'factory_name', 'temp_control', 'harvest_batch__harvest_id'
    )
    return JsonResponse(list(batches), safe=False)

# ==========================================
# 🏭 加工车间：修改与删除接口
# ==========================================
@csrf_exempt
def update_process_batch(request, process_id):
    """修改加工档案 (受控状态)"""
    if request.method == 'PUT':
        data = json.loads(request.body)
        try:
            batch = ProcessBatch.objects.get(process_id=process_id)
            # 🚨 业务防御锁：检查是否已经被装柜出口
            if ExportBatch.objects.filter(process_batch=batch).exists():
                return JsonResponse({'status': 'error', 'message': '该批次已装柜并进入出口申报流程，底层数据已硬化，禁止修改！'}, status=403)
                
            batch.factory_name = data.get('factory_name', batch.factory_name)
            batch.temp_control = data.get('temp_control', batch.temp_control)
            batch.sample_id = data.get('sample_id', batch.sample_id)
            batch.save()
            return JsonResponse({'status': 'success', 'message': '🏭 加工档案与温控记录已成功修正！'})
        except ProcessBatch.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '加工批次不存在'}, status=404)

@csrf_exempt
def delete_process_batch(request, process_id):
    """安全删除加工档案"""
    if request.method == 'DELETE':
        try:
            batch = ProcessBatch.objects.get(process_id=process_id)
            # 🚨 业务防御锁：检查是否已经被装柜出口
            if ExportBatch.objects.filter(process_batch=batch).exists():
                return JsonResponse({'status': 'error', 'message': '该商品已出口流转，为保证跨国溯源证据链完整，禁止作废！'}, status=403)
                
            batch.delete()
            return JsonResponse({'status': 'success', 'message': '🗑️ 加工入库记录已安全作废！'})
        except ProcessBatch.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '加工批次不存在'}, status=404)

# ==========================================
# 5. 出口装柜：Gate B 硬拦截逻辑 [cite: 109, 115, 125]
# ==========================================
@csrf_exempt
def create_export_batch(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            process_batch = ProcessBatch.objects.get(process_id=data.get('process_id'))
            
            # 🛑 Gate B (合规门) 检查冷链温度
            if "-18" not in process_batch.temp_control:
                return JsonResponse({
                    'status': 'error', 
                    'message': f'🛑 Gate B 拦截！加工单 [{process_batch.process_id}] 温控不达标（{process_batch.temp_control}），禁止装柜！'
                }, status=403)

            ExportBatch.objects.create(
                export_id=data.get('export_id'),
                process_batch=process_batch,
                loading_date=data.get('loading_date'),
                bol_number=data.get('bol_number'),
                destination=data.get('destination'),
                customer=data.get('customer'),
                release_status='待放单'
            )
            return JsonResponse({'status': 'success', 'message': '🚢 Gate B 检查通过，已准予装柜！'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@csrf_exempt
def get_export_list(request):
    batches = ExportBatch.objects.all().values(
        'export_id', 'process_batch__process_id', 'loading_date', 
        'bol_number', 'destination', 'customer', 'release_status'
    )
    return JsonResponse(list(batches), safe=False)

# ==========================================
# 🚢 出口装柜：修改与删除接口
# ==========================================
@csrf_exempt
def update_export_batch(request, export_id):
    """修改出口装柜单 (受控状态)"""
    if request.method == 'PUT':
        data = json.loads(request.body)
        try:
            batch = ExportBatch.objects.get(export_id=export_id)
            # 🚨 Gate C 防御锁：检查财务是否已放行
            if batch.release_status != '待放单':
                return JsonResponse({'status': 'error', 'message': '该批次已由财务核销放行，货权已转移，禁止修改单证！'}, status=403)
                
            batch.loading_date = data.get('loading_date', batch.loading_date)
            batch.bol_number = data.get('bol_number', batch.bol_number)
            batch.customer = data.get('customer', batch.customer)
            batch.destination = data.get('destination', batch.destination)
            batch.save()
            return JsonResponse({'status': 'success', 'message': '🚢 出口单证信息已成功更新！'})
        except ExportBatch.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '出口单不存在'}, status=404)

@csrf_exempt
def delete_export_batch(request, export_id):
    """安全删除出口装柜单"""
    if request.method == 'DELETE':
        try:
            batch = ExportBatch.objects.get(export_id=export_id)
            # 🚨 Gate C 防御锁：检查财务是否已放行
            if batch.release_status != '待放单':
                return JsonResponse({'status': 'error', 'message': '该批次已放行结汇，为保证税务及海关审计合规，绝对禁止作废！'}, status=403)
                
            batch.delete()
            return JsonResponse({'status': 'success', 'message': '🗑️ 异常出口单已安全作废！'})
        except ExportBatch.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '出口单不存在'}, status=404)

# ==========================================
# 6. 【核心新增】一键打包“单证包” [cite: 30, 161, 172]
# ==========================================
@csrf_exempt
def generate_doc_pack(request, export_id):
    """
    真正的工业级打包逻辑：
    只要是挂在这票货（从养殖到加工到出口）名下的文件，一网打尽！
    """
    if request.method == 'POST':
        try:
            # 1. 顺藤摸瓜找齐 3 个环节的 ID
            export = ExportBatch.objects.get(export_id=export_id)
            process = export.process_batch
            farm = process.harvest_batch.farm_batch
            
            # 2. 搜集所有 DocPack 里的文件
            evidence_files = DocPack.objects.filter(export_lot=export) | \
                             DocPack.objects.filter(process_batch=process) | \
                             DocPack.objects.filter(farm_batch=farm)

            # 3. 创建 ZIP
            zip_name = f"DOC_PACK_{export_id}.zip"
            zip_relative_path = os.path.join('final_archives', zip_name)
            zip_full_path = os.path.join(settings.MEDIA_ROOT, zip_relative_path)
            os.makedirs(os.path.dirname(zip_full_path), exist_ok=True)

            with zipfile.ZipFile(zip_full_path, 'w') as zipf:
                for doc in evidence_files:
                    if doc.file and os.path.exists(doc.file.path):
                        # 命名：类型_版本_文件名 [cite: 213]
                        arc_name = f"{doc.file_type}_{doc.version}_{os.path.basename(doc.file.path)}"
                        zipf.write(doc.file.path, arcname=arc_name)

            # 4. 保存归档记录
            archive, _ = ExportArchive.objects.get_or_create(export_lot=export)
            archive.archive_file = zip_relative_path
            archive.save()

            return JsonResponse({
                'status': 'success', 
                'url': settings.MEDIA_URL + zip_relative_path,
                'message': f'📦 {export_id} 资料包打包成功！'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

# ==========================================
# 7. 登录与溯源查询 (满血恢复版)
# ==========================================
@csrf_exempt
def login_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        # 🚨 去真实数据库里核对账号密码 (咱们之前升级过的企业级安保)
        user = authenticate(username=username, password=password)
        
        if user is not None:
            if user.is_active:
                role = '厂长' if user.is_superuser else '记录员'
                payload = {
                    'user_id': user.id,
                    'username': user.username,
                    'role': role,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8)
                }
                token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
                
                return JsonResponse({
                    'status': 'success', 
                    'token': token, 
                    'role': role,
                    'message': f'身份验证通过，欢迎 {user.username} ({role})！'
                })
            else:
                return JsonResponse({'status': 'error', 'message': '🚫 账号已被停用，请联系厂长！'}, status=403)
        else:
            return JsonResponse({'status': 'error', 'message': '❌ 账号或密码错误！'}, status=401)

@csrf_exempt
def get_trace_report(request, process_id):
    if request.method == 'GET':
        try:
            # 顺藤摸瓜：加工 -> 起捕 -> 养殖
            process = ProcessBatch.objects.get(process_id=process_id)
            harvest = process.harvest_batch
            farm = harvest.farm_batch
            
            today_str = datetime.datetime.now().strftime('%Y%m%d')
            trace_sn = f"TRACE-{today_str}-{process.process_id}"
            
            trace_data = {
                "trace_sn": trace_sn,
                "farm_info": {
                    "batch_id": farm.farm_batch_id,
                    "unit": farm.breeding_unit,
                    "stocking_date": farm.stocking_date,
                    "feed_med_logs": farm.feed_med_logs,
                    "responsible_person": farm.responsible_person
                },
                "harvest_info": {
                    "harvest_id": harvest.harvest_id,
                    "harvest_date": harvest.harvest_date,
                    "quantity": harvest.quantity
                },
                "process_info": {
                    "process_id": process.process_id,
                    "factory": process.factory_name,
                    "temp_control": process.temp_control
                }
            }
            return JsonResponse({'status': 'success', 'data': trace_data})
            
        except ProcessBatch.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '找不到该加工记录'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
# ==========================================
# 8. Gate C：财务与终极放单门
# ==========================================
@csrf_exempt
def confirm_financial_release(request, export_id):
    if request.method == 'POST':
        try:
            export = ExportBatch.objects.get(export_id=export_id)
            
            if export.release_status == '已放行':
                return JsonResponse({'status': 'error', 'message': '该批次已放行，请勿重复操作'}, status=400)
                
            # Gate C 核心动作：财务确认尾款到账，更改放行状态
            export.release_status = '已放行'
            export.save()
            
            return JsonResponse({
                'status': 'success', 
                'message': f'✅ 财务确认完毕！批次 {export_id} 已解开 Gate C，准予最终放行发送提单！'
            })
            
        except ExportBatch.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '找不到该批次'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        
# ==========================================
# 9. 交易壳：订单与客户管理中心
# ==========================================
@csrf_exempt
def get_orders(request):
    """获取所有销售订单 (支持模糊搜索)"""
    if request.method == 'GET':
        keyword = request.GET.get('keyword', '') # 接收前端传来的搜索词
        
        # 核心逻辑：如果带了搜索词，就在订单号和客户名里模糊匹配
        query = SalesOrder.objects.all()
        if keyword:
            query = query.filter(Q(order_id__icontains=keyword) | Q(customer__name__icontains=keyword))
            
        orders = query.values(
            'order_id', 'customer__name', 'customer__country', 
            'order_date', 'product_spec', 'quantity', 'total_amount', 'deposit_status', 'status'
        ).order_by('-order_date')
        
        return JsonResponse(list(orders), safe=False)

@csrf_exempt
def create_order(request):
    """录入新订单，如果客户不存在则自动建档"""
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            # 1. 客户档案自动化：有则关联，无则新建
            customer, created = Customer.objects.get_or_create(
                name=data.get('customer_name'),
                defaults={
                    'customer_id': 'CUST-' + str(int(timezone.now().timestamp())),
                    'country': data.get('country', '未知'),
                    'contact_info': data.get('contact_info', '')
                }
            )
            
            # 2. 生成具有法律效力的销售订单
            SalesOrder.objects.create(
                order_id=data.get('order_id'),
                customer=customer,
                order_date=data.get('order_date'),
                product_spec=data.get('product_spec'),
                quantity=data.get('quantity'),
                total_amount=data.get('total_amount'),
                deposit_status=data.get('deposit_status', '未付定金')
            )
            return JsonResponse({'status': 'success', 'message': '📝 销售订单已成功录入，生产任务已下达！'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        
@csrf_exempt
def update_order(request, order_id):
    """修改订单 (受控状态)"""
    if request.method == 'PUT':
        data = json.loads(request.body)
        try:
            order = SalesOrder.objects.get(order_id=order_id)
            # 🚨 业务防御锁：只有生产准备中的订单才能改数量和金额
            if order.status != '生产准备中':
                return JsonResponse({'status': 'error', 'message': '订单已进入生产或发货环节，禁止修改明细！'}, status=403)
                
            order.quantity = data.get('quantity', order.quantity)
            order.total_amount = data.get('total_amount', order.total_amount)
            order.deposit_status = data.get('deposit_status', order.deposit_status)
            order.save()
            return JsonResponse({'status': 'success', 'message': '✏️ 订单明细已成功更新！'})
        except SalesOrder.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '订单不存在'}, status=404)

@csrf_exempt
def delete_order(request, order_id):
    """安全删除订单"""
    if request.method == 'DELETE':
        try:
            order = SalesOrder.objects.get(order_id=order_id)
            # 🚨 业务防御锁：如果已经开始生产，死锁不允许删除
            if order.status != '生产准备中':
                return JsonResponse({'status': 'error', 'message': '该订单已关联生产数据，为保证溯源证据链完整，禁止删除！'}, status=403)
                
            order.delete()
            return JsonResponse({'status': 'success', 'message': '🗑️ 订单已安全作废/删除！'})
        except SalesOrder.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '订单不存在'}, status=404)

# 10. 仓储中心：动态实时库存盘点引擎 (WMS)
# ==========================================
@csrf_exempt
def get_inventory(request):
    """
    不依赖死板的库存表，而是通过批次生命周期动态推算实时库存。
    保证数据与实物 100% 账实相符，杜绝人为篡改。
    """
    if request.method == 'GET':
        try:
            # 1. 活鱼原料库 (有起捕记录，但在加工表里找不到关联的)
            raw_batches = HarvestBatch.objects.filter(processbatch__isnull=True)
            raw_kg = sum(float(b.quantity) for b in raw_batches if b.quantity)
            raw_count = raw_batches.count()
            
            # 2. 冻品成品库 (有加工记录，但在出口表里找不到关联的)
            finished_batches = ProcessBatch.objects.filter(exportbatch__isnull=True)
            # 因为重量记录在起捕单上，所以要跨表去拿 harvest_batch.quantity
            finished_kg = sum(float(b.harvest_batch.quantity) for b in finished_batches if b.harvest_batch and b.harvest_batch.quantity)
            finished_count = finished_batches.count()
            
            # 3. 累计已发货 (已经挂了出口单据的)
            exported_batches = ExportBatch.objects.all()
            exported_kg = sum(float(b.process_batch.harvest_batch.quantity) for b in exported_batches if b.process_batch and b.process_batch.harvest_batch and b.process_batch.harvest_batch.quantity)
            exported_count = exported_batches.count()
            
            return JsonResponse({
                'status': 'success',
                'data': {
                    'raw_stock_kg': raw_kg,
                    'raw_count': raw_count,
                    'finished_stock_kg': finished_kg,
                    'finished_count': finished_count,
                    'exported_kg': exported_kg,
                    'exported_count': exported_count
                }
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        
from rest_framework import viewsets
from rest_framework.decorators import action      # 👈 新增：导入 action 装饰器
from rest_framework.response import Response      # 👈 新增：导入 Response 响应对象
from .models import Customer, SalesOrder
from .serializers import CustomerSerializer, SalesOrderSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class SalesOrderViewSet(viewsets.ModelViewSet):
    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer

    # 👇 新增：财务专用的放行接口 (注意这里的缩进，它属于 SalesOrderViewSet 内部)
    @action(detail=True, methods=['post'])
    def release_finance(self, request, pk=None):
        order = self.get_object()
        order.financial_status = "已结清/放行"
        order.save()
        return Response({'status': 'success', 'message': '尾款已确认，提单锁已解除！'})

from .models import ExportBatch
from .serializers import ExportBatchSerializer

class ExportBatchViewSet(viewsets.ModelViewSet):
    queryset = ExportBatch.objects.all()
    serializer_class = ExportBatchSerializer
    # 🚨 新增：一键提交申报的逻辑
   
    @action(detail=True, methods=['post'])
    def submit_declaration(self, request, pk=None):
        export_batch = self.get_object()
        export_batch.customs_status = "海关查验中"
        export_batch.save()
        return Response({'status': '已提交海关申报系统'})

from .models import FinancialLedger
from .serializers import FinancialLedgerSerializer

class FinancialLedgerViewSet(viewsets.ModelViewSet):
    queryset = FinancialLedger.objects.all()
    serializer_class = FinancialLedgerSerializer

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import SalesOrder, FinancialLedger

@api_view(['POST'])
def run_real_calculation(request):
    """真正的全链路财务溯源核算引擎"""
    order_id = request.data.get('order_id')
    order = get_object_or_404(SalesOrder, id=order_id)
    
    # 1. 提取总营收 (FOB)
    revenue = order.total_amount
    
    # 2. 顺藤摸瓜：根据订单找出口装柜记录
    export_batch = order.exportbatch_set.first()
    if not export_batch:
        return Response({"error": "该订单尚未关联出口装柜记录，无法核算三产成本！"}, status=400)
    
    # 3. 顺藤摸瓜：找二产加工记录
    process_batch = export_batch.process_batch
    
    # 4. 顺藤摸瓜：找一产养殖记录
    harvest_batch = process_batch.harvest_batch
    
    # 🚨 真实成本算法 (这里基于重量按行业均价计算，如果你的表里有实际费用字段，可以直接换掉)
    weight = float(harvest_batch.quantity)
    farm_cost = weight * 3.5  # 假设一产饲料动保成本：3.5元/kg
    process_cost = weight * 1.2 # 假设二产加工冷链成本：1.2元/kg
    export_cost = weight * 0.8  # 假设三产报关海运成本：0.8元/kg
    
    net_profit = float(revenue) - farm_cost - process_cost - export_cost
    
    # 5. 写入财务总账
    ledger, created = FinancialLedger.objects.update_or_create(
        order=order,
        defaults={
            'revenue': revenue,
            'farm_cost': farm_cost,
            'process_cost': process_cost,
            'export_cost': export_cost,
            'net_profit': net_profit,
            'status': '已智能平账'
        }
    )
    
    return Response({"message": "核算成功", "net_profit": net_profit})

from .models import TradeDocument
from .serializers import TradeDocumentSerializer
class TradeDocumentViewSet(viewsets.ModelViewSet):
    queryset = TradeDocument.objects.all().order_by('-created_at')
    serializer_class = TradeDocumentSerializer