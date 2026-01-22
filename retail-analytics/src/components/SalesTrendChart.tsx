import { useMemo, useState } from 'react';
import { Card, Radio, Empty } from 'antd';
import ReactECharts from 'echarts-for-react';
import { useData } from '../store/DataContext';
import { calculateSalesTrend } from '../utils/analytics';

type GroupBy = 'day' | 'week' | 'month';

export default function SalesTrendChart() {
  const { filteredRecords } = useData();
  const [groupBy, setGroupBy] = useState<GroupBy>('day');

  const trendData = useMemo(() => {
    return calculateSalesTrend(filteredRecords, groupBy);
  }, [filteredRecords, groupBy]);

  const option = useMemo(() => {
    return {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross',
        },
        formatter: (params: unknown[]) => {
          const p = params as { axisValue: string; seriesName: string; value: number; color: string }[];
          let result = `<div style="font-weight:600">${p[0]?.axisValue}</div>`;
          p.forEach((item) => {
            const value = item.seriesName === '销售额'
              ? `¥${item.value.toLocaleString()}`
              : item.value.toLocaleString();
            result += `<div style="display:flex;justify-content:space-between;gap:16px">
              <span style="color:${item.color}">${item.seriesName}</span>
              <span style="font-weight:600">${value}</span>
            </div>`;
          });
          return result;
        },
      },
      legend: {
        data: ['销售额', '订单数'],
        bottom: 0,
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '12%',
        top: '10%',
        containLabel: true,
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: trendData.map((d) => d.date),
        axisLabel: {
          rotate: groupBy === 'day' && trendData.length > 15 ? 45 : 0,
        },
      },
      yAxis: [
        {
          type: 'value',
          name: '销售额',
          position: 'left',
          axisLabel: {
            formatter: (value: number) => {
              if (value >= 10000) {
                return `${(value / 10000).toFixed(1)}万`;
              }
              return value.toString();
            },
          },
        },
        {
          type: 'value',
          name: '订单数',
          position: 'right',
          splitLine: {
            show: false,
          },
        },
      ],
      series: [
        {
          name: '销售额',
          type: 'line',
          smooth: true,
          yAxisIndex: 0,
          data: trendData.map((d) => d.totalSales),
          areaStyle: {
            opacity: 0.3,
          },
          lineStyle: {
            width: 2,
          },
          itemStyle: {
            color: '#1890ff',
          },
        },
        {
          name: '订单数',
          type: 'bar',
          yAxisIndex: 1,
          data: trendData.map((d) => d.orderCount),
          itemStyle: {
            color: '#91d5ff',
            borderRadius: [4, 4, 0, 0],
          },
          barMaxWidth: 30,
        },
      ],
    };
  }, [trendData, groupBy]);

  return (
    <Card
      title="销售趋势"
      extra={
        <Radio.Group
          value={groupBy}
          onChange={(e) => setGroupBy(e.target.value)}
          size="small"
        >
          <Radio.Button value="day">按天</Radio.Button>
          <Radio.Button value="week">按周</Radio.Button>
          <Radio.Button value="month">按月</Radio.Button>
        </Radio.Group>
      }
      style={{ borderRadius: 8 }}
    >
      {trendData.length > 0 ? (
        <ReactECharts option={option} style={{ height: 350 }} />
      ) : (
        <Empty description="暂无数据" style={{ height: 350, display: 'flex', flexDirection: 'column', justifyContent: 'center' }} />
      )}
    </Card>
  );
}
