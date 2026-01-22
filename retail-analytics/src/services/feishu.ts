import axios from 'axios';
import type {
  FeishuConfig,
  FeishuTokenResponse,
  FeishuRecordsResponse,
  FeishuRecord,
  SalesRecord,
  FieldMapping
} from '../types';

// 飞书API基础配置
const FEISHU_BASE_URL = import.meta.env.DEV
  ? '/api/feishu'
  : 'https://open.feishu.cn';

// 默认字段映射（根据你的多维表格字段名调整）
const DEFAULT_FIELD_MAPPING: FieldMapping = {
  orderId: '订单号',
  orderDate: '订单日期',
  productId: '商品ID',
  productName: '商品名称',
  category: '商品分类',
  quantity: '数量',
  unitPrice: '单价',
  totalAmount: '总金额',
  customerId: '客户ID',
  customerName: '客户名称',
  customerType: '客户类型',
  region: '地区',
  salesChannel: '销售渠道',
  paymentMethod: '支付方式',
};

class FeishuService {
  private config: FeishuConfig | null = null;
  private accessToken: string | null = null;
  private tokenExpireTime: number = 0;
  private fieldMapping: FieldMapping = DEFAULT_FIELD_MAPPING;

  // 初始化配置
  init(config: FeishuConfig, fieldMapping?: Partial<FieldMapping>) {
    this.config = config;
    if (fieldMapping) {
      this.fieldMapping = { ...DEFAULT_FIELD_MAPPING, ...fieldMapping };
    }
  }

  // 设置字段映射
  setFieldMapping(mapping: Partial<FieldMapping>) {
    this.fieldMapping = { ...this.fieldMapping, ...mapping };
  }

  // 获取tenant_access_token
  async getTenantAccessToken(): Promise<string> {
    if (!this.config) {
      throw new Error('飞书配置未初始化，请先调用 init() 方法');
    }

    // 检查token是否过期
    if (this.accessToken && Date.now() < this.tokenExpireTime - 60000) {
      return this.accessToken;
    }

    try {
      const response = await axios.post<FeishuTokenResponse>(
        `${FEISHU_BASE_URL}/open-apis/auth/v3/tenant_access_token/internal`,
        {
          app_id: this.config.appId,
          app_secret: this.config.appSecret,
        },
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (response.data.code !== 0) {
        throw new Error(`获取access_token失败: ${response.data.msg}`);
      }

      this.accessToken = response.data.tenant_access_token;
      this.tokenExpireTime = Date.now() + response.data.expire * 1000;

      return this.accessToken;
    } catch (error) {
      console.error('获取飞书access_token失败:', error);
      throw error;
    }
  }

  // 获取多维表格记录
  async getRecords(
    pageToken?: string,
    pageSize: number = 500
  ): Promise<FeishuRecordsResponse> {
    if (!this.config) {
      throw new Error('飞书配置未初始化');
    }

    const token = await this.getTenantAccessToken();

    const params: Record<string, unknown> = {
      page_size: pageSize,
    };

    if (pageToken) {
      params.page_token = pageToken;
    }

    try {
      const response = await axios.get<FeishuRecordsResponse>(
        `${FEISHU_BASE_URL}/open-apis/bitable/v1/apps/${this.config.appToken}/tables/${this.config.tableId}/records`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          params,
        }
      );

      if (response.data.code !== 0) {
        throw new Error(`获取记录失败: ${response.data.msg}`);
      }

      return response.data;
    } catch (error) {
      console.error('获取飞书多维表格记录失败:', error);
      throw error;
    }
  }

  // 获取所有记录（自动分页）
  async getAllRecords(): Promise<FeishuRecord[]> {
    const allRecords: FeishuRecord[] = [];
    let pageToken: string | undefined;
    let hasMore = true;

    while (hasMore) {
      const response = await this.getRecords(pageToken);
      allRecords.push(...response.data.items);
      hasMore = response.data.has_more;
      pageToken = response.data.page_token;
    }

    return allRecords;
  }

  // 将飞书记录转换为销售记录
  transformToSalesRecords(records: FeishuRecord[]): SalesRecord[] {
    return records.map((record) => {
      const fields = record.fields;
      const mapping = this.fieldMapping;

      // 处理日期字段（飞书多维表格日期格式可能是时间戳或字符串）
      let orderDate = '';
      const dateValue = fields[mapping.orderDate];
      if (typeof dateValue === 'number') {
        orderDate = new Date(dateValue).toISOString().split('T')[0];
      } else if (typeof dateValue === 'string') {
        orderDate = dateValue;
      }

      // 处理文本字段（可能是数组格式）
      const getText = (value: unknown): string => {
        if (Array.isArray(value)) {
          return value.map(v => v?.text || v).join('');
        }
        return String(value || '');
      };

      // 处理数字字段
      const getNumber = (value: unknown): number => {
        if (typeof value === 'number') return value;
        if (typeof value === 'string') return parseFloat(value) || 0;
        return 0;
      };

      return {
        id: record.record_id,
        orderId: getText(fields[mapping.orderId]),
        orderDate,
        productId: getText(fields[mapping.productId]),
        productName: getText(fields[mapping.productName]),
        category: getText(fields[mapping.category]),
        quantity: getNumber(fields[mapping.quantity]),
        unitPrice: getNumber(fields[mapping.unitPrice]),
        totalAmount: getNumber(fields[mapping.totalAmount]),
        customerId: getText(fields[mapping.customerId]),
        customerName: getText(fields[mapping.customerName]),
        customerType: getText(fields[mapping.customerType]),
        region: getText(fields[mapping.region]),
        salesChannel: getText(fields[mapping.salesChannel]),
        paymentMethod: getText(fields[mapping.paymentMethod]),
      };
    });
  }

  // 获取并转换所有销售记录
  async fetchSalesData(): Promise<SalesRecord[]> {
    const records = await this.getAllRecords();
    return this.transformToSalesRecords(records);
  }
}

// 导出单例
export const feishuService = new FeishuService();
export default feishuService;
