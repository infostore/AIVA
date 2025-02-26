'use client';

import { Chart, registerables } from 'chart.js';
import 'chartjs-adapter-date-fns';
import { ko } from 'date-fns/locale';
import { useEffect, useRef } from 'react';

// Chart.js 등록
Chart.register(...registerables);

interface StockChartProps {
  data: {
    date: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }[];
  period?: '1d' | '1w' | '1m' | '3m' | '6m' | '1y' | 'all';
  height?: number;
}

const StockChart = ({ data, period = '1m', height = 400 }: StockChartProps) => {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);

  useEffect(() => {
    if (!chartRef.current || !data || data.length === 0) return;

    // 이전 차트 인스턴스 제거
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    const ctx = chartRef.current.getContext('2d');
    if (!ctx) return;

    // 데이터 준비
    const chartData = data.map(item => ({
      x: new Date(item.date),
      y: item.close,
    }));

    // 볼륨 데이터
    const volumeData = data.map(item => ({
      x: new Date(item.date),
      y: item.volume,
    }));

    // 차트 생성
    chartInstance.current = new Chart(ctx, {
      type: 'line',
      data: {
        datasets: [
          {
            label: '주가',
            data: chartData,
            borderColor: 'rgb(59, 130, 246)',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            borderWidth: 2,
            pointRadius: 0,
            pointHoverRadius: 5,
            pointHoverBackgroundColor: 'rgb(59, 130, 246)',
            pointHoverBorderColor: 'white',
            pointHoverBorderWidth: 2,
            fill: true,
            tension: 0.1,
            yAxisID: 'y',
          },
          {
            label: '거래량',
            data: volumeData,
            type: 'bar',
            backgroundColor: 'rgba(156, 163, 175, 0.5)',
            borderColor: 'rgba(156, 163, 175, 0.8)',
            borderWidth: 1,
            yAxisID: 'y1',
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false,
        },
        plugins: {
          tooltip: {
            enabled: true,
            mode: 'index',
            intersect: false,
            callbacks: {
              label: function(context) {
                const label = context.dataset.label || '';
                const value = context.parsed.y;
                if (label === '주가') {
                  return `${label}: ${value.toLocaleString()} 원`;
                } else if (label === '거래량') {
                  return `${label}: ${value.toLocaleString()}`;
                }
                return `${label}: ${value}`;
              },
            },
          },
          legend: {
            display: true,
            position: 'top',
          },
        },
        scales: {
          x: {
            type: 'time',
            time: {
              unit: getPeriodUnit(period),
              displayFormats: {
                day: 'MM/dd',
                week: 'MM/dd',
                month: 'yyyy/MM',
              },
              tooltipFormat: 'yyyy년 MM월 dd일',
            },
            adapters: {
              date: {
                locale: ko,
              },
            },
            title: {
              display: true,
              text: '날짜',
            },
          },
          y: {
            type: 'linear',
            display: true,
            position: 'left',
            title: {
              display: true,
              text: '가격 (원)',
            },
            ticks: {
              callback: function(value) {
                return value.toLocaleString();
              },
            },
          },
          y1: {
            type: 'linear',
            display: true,
            position: 'right',
            title: {
              display: true,
              text: '거래량',
            },
            grid: {
              drawOnChartArea: false,
            },
            ticks: {
              callback: function(value) {
                return value.toLocaleString();
              },
            },
          },
        },
      },
    });

    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [data, period]);

  // 기간에 따른 시간 단위 설정
  const getPeriodUnit = (period: string): 'day' | 'week' | 'month' => {
    switch (period) {
      case '1d':
      case '1w':
        return 'day';
      case '1m':
      case '3m':
        return 'week';
      case '6m':
      case '1y':
      case 'all':
        return 'month';
      default:
        return 'day';
    }
  };

  return (
    <div className="w-full" style={{ height: `${height}px` }}>
      <canvas ref={chartRef} />
    </div>
  );
};

export default StockChart; 