from rest_framework import serializers
from .models import Customer, SalesOrder

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__' # 把客户的所有字段全部暴露给前端

class SalesOrderSerializer(serializers.ModelSerializer):
    # 🚨 架构师的小魔法：嵌套序列化
    # 这样前端不仅能拿到 customer 的 ID，还能直接拿到该客户的全部详细信息（比如信用评级），省去前端二次请求！
    customer_detail = CustomerSerializer(source='customer', read_only=True)

    class Meta:
        model = SalesOrder
        fields = '__all__'

from .models import ExportBatch

class ExportBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExportBatch
        fields = '__all__'

from .models import FinancialLedger

class FinancialLedgerSerializer(serializers.ModelSerializer):
    # 外挂魔法：让前端直接看到订单号和客户名，不用再去查订单表
    order_id = serializers.CharField(source='order.order_id', read_only=True)
    customer_name = serializers.CharField(source='order.customer.name', read_only=True)
    
    class Meta:
        model = FinancialLedger
        fields = '__all__'

from .models import TradeDocument
class TradeDocumentSerializer(serializers.ModelSerializer):
    order_id_display = serializers.CharField(source='order.order_id', read_only=True)
    order_financial_status = serializers.CharField(source='order.financial_status', read_only=True)
    class Meta:
        model = TradeDocument
        fields = '__all__'