'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useTheme } from 'next-themes';
import { Moon, Sun } from 'lucide-react';
import { post } from '@/network';
import { toast } from 'sonner';
import { RSAEncrypt } from '@/lib/tool';

export default function Home() {
  const { setTheme, theme } = useTheme();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleRegister = async () => {
    setLoading(true);
    setMessage('');
    try {
      const encryptedPassword = await RSAEncrypt(password);
      const resp = await post<{ msg: string }>('/register', {
        email,
        password: encryptedPassword,
      });
      toast.success(resp.msg || 'Registration successful!');
    } catch (error) {
      console.log('Registration error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async () => {
    setLoading(true);
    setMessage('');
    try {
      const encryptedPassword = await RSAEncrypt(password);
      const resp = await post<{ data: { access_token: string }; msg: string }>(
        '/login',
        {
          email,
          password: encryptedPassword,
        }
      );
      toast.success(resp.msg || 'Login successful!');
      localStorage.setItem('token', resp.data.access_token);
    } catch (error) {
      console.log('Login error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className='flex min-h-screen items-center justify-center bg-background p-4'>
      <div className='absolute top-4 right-4'>
        <Button
          variant='ghost'
          size='icon'
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
        >
          <Sun className='h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0' />
          <Moon className='absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100' />
          <span className='sr-only'>Toggle theme</span>
        </Button>
      </div>
      <Tabs defaultValue='login' className='w-[500px]'>
        <TabsList className='grid w-full grid-cols-2'>
          <TabsTrigger value='login'>Login</TabsTrigger>
          <TabsTrigger value='register'>Register</TabsTrigger>
        </TabsList>
        <TabsContent value='login'>
          <Card>
            <CardHeader>
              <CardTitle>Login</CardTitle>
              <CardDescription>
                Enter your email below to login to your account.
              </CardDescription>
            </CardHeader>
            <CardContent className='space-y-2'>
              <div className='space-y-1'>
                <Label htmlFor='email'>Email</Label>
                <Input
                  id='email'
                  type='email'
                  placeholder='m@example.com'
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              <div className='space-y-1'>
                <Label htmlFor='password'>Password</Label>
                <Input
                  id='password'
                  type='password'
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </CardContent>
            <CardFooter className='flex flex-col items-start gap-2'>
              <Button
                className='w-full'
                onClick={handleLogin}
                disabled={loading}
              >
                {loading ? 'Logging in...' : 'Login'}
              </Button>
              {message && (
                <p className='text-sm text-red-500 dark:text-red-400'>
                  {message}
                </p>
              )}
            </CardFooter>
          </Card>
        </TabsContent>
        <TabsContent value='register'>
          <Card>
            <CardHeader>
              <CardTitle>Register</CardTitle>
              <CardDescription>
                Create a new account here. Click register when you're done.
              </CardDescription>
            </CardHeader>
            <CardContent className='space-y-2'>
              <div className='space-y-1'>
                <Label htmlFor='register-email'>Email</Label>
                <Input
                  id='register-email'
                  type='email'
                  placeholder='m@example.com'
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              <div className='space-y-1'>
                <Label htmlFor='register-password'>Password</Label>
                <Input
                  id='register-password'
                  type='password'
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </CardContent>
            <CardFooter className='flex flex-col items-start gap-2'>
              <Button
                className='w-full'
                onClick={handleRegister}
                disabled={loading}
              >
                {loading ? 'Registering...' : 'Register'}
              </Button>
              {message && (
                <p className='text-sm text-red-500 dark:text-red-400'>
                  {message}
                </p>
              )}
            </CardFooter>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
