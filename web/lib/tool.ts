export const RSAEncrypt = async (password: string): Promise<string> => {
  const JSEncrypt = (await import('jsencrypt')).default;
  const jsencrypt = new JSEncrypt();
  if (!process.env.NEXT_PUBLIC_RSA_PUBLIC_KEY) {
    return Promise.reject(
      new Error('RSA_PUBLIC_KEY is not defined in environment variables')
    );
  }
  jsencrypt.setKey(process.env.NEXT_PUBLIC_RSA_PUBLIC_KEY);
  return jsencrypt.encrypt(password) || '';
};
