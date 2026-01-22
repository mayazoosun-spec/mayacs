// 飞书多维表格相关类型
export interface FeishuConfig {
  appId: string;
  appSecret: string;
  appToken: string;  // 多维表格 app_token
  tableId: string;   // 数据表 table_id
}

export interface FeishuTokenResponse {
  code: number;
  msg: string;
  tenant_access_token: string;
  expire: number;
}

export interface FeishuRecord {
  record_id: string;
  fields: Record<string, unknown>;
}

export interface FeishuRecordsResponse {
  code: number;
  msg: string;
  data: {
    has_more: boolean;
    page_token?: string;
    total: number;
    items: FeishuRecord[];
  };
}

// 零售数据类型
export interface SalesRecord {
  id: string;
  orderId: string;           // 订单号
  orderDate: string;         // 订单日期
  productId: string;         // 商品ID
  productName: string;       // 商品名称
  category: string;          // 商品分类
  quantity: number;          // 数量
  unitPrice: number;         // 单价
  totalAmount: number;       // 总金额
  customerId: string;        // 客户ID
  customerName: string;      // 客户名称
  customerType: string;      // 客户类型
  region: string;            // 地区
  salesChannel: string;      // 销售渠道
  paymentMethod: string;     // 支付方式
}

// 分析数据类型
export interface SalesTrend {
  date: string;
  totalSales: number;
  orderCount: number;
  avgOrderValue: number;
}

export interface ProductRanking {
  productId: string;
  productName: string;
  category: string;
  totalQuantity: number;
  totalSales: number;
  orderCount: number;
}

export interface CustomerAnalysis {
  customerId: string;
  customerName: string;
  customerType: string;
  totalOrders: number;
  totalSpent: number;
  avgOrderValue: number;
  lastOrderDate: string;
  purchaseFrequency: number;  // 购买频次（月）
}

export interface CategoryAnalysis {
  category: string;
  totalSales: number;
  totalQuantity: number;
  orderCount: number;
  percentage: number;
}

export interface RegionAnalysis {
  region: string;
  totalSales: number;
  orderCount: number;
  customerCount: number;
}

export interface DashboardSummary {
  totalSales: number;
  totalOrders: number;
  totalCustomers: number;
  avgOrderValue: number;
  salesGrowth: number;      // 销售增长率
  orderGrowth: number;      // 订单增长率
  customerGrowth: number;   // 客户增长率
}

// 字段映射配置
export interface FieldMapping {
  orderId: string;
  orderDate: string;
  productId: string;
  productName: string;
  category: string;
  quantity: string;
  unitPrice: string;
  totalAmount: string;
  customerId: string;
  customerName: string;
  customerType: string;
  region: string;
  salesChannel: string;
  paymentMethod: string;
}

// 时间范围
export type TimeRange = '7d' | '30d' | '90d' | '365d' | 'custom';

export interface DateRange {
  start: string;
  end: string;
}
