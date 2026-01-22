import dayjs from 'dayjs';
import type {
  SalesRecord,
  SalesTrend,
  ProductRanking,
  CustomerAnalysis,
  CategoryAnalysis,
  RegionAnalysis,
  DashboardSummary,
  DateRange,
} from '../types';

// 按日期过滤数据
export function filterByDateRange(
  records: SalesRecord[],
  dateRange: DateRange
): SalesRecord[] {
  const start = dayjs(dateRange.start);
  const end = dayjs(dateRange.end);

  return records.filter((record) => {
    const date = dayjs(record.orderDate);
    return date.isAfter(start.subtract(1, 'day')) && date.isBefore(end.add(1, 'day'));
  });
}

// 计算销售趋势
export function calculateSalesTrend(
  records: SalesRecord[],
  groupBy: 'day' | 'week' | 'month' = 'day'
): SalesTrend[] {
  const grouped = new Map<string, SalesRecord[]>();

  records.forEach((record) => {
    let key: string;
    const date = dayjs(record.orderDate);

    switch (groupBy) {
      case 'week':
        key = date.startOf('week').format('YYYY-MM-DD');
        break;
      case 'month':
        key = date.format('YYYY-MM');
        break;
      default:
        key = date.format('YYYY-MM-DD');
    }

    if (!grouped.has(key)) {
      grouped.set(key, []);
    }
    grouped.get(key)!.push(record);
  });

  const trends: SalesTrend[] = [];

  grouped.forEach((items, date) => {
    const totalSales = items.reduce((sum, r) => sum + r.totalAmount, 0);
    const orderCount = new Set(items.map((r) => r.orderId)).size;

    trends.push({
      date,
      totalSales,
      orderCount,
      avgOrderValue: orderCount > 0 ? totalSales / orderCount : 0,
    });
  });

  return trends.sort((a, b) => a.date.localeCompare(b.date));
}

// 计算商品排行
export function calculateProductRanking(
  records: SalesRecord[],
  sortBy: 'sales' | 'quantity' = 'sales',
  limit: number = 10
): ProductRanking[] {
  const productMap = new Map<string, ProductRanking>();

  records.forEach((record) => {
    const key = record.productId;
    if (!productMap.has(key)) {
      productMap.set(key, {
        productId: record.productId,
        productName: record.productName,
        category: record.category,
        totalQuantity: 0,
        totalSales: 0,
        orderCount: 0,
      });
    }

    const product = productMap.get(key)!;
    product.totalQuantity += record.quantity;
    product.totalSales += record.totalAmount;
    product.orderCount += 1;
  });

  const rankings = Array.from(productMap.values());

  rankings.sort((a, b) => {
    if (sortBy === 'sales') {
      return b.totalSales - a.totalSales;
    }
    return b.totalQuantity - a.totalQuantity;
  });

  return rankings.slice(0, limit);
}

// 计算客户分析
export function calculateCustomerAnalysis(
  records: SalesRecord[]
): CustomerAnalysis[] {
  const customerMap = new Map<string, {
    orders: Set<string>;
    records: SalesRecord[];
  }>();

  records.forEach((record) => {
    const key = record.customerId;
    if (!customerMap.has(key)) {
      customerMap.set(key, {
        orders: new Set(),
        records: [],
      });
    }

    const customer = customerMap.get(key)!;
    customer.orders.add(record.orderId);
    customer.records.push(record);
  });

  const analyses: CustomerAnalysis[] = [];

  customerMap.forEach((data, customerId) => {
    const { orders, records: customerRecords } = data;
    const totalOrders = orders.size;
    const totalSpent = customerRecords.reduce((sum, r) => sum + r.totalAmount, 0);

    // 计算购买频次（每月订单数）
    const sortedDates = customerRecords
      .map((r) => r.orderDate)
      .sort();
    const minDate = sortedDates[0] ? dayjs(sortedDates[0]) : null;
    const maxDate = sortedDates[sortedDates.length - 1] ? dayjs(sortedDates[sortedDates.length - 1]) : null;
    const monthsDiff = (minDate && maxDate) ? Math.max(maxDate.diff(minDate, 'month'), 1) : 1;
    const purchaseFrequency = totalOrders / monthsDiff;

    // 最近订单日期
    const lastOrderDate = customerRecords
      .map((r) => r.orderDate)
      .sort()
      .pop() || '';

    analyses.push({
      customerId,
      customerName: customerRecords[0]?.customerName || '',
      customerType: customerRecords[0]?.customerType || '',
      totalOrders,
      totalSpent,
      avgOrderValue: totalOrders > 0 ? totalSpent / totalOrders : 0,
      lastOrderDate,
      purchaseFrequency,
    });
  });

  return analyses.sort((a, b) => b.totalSpent - a.totalSpent);
}

