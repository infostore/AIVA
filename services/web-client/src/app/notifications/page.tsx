'use client';

import { notificationService } from '@/services/api';
import Link from 'next/link';
import { useEffect, useState } from 'react';

interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'alert' | 'warning';
  isRead: boolean;
  createdAt: string;
}

interface NotificationSettings {
  emailNotifications: boolean;
  pushNotifications: boolean;
  priceAlerts: boolean;
  newsAlerts: boolean;
  reportAlerts: boolean;
  marketSummary: boolean;
}

export default function Notifications() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [settings, setSettings] = useState<NotificationSettings>({
    emailNotifications: true,
    pushNotifications: true,
    priceAlerts: true,
    newsAlerts: true,
    reportAlerts: false,
    marketSummary: true,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'all' | 'unread' | 'settings'>('all');
  const [settingsChanged, setSettingsChanged] = useState(false);

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        setLoading(true);
        const data = await notificationService.getNotifications();
        setNotifications(data);
        setError(null);
      } catch (err: any) {
        setError(err.message || '알림을 불러오는 중 오류가 발생했습니다.');
      } finally {
        setLoading(false);
      }
    };

    fetchNotifications();
  }, []);

  const handleMarkAsRead = async (id: string) => {
    try {
      await notificationService.markAsRead(id);
      setNotifications(
        notifications.map((notification) =>
          notification.id === id
            ? { ...notification, isRead: true }
            : notification
        )
      );
    } catch (err: any) {
      console.error('알림 읽음 처리 중 오류:', err);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      // 실제로는 API에서 일괄 처리 엔드포인트가 필요합니다
      const unreadNotifications = notifications.filter((n) => !n.isRead);
      await Promise.all(
        unreadNotifications.map((n) => notificationService.markAsRead(n.id))
      );
      
      setNotifications(
        notifications.map((notification) => ({
          ...notification,
          isRead: true,
        }))
      );
    } catch (err: any) {
      console.error('모든 알림 읽음 처리 중 오류:', err);
    }
  };

  const handleSettingChange = (setting: keyof NotificationSettings) => {
    setSettings((prev) => ({
      ...prev,
      [setting]: !prev[setting],
    }));
    setSettingsChanged(true);
  };

  const saveSettings = async () => {
    try {
      await notificationService.updateSettings(settings);
      setSettingsChanged(false);
      alert('알림 설정이 저장되었습니다.');
    } catch (err: any) {
      console.error('알림 설정 저장 중 오류:', err);
    }
  };

  const filteredNotifications = activeTab === 'unread'
    ? notifications.filter((n) => !n.isRead)
    : notifications;

  return (
    <main className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <Link href="/" className="text-blue-600 hover:underline">
          ← 대시보드로 돌아가기
        </Link>
      </div>

      <h1 className="text-3xl font-bold mb-6">알림 관리</h1>

      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('all')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'all'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              모든 알림
            </button>
            <button
              onClick={() => setActiveTab('unread')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'unread'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              읽지 않은 알림
            </button>
            <button
              onClick={() => setActiveTab('settings')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'settings'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              알림 설정
            </button>
          </nav>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : error ? (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p>{error}</p>
        </div>
      ) : activeTab === 'settings' ? (
        <div className="card">
          <h2 className="text-xl font-semibold mb-6">알림 설정</h2>
          
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium">이메일 알림</h3>
                <p className="text-sm text-gray-500">중요 알림을 이메일로 받습니다.</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  className="sr-only peer"
                  checked={settings.emailNotifications}
                  onChange={() => handleSettingChange('emailNotifications')}
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium">푸시 알림</h3>
                <p className="text-sm text-gray-500">브라우저 푸시 알림을 받습니다.</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  className="sr-only peer"
                  checked={settings.pushNotifications}
                  onChange={() => handleSettingChange('pushNotifications')}
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium">가격 알림</h3>
                <p className="text-sm text-gray-500">주식 가격 변동 알림을 받습니다.</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  className="sr-only peer"
                  checked={settings.priceAlerts}
                  onChange={() => handleSettingChange('priceAlerts')}
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium">뉴스 알림</h3>
                <p className="text-sm text-gray-500">관심 종목 관련 뉴스 알림을 받습니다.</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  className="sr-only peer"
                  checked={settings.newsAlerts}
                  onChange={() => handleSettingChange('newsAlerts')}
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium">리포트 알림</h3>
                <p className="text-sm text-gray-500">분석 리포트 발행 알림을 받습니다.</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  className="sr-only peer"
                  checked={settings.reportAlerts}
                  onChange={() => handleSettingChange('reportAlerts')}
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium">시장 요약</h3>
                <p className="text-sm text-gray-500">일일 시장 요약 알림을 받습니다.</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  className="sr-only peer"
                  checked={settings.marketSummary}
                  onChange={() => handleSettingChange('marketSummary')}
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
            
            <div className="pt-4 border-t border-gray-200">
              <button
                onClick={saveSettings}
                disabled={!settingsChanged}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-blue-300"
              >
                설정 저장
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div>
          {filteredNotifications.length > 0 ? (
            <div className="space-y-4">
              <div className="flex justify-between items-center mb-4">
                <p className="text-sm text-gray-500">
                  총 {filteredNotifications.length}개의 알림이 있습니다.
                </p>
                <button
                  onClick={handleMarkAllAsRead}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  모두 읽음으로 표시
                </button>
              </div>

              {filteredNotifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`card border-l-4 ${
                    notification.type === 'alert'
                      ? 'border-l-red-500'
                      : notification.type === 'warning'
                      ? 'border-l-yellow-500'
                      : 'border-l-blue-500'
                  } ${!notification.isRead ? 'bg-blue-50' : ''}`}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-semibold text-lg">{notification.title}</h3>
                      <p className="text-gray-600 mt-1">{notification.message}</p>
                      <p className="text-xs text-gray-500 mt-2">
                        {new Date(notification.createdAt).toLocaleString('ko-KR')}
                      </p>
                    </div>
                    {!notification.isRead && (
                      <button
                        onClick={() => handleMarkAsRead(notification.id)}
                        className="text-sm text-blue-600 hover:text-blue-800"
                      >
                        읽음으로 표시
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
                />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">알림이 없습니다</h3>
              <p className="mt-1 text-sm text-gray-500">
                {activeTab === 'unread'
                  ? '모든 알림을 확인했습니다.'
                  : '아직 알림이 없습니다.'}
              </p>
            </div>
          )}
        </div>
      )}
    </main>
  );
} 