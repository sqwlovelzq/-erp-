from django.db import models
from django.utils import timezone

# 1. 一产：养殖批次
class FarmBatch(models.Model):
    farm_batch_id = models.CharField("养殖批次号", max_length=50, unique=True)
    breeding_unit = models.CharField("养殖单元", max_length=50) 
    stocking_date = models.DateField("放养日期") 
    feed_med_logs = models.TextField("饲料/药物记录") 
    target_spec = models.CharField("目标规格", max_length=100, default="待定")
    status = models.CharField(max_length=20, default='养殖中', verbose_name='当前状态')
    responsible_person = models.CharField("责任人", max_length=50) 

    def __str__(self):
        return self.farm_batch_id

# 2. 一产：收获批次
class HarvestBatch(models.Model):
    harvest_id = models.CharField("收获编号", max_length=50, unique=True)
    farm_batch = models.ForeignKey(FarmBatch, on_delete=models.CASCADE, verbose_name="关联养殖批次")
    harvest_date = models.DateField("起捕日期") 
    quantity = models.DecimalField("数量(kg)", max_digits=10, decimal_places=2) 

    def __str__(self):
        return self.harvest_id

# 3. 二产：加工批次
class ProcessBatch(models.Model):
    process_id = models.CharField("加工批次号", max_length=50, unique=True)
    harvest_batch = models.ForeignKey(HarvestBatch, on_delete=models.CASCADE, verbose_name="关联收获批次")
    factory_name = models.CharField("加工厂名称", max_length=100) 
    temp_control = models.TextField("温控记录") 
    sample_id = models.CharField("留样编号", max_length=50, default="未留样")
    
    def __str__(self):
        return self.process_id

# ==========================================
# 🌟 零产：全球贸易中枢 (CRM 客户档案)
# ==========================================
class Customer(models.Model):
    customer_id = models.CharField("客户编号", max_length=50, unique=True)
    name = models.CharField("客户名称", max_length=100)
    country = models.CharField("国家/地区", max_length=50)
    contact_info = models.CharField("联系方式", max_length=100, null=True, blank=True)
    
    # 🚨 新增 GTM 核心风控字段
    credit_rating = models.CharField("信用评级", max_length=20, default="B级 (良好)") # 如：A级 (极佳)
    total_trade_volume = models.DecimalField("累计交易额($)", max_digits=15, decimal_places=2, default=0)
    default_count = models.IntegerField("历史违约次数", default=0)

    def __str__(self):
        return f"{self.name} ({self.country})"

# ==========================================
# 🌟 零产：全球贸易订单中心
# ==========================================
class SalesOrder(models.Model):
    order_id = models.CharField("订单编号", max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, verbose_name="关联采购商")
    
    order_date = models.DateField("下单日期", default=timezone.now)
    product_spec = models.CharField("需求规格", max_length=100) 
    quantity = models.IntegerField("订单数量(kg)")
    total_amount = models.DecimalField("总金额(FOB)", max_digits=12, decimal_places=2, default=0)
    
    deposit_status = models.CharField("定金状态", max_length=20, default="未收定金")
    status = models.CharField("订单状态", max_length=20, default="生产准备中") 
    financial_status = models.CharField("财务状态", max_length=20, default="待收尾款")
    
    def __str__(self):
        return f"Order: {self.order_id}"

# ==========================================
# 4. 三产：出口装柜 (打通全链路的终极桥梁)
# ==========================================
class ExportBatch(models.Model):
    export_id = models.CharField(max_length=50, unique=True, verbose_name="出口批次号")
    process_batch = models.ForeignKey(ProcessBatch, on_delete=models.CASCADE, verbose_name="关联加工批次")
    
    # 🚨 终极改动：用 ForeignKey 直接关联到 SalesOrder！
    # 这样通过 ExportBatch，就能顺藤摸瓜：订单 -> 加工 -> 收获 -> 养殖！
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="关联贸易订单")
    
    loading_date = models.DateField(verbose_name="装柜时间")
    bol_number = models.CharField(max_length=100, verbose_name="提单号")
    destination = models.CharField(max_length=100, verbose_name="目的地")
    
    # 🚨 新增：报关状态机
    customs_status = models.CharField("报关状态", max_length=20, default="草稿/待申报")
    release_status = models.CharField(max_length=20, default='待放单', verbose_name="放单状态")

    def __str__(self):
        return self.export_id

