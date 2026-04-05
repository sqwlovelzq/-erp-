from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from traceability.views import run_real_calculation # 记得在顶部导入它！
from traceability.views import ExportBatchViewSet # 确保有这个


# 🚨 确保在这里把 login_api 也引进来
from traceability.views import (
    get_farm_batches, 
    create_harvest, 
    upload_evidence, 
    get_harvest_list, 
    create_process_batch,
    get_process_batches,
    get_trace_report,
    login_api,
    create_export_batch,
    get_export_list,
    generate_doc_pack,
    confirm_financial_release,
    get_orders,
    create_order,
    get_inventory,
    update_order,
    delete_order,
    update_farm_batch,
    delete_farm_batch,
    update_process_batch,
    delete_process_batch,
    update_export_batch,
    delete_export_batch,
    CustomerViewSet,    
    SalesOrderViewSet,
    ExportBatchViewSet,
    FinancialLedgerViewSet,
    run_real_calculation,
    TradeDocumentViewSet
)

urlpatterns = [
    # 后台管理员入口
    path('admin/', admin.site.urls),
    
    # 0. 🔐 安全认证系统
    path('api/login/', login_api),  # 👈 验证账号密码并发送 Token 的通道
    
    # 1. 🌊 养殖与起捕
    path('api/batches/', get_farm_batches),
    path('api/harvests/', create_harvest),
    path('api/batches/update/<str:farm_batch_id>/', update_farm_batch),
    path('api/batches/delete/<str:farm_batch_id>/', delete_farm_batch), 
    
    # 2. 📎 证据与文件上传
    path('api/upload/', upload_evidence),
    
    # 3. 🏭 加工环节流转
    path('api/harvest-list/', get_harvest_list),
    path('api/process/', create_process_batch),
    path('api/process-list/', get_process_batches),
    path('api/process/update/<str:process_id>/', update_process_batch), 
    path('api/process/delete/<str:process_id>/', delete_process_batch), 
    
    # 4. 📜 终极数字溯源档案
    path('api/trace/<str:process_id>/', get_trace_report), 

    # 5. 🚢 出口与放单中心
    path('api/export/', create_export_batch),
    path('api/export-list/', get_export_list),
    path('api/export/update/<str:export_id>/', update_export_batch),
    path('api/export/delete/<str:export_id>/', delete_export_batch),
    # 🚨 把这三行加到 urlpatterns 列表里面去
    path('api/gtm/exports/', ExportBatchViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/gtm/exports/<int:pk>/', ExportBatchViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    # 这就是你刚才苦苦寻找的“提交申报”专属通道！
    path('api/gtm/exports/<int:pk>/submit_declaration/', ExportBatchViewSet.as_view({'post': 'submit_declaration'})),
    
    # 6. 📦 资料包生成接口 (单证包导出)
    # <str:export_id> 的意思是：网址后面跟什么出口号，秘书就去打哪个包
    path('api/generate-pack/<str:export_id>/', generate_doc_pack), 
    
    # 7. 💰 财务放行 Gate C
    path('api/export/release/<str:export_id>/', confirm_financial_release), 
    
    # 8. 💼 交易壳：订单与客户中心
    path('api/orders/', get_orders),
    path('api/orders/create/', create_order),
    path('api/orders/update/<str:order_id>/', update_order), 
    path('api/orders/delete/<str:order_id>/', delete_order), 

    # 9. 📦 仓储与动态库存中心 (WMS)
    path('api/inventory/', get_inventory),

    # ==========================================
    # 🌟 10. GTM 全球贸易中枢 (在列表最后追加这4行)
    # ==========================================
    path('api/gtm/customers/', CustomerViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/gtm/customers/<int:pk>/', CustomerViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    path('api/gtm/sales-orders/', SalesOrderViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/gtm/sales-orders/<int:pk>/', SalesOrderViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    path('api/gtm/exports/', ExportBatchViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/gtm/exports/<int:pk>/', ExportBatchViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    path('api/gtm/finance/', FinancialLedgerViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/gtm/finance/<int:pk>/', FinancialLedgerViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    path('api/gtm/finance/run-calc/', run_real_calculation),
    path('api/gtm/documents/', TradeDocumentViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/gtm/documents/<int:pk>/', TradeDocumentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
