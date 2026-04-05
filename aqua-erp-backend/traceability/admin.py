from django.contrib import admin
from .models import FarmBatch, HarvestBatch, ProcessBatch, Customer, SalesOrder, ExportBatch, DocPack, ExportArchive

# 注册所有数据表到后台管理系统
admin.site.register(FarmBatch)
admin.site.register(HarvestBatch)
admin.site.register(ProcessBatch)
admin.site.register(DocPack)
admin.site.register(ExportArchive)

# 为了让 GTM 核心表在后台更好看，我们加一点简单的展示配置
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'credit_rating', 'total_trade_volume')
    search_fields = ('name', 'country')

@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'customer', 'total_amount', 'status')
    list_filter = ('status', 'deposit_status')

@admin.register(ExportBatch)
class ExportBatchAdmin(admin.ModelAdmin):
    list_display = ('export_id', 'sales_order', 'destination', 'customs_status')
    list_filter = ('customs_status', 'release_status')