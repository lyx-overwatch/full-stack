'use client';
import { post } from '@/network';
import { toast } from 'sonner';
import { useRouter } from 'next/navigation';
import React, { useMemo, useState } from 'react';

const ChatPage: React.FC = () => {
  const router = useRouter();
  const [messages, setMessages] = useState<string[]>([]);
  const [input, setInput] = useState<string>('');
  const [token] = useState(() => {
    if (typeof window === 'undefined') {
      return '';
    }
    return localStorage.getItem('token') || '';
  });

  const userProfile = useMemo(() => {
    if (!token) {
      return {
        name: '未登录用户',
        email: '暂无用户信息',
      };
    }

    try {
      const profileStr = localStorage.getItem('profile') || '';
      const parsed = JSON.parse(profileStr) as {
        name?: string;
        email?: string;
      };

      const email = parsed.email || '暂无邮箱信息';
      const name = parsed.name || email;

      return {
        name,
        email,
      };
    } catch {
      return {
        name: '已登录用户',
        email: '无法解析用户信息',
      };
    }
  }, [token]);

  const avatarText = useMemo(() => {
    const source = userProfile.name || userProfile.email;
    const first = source.trim().charAt(0);
    return first ? first.toUpperCase() : 'U';
  }, [userProfile]);

  const handleSendMessage = async () => {
    if (input.trim() === '') return;
    setMessages([...messages, input]);
    setInput('');
    await post('/chat', { message: input });
    // setMessages((prev) => [...prev, data.reply]);
  };

  const handleLogout = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      toast.error('您尚未登录');
      router.push('/');
      return;
    }
    const resp = await post<{ msg: string; code: number }>('/logout', {});
    if (resp.code === 200) {
      localStorage.removeItem('token');
      localStorage.removeItem('profile');
      toast.success(resp.msg || '退出登录成功');
      router.push('/');
    }
  };

  return (
    <div className='flex flex-col h-screen pb-16'>
      <div className='flex justify-end p-4 border-b'>
        <details className='relative'>
          <summary className='flex h-10 w-10 cursor-pointer list-none items-center justify-center rounded-full border bg-muted text-sm font-semibold text-foreground hover:bg-muted/80'>
            {avatarText}
          </summary>
          <div className='absolute right-0 z-20 mt-2 w-64 rounded-lg border bg-background p-3 shadow-md'>
            <p className='text-sm font-medium text-foreground'>
              {userProfile.name}
            </p>
            <p className='mt-1 text-xs text-muted-foreground'>
              {userProfile.email}
            </p>
            <button
              type='button'
              className='mt-3 w-full rounded-md border px-3 py-2 text-sm hover:bg-muted'
              onClick={handleLogout}
            >
              退出登录
            </button>
          </div>
        </details>
      </div>
      <div className='flex-1 p-4 overflow-y-auto'>
        {messages.map((msg, index) => (
          <div key={index} className='mb-2'>
            {msg}
          </div>
        ))}
      </div>
      <div className='p-4 border-t'>
        <input
          type='text'
          placeholder='Type your message...'
          className='w-full p-2 border rounded'
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              handleSendMessage();
            }
          }}
        />
      </div>
    </div>
  );
};

export default ChatPage;
