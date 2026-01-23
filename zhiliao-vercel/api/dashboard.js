// Vercel Serverless Function - 飞书多维表格数据接口
// 部署后访问: https://你的域名.vercel.app/api/dashboard

export default async function handler(req, res) {
  // CORS设置
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // 飞书配置
  const CONFIG = {
    appId: process.env.FEISHU_APP_ID || 'cli_a9f85a3bc2f85bd9',
    appSecret: process.env.FEISHU_APP_SECRET || 'LCAnNoRSHN4pOZKDIMMpXdC4YamqDcLz',
    appToken: process.env.FEISHU_APP_TOKEN || 'CTGAbIKYYap81Msk8iVc5ELOn4b',
    tableId: process.env.FEISHU_TABLE_ID || 'tblGN0MqO6YtoaqT',
  };

  try {
    // 1. 获取Token
    const tokenRes = await fetch('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ app_id: CONFIG.appId, app_secret: CONFIG.appSecret }),
    });
    const tokenData = await tokenRes.json();
    
    if (tokenData.code !== 0) {
      return res.status(401).json({ success: false, error: `Token获取失败: ${tokenData.msg}` });
    }
    const token = tokenData.tenant_access_token;

    // 2. 获取所有记录
    let allRecords = [];
    let pageToken = null;

    do {
      const url = new URL(`https://open.feishu.cn/open-apis/bitable/v1/apps/${CONFIG.appToken}/tables/${CONFIG.tableId}/records`);
      url.searchParams.set('page_size', '500');
      if (pageToken) url.searchParams.set('page_token', pageToken);

      const recordsRes = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const recordsData = await recordsRes.json();

      if (recordsData.code !== 0) {
        return res.status(400).json({ success: false, error: `获取记录失败: ${recordsData.msg}` });
      }

      allRecords = allRecords.concat(recordsData.data.items || []);
      pageToken = recordsData.data.has_more ? recordsData.data.page_token : null;
    } while (pageToken);

    // 3. 处理数据
    const result = processRecords(allRecords);
    result.meta = {
      totalRecords: allRecords.length,
      generatedAt: new Date().toISOString(),
    };

    return res.status(200).json({ success: true, data: result });

  } catch (error) {
    return res.status(500).json({ success: false, error: error.message });
  }
}

// 解析飞书字段值
function parseValue(val) {
  if (val === null || val === undefined) return null;
  if (Array.isArray(val)) return val.map(v => v.text || v.name || v).join(', ');
  if (typeof val === 'object') return val.text || val.name || val.value || String(val);
  return val;
}

// 处理记录
function processRecords(records) {
  if (records.length === 0) return { dailyData: [], productData: [], fields: [] };

  const fields = Object.keys(records[0].fields);

  // 智能匹配字段
  const find = (keys) => fields.find(f => keys.some(k => f.toLowerCase().includes(k.toLowerCase())));
  const dateField = find(['日期', 'date', '时间', 'time']);
  const orderField = find(['单号', '订单', 'order']);
  const skuField = find(['商品id', 'sku', '编码', '货号']);
  const nameField = find(['商品名', '品名', 'name', '名称']);
  const priceField = find(['单价', 'price', '售价']);
  const qtyField = find(['数量', 'qty', '件数']);
  const amountField = find(['金额', 'amount', '销售额', '合计']);

  // 转换记录
  const processed = records.map(r => {
    const f = r.fields;
    let date = parseValue(f[dateField]);
    if (typeof date === 'number') date = new Date(date).toISOString().split('T')[0];
    else if (typeof date === 'string') {
      const m = date.match(/\d{4}-\d{2}-\d{2}/);
      date = m ? m[0] : date.split(' ')[0];
    }
    return {
      date,
      orderId: parseValue(f[orderField]) || r.record_id,
      sku: parseValue(f[skuField]),
      name: parseValue(f[nameField]),
      price: parseFloat(parseValue(f[priceField])) || 0,
      qty: parseInt(parseValue(f[qtyField])) || 1,
      amount: parseFloat(parseValue(f[amountField])) || 0,
    };
  }).filter(r => r.date);

  // 按日期聚合
  const dateMap = new Map();
  processed.forEach(r => {
    if (!dateMap.has(r.date)) {
      dateMap.set(r.date, { date: r.date, sales: 0, orders: new Set(), qty: 0, items: 0 });
    }
    const d = dateMap.get(r.date);
    d.sales += r.amount;
    d.orders.add(r.orderId);
    d.qty += r.qty;
    d.items += 1;
  });

  const dailyData = Array.from(dateMap.values())
    .map(d => ({
      date: d.date,
      sales: Math.round(d.sales * 100) / 100,
      orders: d.orders.size,
      qty: d.qty,
      items: d.items,
      avgOrder: d.orders.size > 0 ? Math.round(d.sales / d.orders.size * 100) / 100 : 0,
    }))
    .sort((a, b) => a.date.localeCompare(b.date));

  // 按商品聚合
  const productMap = new Map();
  processed.forEach(r => {
    const key = r.sku || r.name;
    if (!key) return;
    if (!productMap.has(key)) {
      productMap.set(key, { sku: r.sku, name: r.name, sales: 0, qty: 0, orders: new Set() });
    }
    const p = productMap.get(key);
    p.sales += r.amount;
    p.qty += r.qty;
    p.orders.add(r.orderId);
  });

  const productData = Array.from(productMap.values())
    .map(p => ({
      sku: p.sku,
      name: p.name,
      sales: Math.round(p.sales * 100) / 100,
      qty: p.qty,
      orders: p.orders.size,
      price: p.qty > 0 ? Math.round(p.sales / p.qty * 100) / 100 : 0,
    }))
    .sort((a, b) => b.sales - a.sales);

  // 汇总
  const totalSales = dailyData.reduce((s, d) => s + d.sales, 0);
  const totalOrders = dailyData.reduce((s, d) => s + d.orders, 0);
  const totalQty = dailyData.reduce((s, d) => s + d.qty, 0);
  const totalItems = dailyData.reduce((s, d) => s + d.items, 0);

  return {
    summary: {
      totalSales: Math.round(totalSales * 100) / 100,
      totalOrders,
      totalQty,
      avgOrder: totalOrders > 0 ? Math.round(totalSales / totalOrders * 100) / 100 : 0,
      bindRate: totalOrders > 0 ? Math.round(totalItems / totalOrders * 100) / 100 : 0,
      skuCount: productData.length,
      days: dailyData.length,
    },
    dailyData,
    productData: productData.slice(0, 50),
    fields,
  };
}