# ==========================================
# 5. 文件证据中心 & 6. 出口档案归档 (保持不变)
# ==========================================
class DocPack(models.Model):
    farm_batch = models.ForeignKey(FarmBatch, on_delete=models.CASCADE, verbose_name="关联养殖批次", null=True, blank=True)
    process_batch = models.ForeignKey(ProcessBatch, on_delete=models.CASCADE, verbose_name="关联加工批次", null=True, blank=True)
    export_lot = models.ForeignKey(ExportBatch, on_delete=models.CASCADE, verbose_name="关联出口批次", null=True, blank=True)
    file_type = models.CharField("文件类型", max_length=50, default="检测报告") 
    file = models.FileField("证据文件", upload_to='evidences/%Y/%m/', null=True) 
    version = models.CharField("版本号", max_length=10, default="V1.0") 
    status = models.CharField("文件状态", max_length=20, default="待审核") 
    upload_time = models.DateTimeField("上传时间",  default=timezone.now)
    uploader = models.CharField("上传人", max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.file_type} - {self.version}"

class ExportArchive(models.Model):
    export_lot = models.OneToOneField(ExportBatch, on_delete=models.CASCADE, related_name='final_archive')
    archive_file = models.FileField("最终单证压缩包", upload_to='final_archives/', null=True, blank=True)
    generated_at = models.DateTimeField("生成时间", auto_now_add=True)

    def __str__(self):
        return f"Archive for {self.export_lot.export_id}"
    
    # ==========================================
# 🌟 财务中心：全成本核算总账 (Financial Ledger)
# ==========================================
class FinancialLedger(models.Model):
    # 财务账本必须和某个特定订单“一对一”绑定
    order = models.OneToOneField(SalesOrder, on_delete=models.CASCADE, verbose_name="关联订单")
    
    # 核心财务指标
    revenue = models.DecimalField("总营收(FOB)", max_digits=12, decimal_places=2, default=0)
    
    # 穿透三产的成本池
    farm_cost = models.DecimalField("一产养殖成本(饲料/动保)", max_digits=10, decimal_places=2, default=0)
    process_cost = models.DecimalField("二产加工成本(包装/冷藏)", max_digits=10, decimal_places=2, default=0)
    export_cost = models.DecimalField("三产出海成本(报关/海运)", max_digits=10, decimal_places=2, default=0)
    
    net_profit = models.DecimalField("净利润", max_digits=12, decimal_places=2, default=0)
    status = models.CharField("核算状态", max_length=20, default="待核算") # 待核算 / 已平账

    def __str__(self):
        return f"Ledger for {self.order.order_id}"

# ==========================================
# 🌟 独立单证中心 (Document Management)
# ==========================================
class TradeDocument(models.Model):
    DOC_TYPES = (
        ('合同', '销售合同 (Sales Contract)'),
        ('发票', '商业发票 (Commercial Invoice)'),
        ('装箱单', '装箱单 (Packing List)'),
        ('提单', '海运提单 (Bill of Lading)'),
        ('原产地证', '原产地证 (Cert of Origin)'),
    )
    
    doc_no = models.CharField("单证编号", max_length=50, unique=True)
    doc_type = models.CharField("单证类型", max_length=20, choices=DOC_TYPES)
    # 单证全部挂靠在“订单”这个绝对核心上
    order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, verbose_name="关联订单")
    status = models.CharField("单证状态", max_length=20, default="待签发") # 待签发 / 已生效 / 已归档
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    def __str__(self):
        return f"{self.doc_no} ({self.doc_type})"