// 计算分类分析
export function calculateCategoryAnalysis(
  records: SalesRecord[]
): CategoryAnalysis[] {
  const categoryMap = new Map<string, {
    totalSales: number;
    totalQuantity: number;
    orderCount: number;
  }>();

  let grandTotalSales = 0;

  records.forEach((record) => {
    const key = record.category || '未分类';
    if (!categoryMap.has(key)) {
      categoryMap.set(key, {
        totalSales: 0,
        totalQuantity: 0,
        orderCount: 0,
      });
    }

    const category = categoryMap.get(key)!;
    category.totalSales += record.totalAmount;
    category.totalQuantity += record.quantity;
    category.orderCount += 1;
    grandTotalSales += record.totalAmount;
  });

  const analyses: CategoryAnalysis[] = [];

  categoryMap.forEach((data, category) => {
    analyses.push({
      category,
      ...data,
      percentage: grandTotalSales > 0 ? (data.totalSales / grandTotalSales) * 100 : 0,
    });
  });

  return analyses.sort((a, b) => b.totalSales - a.totalSales);
}

// 计算地区分析
export function calculateRegionAnalysis(
  records: SalesRecord[]
): RegionAnalysis[] {
  const regionMap = new Map<string, {
    totalSales: number;
    orders: Set<string>;
    customers: Set<string>;
  }>();

  records.forEach((record) => {
    const key = record.region || '未知地区';
    if (!regionMap.has(key)) {
      regionMap.set(key, {
        totalSales: 0,
        orders: new Set(),
        customers: new Set(),
      });
    }

    const region = regionMap.get(key)!;
    region.totalSales += record.totalAmount;
    region.orders.add(record.orderId);
    region.customers.add(record.customerId);
  });

  const analyses: RegionAnalysis[] = [];

  regionMap.forEach((data, region) => {
    analyses.push({
      region,
      totalSales: data.totalSales,
      orderCount: data.orders.size,
      customerCount: data.customers.size,
    });
  });

  return analyses.sort((a, b) => b.totalSales - a.totalSales);
}

// 计算仪表板摘要
export function calculateDashboardSummary(
  currentRecords: SalesRecord[],
  previousRecords?: SalesRecord[]
): DashboardSummary {
  // 当前周期数据
  const totalSales = currentRecords.reduce((sum, r) => sum + r.totalAmount, 0);
  const uniqueOrders = new Set(currentRecords.map((r) => r.orderId));
  const totalOrders = uniqueOrders.size;
  const uniqueCustomers = new Set(currentRecords.map((r) => r.customerId));
  const totalCustomers = uniqueCustomers.size;
  const avgOrderValue = totalOrders > 0 ? totalSales / totalOrders : 0;

  // 计算增长率
  let salesGrowth = 0;
  let orderGrowth = 0;
  let customerGrowth = 0;

  if (previousRecords && previousRecords.length > 0) {
    const prevTotalSales = previousRecords.reduce((sum, r) => sum + r.totalAmount, 0);
    const prevTotalOrders = new Set(previousRecords.map((r) => r.orderId)).size;
    const prevTotalCustomers = new Set(previousRecords.map((r) => r.customerId)).size;

    salesGrowth = prevTotalSales > 0 ? ((totalSales - prevTotalSales) / prevTotalSales) * 100 : 0;
    orderGrowth = prevTotalOrders > 0 ? ((totalOrders - prevTotalOrders) / prevTotalOrders) * 100 : 0;
    customerGrowth = prevTotalCustomers > 0 ? ((totalCustomers - prevTotalCustomers) / prevTotalCustomers) * 100 : 0;
  }

  return {
    totalSales,
    totalOrders,
    totalCustomers,
    avgOrderValue,
    salesGrowth,
    orderGrowth,
    customerGrowth,
  };
}

// 格式化金额
export function formatCurrency(value: number, currency: string = '¥'): string {
  return `${currency}${value.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

// 格式化百分比
export function formatPercentage(value: number): string {
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(2)}%`;
}

// 格式化数字
export function formatNumber(value: number): string {
  return value.toLocaleString('zh-CN');
}
