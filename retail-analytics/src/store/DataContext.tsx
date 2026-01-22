import React, { createContext, useContext, useState, useCallback } from 'react';
import type { SalesRecord, DateRange, FeishuConfig, FieldMapping } from '../types';
import feishuService from '../services/feishu';
import dayjs from 'dayjs';

interface DataState {
  records: SalesRecord[];
  filteredRecords: SalesRecord[];
  loading: boolean;
  error: string | null;
  isConfigured: boolean;
  dateRange: DateRange;
}

interface DataContextValue extends DataState {
  setDateRange: (range: DateRange) => void;
  initFeishu: (config: FeishuConfig, fieldMapping?: Partial<FieldMapping>) => void;
  fetchData: () => Promise<void>;
  loadDemoData: () => void;
}

const defaultDateRange: DateRange = {
  start: dayjs().subtract(30, 'day').format('YYYY-MM-DD'),
  end: dayjs().format('YYYY-MM-DD'),
};

const DataContext = createContext<DataContextValue | null>(null);

// 生成演示数据
function generateDemoData(): SalesRecord[] {
  const products = [
    { id: 'P001', name: '智能手表', category: '电子产品', price: 1299 },
    { id: 'P002', name: '无线耳机', category: '电子产品', price: 699 },
    { id: 'P003', name: '运动鞋', category: '服饰', price: 599 },
    { id: 'P004', name: '纯棉T恤', category: '服饰', price: 99 },
    { id: 'P005', name: '咖啡豆', category: '食品', price: 89 },
    { id: 'P006', name: '护肤套装', category: '美妆', price: 399 },
    { id: 'P007', name: '书籍套装', category: '图书', price: 158 },
    { id: 'P008', name: '保温杯', category: '家居', price: 168 },
    { id: 'P009', name: '瑜伽垫', category: '运动', price: 128 },
    { id: 'P010', name: '蓝牙音箱', category: '电子产品', price: 459 },
  ];

  const customers = [
    { id: 'C001', name: '张三', type: 'VIP' },
    { id: 'C002', name: '李四', type: '普通' },
    { id: 'C003', name: '王五', type: 'VIP' },
    { id: 'C004', name: '赵六', type: '普通' },
    { id: 'C005', name: '钱七', type: '新客' },
    { id: 'C006', name: '孙八', type: 'VIP' },
    { id: 'C007', name: '周九', type: '普通' },
    { id: 'C008', name: '吴十', type: '新客' },
  ];

  const regions = ['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '南京'];
  const channels = ['线上商城', '线下门店', '直播带货', '团购'];
  const payments = ['微信支付', '支付宝', '银行卡', '现金'];

  const records: SalesRecord[] = [];
  const startDate = dayjs().subtract(90, 'day');

  for (let i = 0; i < 500; i++) {
    const product = products[Math.floor(Math.random() * products.length)];
    const customer = customers[Math.floor(Math.random() * customers.length)];
    const quantity = Math.floor(Math.random() * 5) + 1;
    const orderDate = startDate.add(Math.floor(Math.random() * 90), 'day');

    records.push({
      id: `R${String(i + 1).padStart(4, '0')}`,
      orderId: `ORD${orderDate.format('YYYYMMDD')}${String(Math.floor(Math.random() * 1000)).padStart(4, '0')}`,
      orderDate: orderDate.format('YYYY-MM-DD'),
      productId: product.id,
      productName: product.name,
      category: product.category,
      quantity,
      unitPrice: product.price,
      totalAmount: product.price * quantity,
      customerId: customer.id,
      customerName: customer.name,
      customerType: customer.type,
      region: regions[Math.floor(Math.random() * regions.length)],
      salesChannel: channels[Math.floor(Math.random() * channels.length)],
      paymentMethod: payments[Math.floor(Math.random() * payments.length)],
    });
  }

  return records.sort((a, b) => a.orderDate.localeCompare(b.orderDate));
}

export function DataProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<DataState>({
    records: [],
    filteredRecords: [],
    loading: false,
    error: null,
    isConfigured: false,
    dateRange: defaultDateRange,
  });

  const filterRecordsByDate = useCallback((records: SalesRecord[], dateRange: DateRange) => {
    const start = dayjs(dateRange.start);
    const end = dayjs(dateRange.end);

    return records.filter((record) => {
      const date = dayjs(record.orderDate);
      return date.isAfter(start.subtract(1, 'day')) && date.isBefore(end.add(1, 'day'));
    });
  }, []);

  const setDateRange = useCallback((range: DateRange) => {
    setState((prev) => ({
      ...prev,
      dateRange: range,
      filteredRecords: filterRecordsByDate(prev.records, range),
    }));
  }, [filterRecordsByDate]);

  const initFeishu = useCallback((config: FeishuConfig, fieldMapping?: Partial<FieldMapping>) => {
    feishuService.init(config, fieldMapping);
    setState((prev) => ({ ...prev, isConfigured: true }));
  }, []);

  const fetchData = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const records = await feishuService.fetchSalesData();
      setState((prev) => ({
        ...prev,
        records,
        filteredRecords: filterRecordsByDate(records, prev.dateRange),
        loading: false,
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : '获取数据失败',
      }));
    }
  }, [filterRecordsByDate]);

  const loadDemoData = useCallback(() => {
    const records = generateDemoData();
    setState((prev) => ({
      ...prev,
      records,
      filteredRecords: filterRecordsByDate(records, prev.dateRange),
      isConfigured: true,
    }));
  }, [filterRecordsByDate]);

  const value: DataContextValue = {
    ...state,
    setDateRange,
    initFeishu,
    fetchData,
    loadDemoData,
  };

  return <DataContext.Provider value={value}>{children}</DataContext.Provider>;
}

export function useData() {
  const context = useContext(DataContext);
  if (!context) {
    throw new Error('useData must be used within a DataProvider');
  }
  return context;
}
